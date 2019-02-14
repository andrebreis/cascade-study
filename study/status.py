from math import log2


class Status(object):

    def __init__(self, correct_key, initial_key, error_rate):
        self.correct_key = correct_key
        self.initial_key = initial_key
        self.error_rate = error_rate

        self.final_key = None
        self.channel_uses = []
        self.correct = True
        self.bit_error_ratio = 0
        self.efficiency = 1.0

    def _calculate_ber(self):
        num_errors = 0
        for i in range(0, len(self.final_key)):
            num_errors += int(self.final_key[i]) ^ int(self.correct_key[i])
        return num_errors / len(self.final_key)

    def _calculate_efficiency(self):
        """
        TODO: other formula was: return (1 - sum(self.channel_uses)/len(self.initial_key))/ (
        -self.error_rate*log2(self.error_rate)-(1-self.error_rate)*log2(1-self.error_rate))
        """
        return sum(self.channel_uses) / (len(self.initial_key) * len(self.initial_key) * (1 - self.error_rate))

    def calculate_parameters(self):
        if self.final_key != self.correct_key:
            self.correct = False
            self.bit_error_ratio = self._calculate_ber()

        self.efficiency = self._calculate_efficiency()

    def flush_to_file(self, filename):
        with open(filename, 'a') as f:
            f.write('%s,%s,%s,%s,%s,%s,%s,%s\n' % (self.correct_key,
                                                   self.initial_key,
                                                   self.final_key,
                                                   self.error_rate,
                                                   self.correct,
                                                   self.bit_error_ratio,
                                                   self.efficiency,
                                                   self.channel_uses))


