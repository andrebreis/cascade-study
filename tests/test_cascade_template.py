import random
import unittest

from bitstring import BitArray

from implementations.original import CascadeTemplate


class TestCascadeTemplate(unittest.TestCase):

    class CascadeTemplateWrapper(CascadeTemplate):
        def __init__(self, correct_party, key):
            CascadeTemplate.__init__(self, correct_party, key)
            self.num_iterations = 3
            self.block_size = 8

        def get_iteration_blocks(self, iter_num):
            blocks = []
            if iter_num == 0:
                for i in range(0, len(self.key), self.block_size):  # create list of block indexes [[0,1,2,3],[4,5,6,7]]
                    blocks.append(list(range(i, min(i + self.block_size, len(self.key)))))
                return blocks
            random.seed(1332+iter_num*121)
            return self.shuffle_blocks(self.block_size)

    def test_binary(self):
        obj = CascadeTemplate(CascadeTemplate(None, BitArray(bin='1111')), BitArray(bin='1011'))
        error_index = obj._binary(range(0, len(obj.key)))
        self.assertEqual(error_index, 1)

        obj = CascadeTemplate(CascadeTemplate(None, BitArray(bin='111110')), BitArray(bin='111111'))
        error_index = obj._binary(range(0, len(obj.key)))
        self.assertEqual(error_index, 5)

    def test_cascade(self):
        c_key = '1'*32
        key = '11110001 01100110 01011101 11110111'
        obj = self.CascadeTemplateWrapper(CascadeTemplate(None, BitArray(bin=c_key)), BitArray(bin=key))
        obj.run_algorithm()
        self.assertEqual(obj.key, obj.correct_party.key)
