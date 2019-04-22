import random
import unittest

from unittest.mock import MagicMock

from implementations.original import OriginalCascade
from utils.key import Key


class TestCascadeOriginal(unittest.TestCase):

    def test_get_iteration_blocks(self):
        algorithm = OriginalCascade(Key('ffff'), Key('bbbb'), 0.21, MagicMock(), 0, False)

        blocks = algorithm.get_iteration_blocks(0)
        self.assertEqual(blocks, [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]])

        random.seed(1337)
        blocks = algorithm.get_iteration_blocks(1)
        self.assertEqual(blocks, [[13, 7, 0, 12, 1, 8, 3, 4], [10, 6, 5, 2, 15, 14, 9, 11]])
