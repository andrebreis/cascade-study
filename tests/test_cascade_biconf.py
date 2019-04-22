import random
import unittest

from unittest.mock import MagicMock

from implementations.biconf import CascadeBiconf
from implementations.template import CascadeTemplate
from utils.key import Key


class TestCascadeBiconf(unittest.TestCase):

    def test_get_iteration_blocks(self):
        algorithm = CascadeBiconf(Key('ffffff'), Key('bbbbbb'), 0.21, MagicMock(), 0, False)

        blocks = algorithm.get_iteration_blocks(0)

        self.assertEqual(blocks, [[0, 1, 2, 3],
                                  [4, 5, 6, 7],
                                  [8, 9, 10, 11],
                                  [12, 13, 14, 15],
                                  [16, 17, 18, 19],
                                  [20, 21, 22, 23]])

        random.seed(1337)
        blocks = algorithm.get_iteration_blocks(1)
        self.assertEqual(blocks,
                         [[13, 8, 2, 0, 22, 9, 7, 16, 1, 23, 3, 15], [6, 4, 14, 21, 12, 10, 5, 20, 18, 11, 17, 19]])

        blocks = algorithm.get_iteration_blocks(2)
        self.assertEqual(blocks,
                         [[3, 5, 7, 8, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23], [0, 1, 2, 4, 6, 9, 10, 11, 16, 22]])

    def test_run_algorithm(self):
        self.ra = CascadeTemplate.run_algorithm
        CascadeTemplate.run_algorithm = MagicMock()

        algorithm = CascadeBiconf(Key('ffffff'), Key('bbbbbb'), 0.21, MagicMock(), 0, False)
        algorithm.run_biconf = MagicMock()

        algorithm.run_algorithm()

        CascadeTemplate.run_algorithm.assert_called_once()
        algorithm.run_biconf.assert_called_once()

        CascadeTemplate.run_algorithm = self.ra

    def test_run_biconf(self):
        algorithm = CascadeBiconf(Key('ffffff'), Key('bbbbbb'), 0.21, MagicMock(), 0, False)
        algorithm.run_biconf()
        self.assertEqual(algorithm.key, algorithm.correct_key)
