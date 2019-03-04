import unittest
from unittest.mock import MagicMock

from study.status import Status
from utils.key import Key


class TestCascadeTemplate(unittest.TestCase):

    def test_calculate_ber(self):
        status = Status('/tmp/test', 'test', 0, 0)
        status.correct_key = Key('ffff')
        status.final_key = Key('fbfe')
        self.assertEqual(status._calculate_ber(), 2 / 16)

    def test_calculate_efficiency(self):
        status = Status('/tmp/test', 'test', 0, 0)

        status.exchanged_msg_len = MagicMock(return_value=11)
        status.correct_key = Key(('f' * 8))
        status.channel_error_rate = 0.0625

        self.assertAlmostEqual(status._calculate_efficiency(), 11 / 10.79328, delta=0.0001)

    def test_num_channel_uses(self):
        status = Status('/tmp/test', 'test', 0, 0)
        status.channel_uses = [[8, [1, 1, 1], [1], [1, 1, 1, 1]], [3, [1], [1], [1]], [5, [2, 3], [1, 1, 1]]]

        self.assertEqual(status.num_channel_uses(), 11)

    def test_exchanged_msg_len(self):
        status = Status('/tmp/test', 'test', 0, 0)
        status.channel_uses = [[8, [1, 1, 1], [1], [1, 1, 1, 1]], [3, [1], [1], [1]], [5, [2, 3], [1, 1, 1]]]

        self.assertEqual(status.exchanged_msg_len(), 35)
