#include <Python.h>

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include <stdint.h>
#include <limits.h>

typedef uint_fast32_t  word;
#define WORD_BITS      (CHAR_BIT * sizeof (word))
#define INIT_NUM_ROWS 16384

typedef struct {
    int    rows;  /* Number of row vectors */
    int    cols;  /* Number of defined bits in each row */
    int    words; /* Number of words per row vector */
    int*  first_ones;
    word** row;   /* Array of pointers */
} row_matrix;



static PyObject* init(PyObject* self, PyObject* args) {
    int num_cols;

    if(!PyArg_ParseTuple(args, "i", &num_cols))
        return NULL;

    row_matrix* matrix = (row_matrix*) PyObject_Malloc(sizeof(row_matrix));

    matrix->rows = 0;
    matrix->cols = num_cols;
    matrix->words = (num_cols + WORD_BITS - 1) / WORD_BITS;

    matrix->row = (word**) PyObject_Malloc(sizeof(word*) * INIT_NUM_ROWS);

    matrix->first_ones = (int*) PyObject_Calloc(INIT_NUM_ROWS, sizeof(int));

    return PyLong_FromVoidPtr((void*)matrix);

}

int row_get(word* row, int col){
    return (row[col / WORD_BITS] & ((word) 1U << (col % WORD_BITS))) != 0;
}

int find_first_one(word* row, int num_words) {
    for(int i = 0; i < num_words; i++) {
        if(row[i] != 0) {
            for(unsigned int j = 0; j < WORD_BITS; j++) {
                if((row[i] >> j) & 1U)
                    return i*WORD_BITS+j;
            }
        }
    }
    return -1;
}

int row_equals(word* row1, word* row2, int num_cols, int num_words) {
    return memcmp(row1, row2, sizeof(word)* num_words) == 0;
}

int _is_known(row_matrix* matrix, word* row) {
    if (matrix->rows == 0)
            return 0;

    word* current_row = (word*) PyObject_Calloc(matrix->words, sizeof(word));
    for(int i = 0; i < matrix->rows; i++) {
        int first_one = matrix->first_ones[i];
        if (row_get(row, first_one) != row_get(current_row, first_one)) {
            int w = matrix->words;
            while (w-->0) 
                current_row[w] ^= matrix->row[i][w];
            if (row_equals(current_row, row, matrix->cols, matrix->words)) {
                PyObject_Free(current_row);
                PyObject_Free(row);
                return 1;
            }
        }
    }
    PyObject_Free(current_row);
    return 0;
}

int get_row_position(row_matrix* matrix, word* row, int first_one) {

    for (int i = 0; i < matrix->rows; i++) {
        int iteration_row_first_one = matrix->first_ones[i];

        if (first_one == iteration_row_first_one) {
            for (int j = first_one + 1; j < matrix->cols; j++) {
                if (row_get(row, j) < row_get(matrix->row[i], j))
                    return i;
            }
        }
        else if (first_one < iteration_row_first_one)
                return i;    
    }
    return matrix->rows;
}

word* serialize_list(PyObject* list, int parity, int num_words, int num_cols) {
    word* row = PyObject_Calloc(sizeof(word), num_words);
    for(int i = 0; i < PyList_Size(list); i++) {
        int index = PyLong_AsLong(PyList_GetItem(list, (Py_ssize_t)i));
        row[index/WORD_BITS] |= ((word)1 << (index % WORD_BITS));
    }
    row[num_words-1] |= ((word)parity << ((num_cols-1) % WORD_BITS));

    return row;
}

int _insert_row(row_matrix* matrix, word* row) {

    int first_one = find_first_one(row, matrix->words);

    if(first_one == -1) {
        PyObject_Free(row);
        return -1;
    }

    int index = get_row_position(matrix, row, first_one);

    if (index > 0 && matrix->first_ones[index-1] == first_one) {
        for(int i = 0; i < matrix->words; i++)
            row[i] ^= matrix->row[index - 1][i];
        return _insert_row(matrix, row);
    }
    if (index < matrix->rows && matrix->first_ones[index] == first_one) {
        for(int i = 0; i < matrix->words; i++)
            row[i] ^= matrix->row[index][i];
        return _insert_row(matrix, row);
    }

    memmove(&(matrix->row[index+1]), &(matrix->row[index]), sizeof(word*) * (matrix->rows-index));
    matrix->row[index] = row;
    matrix->rows += 1;
    memmove(&(matrix->first_ones[index+1]), &(matrix->first_ones[index]), sizeof(int) * (matrix->rows-index));
    matrix->first_ones[index] = first_one;

    return 0;
}

static PyObject* create_row(PyObject *self, PyObject *args) {
    PyObject* list;
    PyObject* py_handle;
    int parity;
    if(!PyArg_ParseTuple(args, "OOi", &py_handle, &list, &parity))
        return NULL;
    row_matrix* matrix = (row_matrix* ) PyLong_AsVoidPtr(py_handle);
    word* row = serialize_list(list, parity, matrix->words, matrix->cols);
    return PyLong_FromVoidPtr((void*)row);
}

static PyObject* insert_row(PyObject *self, PyObject *args) {

    PyObject* matrix_handle;
    PyObject* row_handle;
    if(!PyArg_ParseTuple(args, "OO", &matrix_handle, &row_handle))
        return NULL;

    row_matrix* matrix = (row_matrix*) PyLong_AsVoidPtr(matrix_handle);
    word* row = (word*) PyLong_AsVoidPtr(row_handle);

    _insert_row(matrix, row);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* can_be_inferred(PyObject *self, PyObject *args) {

    PyObject* matrix_handle;
    PyObject* row_handle;
    if(!PyArg_ParseTuple(args, "OO", &matrix_handle, &row_handle))
        return NULL;

    row_matrix* matrix = (row_matrix*) PyLong_AsVoidPtr(matrix_handle);
    word* row = (word*) PyLong_AsVoidPtr(row_handle);

    return PyLong_FromLong(_is_known(matrix, row));
}

static PyObject* delete(PyObject *self, PyObject *args) {
    PyObject* py_handle;
    if(!PyArg_ParseTuple(args, "O", &py_handle))
        return NULL;
    row_matrix* matrix = (row_matrix* ) PyLong_AsVoidPtr(py_handle);

    for(int i = 0; i < matrix->rows; i++)
        PyObject_Free(matrix->row[i]);

    PyObject_Free(matrix->row);
    PyObject_Free(matrix->first_ones);
    PyObject_Free(matrix);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef myMethods[] = {
        { "init", init, METH_VARARGS, "Initializes the binary matrix" },
        { "create_row", create_row, METH_VARARGS, "Creates a row from given input"},
        { "can_be_inferred", can_be_inferred, METH_VARARGS, "Checks if a row can be inferred"},
        { "insert_row", insert_row, METH_VARARGS, "Inserts the given row if cannot be inferred" },
        { "delete", delete, METH_VARARGS, "Frees the memory for the matrix"},
        { NULL, NULL, 0, NULL }
};

// Our Module Definition struct
static struct PyModuleDef inference = {
        PyModuleDef_HEAD_INIT,
        "inference",
        "inference",
        -1,
        myMethods
};

// Initializes our module using our above struct
PyMODINIT_FUNC PyInit_inference(void)
{
    return PyModule_Create(&inference);
}
