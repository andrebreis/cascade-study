from math import log2

from utils.key import Key


class Status(object):

    def __init__(self, correct_key, initial_key, error_rate, seed):
        self.correct_key = Key(correct_key.hex)
        self.initial_key = Key(initial_key.hex)
        self.error_rate = error_rate
        self.seed = seed

        self.final_key = None
        self.channel_uses = []
        self.correct = True
        self.bit_error_ratio = 0
        self.efficiency = 1.0

    def start_iteration(self, channel_use):
        self.channel_uses.append([channel_use['len']])

    def start_block(self):
        self.channel_uses[-1].append([])

    def add_channel_use(self, channel_use):
        self.channel_uses[-1][-1].append(channel_use['len'])

    def _calculate_ber(self):
        num_errors = 0
        for i in range(0, len(self.final_key)):
            num_errors += int(self.final_key.bin[i]) ^ int(self.correct_key.bin[i])
        return num_errors / len(self.final_key)

    def _deep_sum(self, lst):
        return sum(self._deep_sum(el) if isinstance(el, list) else el for el in lst)

    def exchanged_msg_len(self):
        return self._deep_sum(self.channel_uses)

    def num_channel_uses(self):
        num = 0
        for iteration in self.channel_uses:
            num += 1
            max_len = 0
            for i in range(1, len(iteration)):  # for each iteration get the minimum needed number of uses
                max_len = max(max_len, len(iteration[i]))
            num += max_len
        return num

    def _calculate_efficiency(self):
        """
        TODO: other formula was: return
        sum(self.channel_uses) / (len(self.initial_key) * -len(self.initial_key) * log2(1 - self.error_rate))
        """
        # print(1 - sum(self.channel_uses)/len(self.initial_key))
        # print(self.error_rate)
        # print( -self.error_rate*log2(self.error_rate)-(1-self.error_rate)*log2(1-self.error_rate))
        return (1 - self.exchanged_msg_len() / len(self.initial_key)) / (
            -self.error_rate*log2(self.error_rate)-(1-self.error_rate)*log2(1-self.error_rate))

    def calculate_parameters(self):
        if self.final_key != self.correct_key:
            self.correct = False
            self.bit_error_ratio = self._calculate_ber()

        self.efficiency = self._calculate_efficiency()

    def flush_to_file(self, filename):
        with open(filename, 'a') as f:
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (self.correct_key,
                                                      self.initial_key,
                                                      self.final_key,
                                                      self.error_rate,
                                                      self.correct,
                                                      self.bit_error_ratio,
                                                      self.efficiency,
                                                      self.num_channel_uses(),
                                                      self.seed))

    @staticmethod
    def from_line(line):
        split = line.split(',')
        status = Status(split[0], split[1], split[3], split[-1])
        return status

