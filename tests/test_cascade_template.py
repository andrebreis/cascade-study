import random
import unittest

from implementations.original import CascadeTemplate
from study.status import Status
from utils.key import Key
from mock import MagicMock


class TestCascadeTemplate(unittest.TestCase):

    class CascadeTemplateWrapper(CascadeTemplate):
        def __init__(self, correct_key, key, error_rate, status, seed):
            CascadeTemplate.__init__(self, correct_key, key, error_rate, status, seed)
            self.num_iterations = 3
            self.block_size = 8

        def get_iteration_blocks(self, iter_num):
            blocks = []
            if iter_num == 0:
                for i in range(0, len(self.key), self.block_size):  # create list of block indexes [[0,1,2,3],[4,5,6,7]]
                    blocks.append(list(range(i, min(i + self.block_size, len(self.key)))))
                return blocks
            return self.shuffle_blocks(self.block_size)

    def test_binary(self):
        random.seed(1337)
        obj = CascadeTemplate(Key('f'), Key('b'), 0.25, MagicMock(), 0)
        error_index = obj._binary(range(0, len(obj.key)))
        self.assertEqual(error_index, 1)

        obj = CascadeTemplate(Key('3e'), Key('3f'), 0.17, MagicMock(), 0)
        error_index = obj._binary(range(0, len(obj.key)))
        self.assertEqual(error_index, 7)

    def test_cascade(self):
        random.seed(1337)
        c_key = 'f'*8
        key = 'f1665bf7'
        obj = self.CascadeTemplateWrapper(Key(c_key), Key(key), 0.25, MagicMock(), 0)
        obj.run_algorithm()
        self.assertEqual(obj.key, obj.correct_key)
