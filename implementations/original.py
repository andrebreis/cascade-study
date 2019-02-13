import math
import random


class CascadeTemplate(object):

    def __init__(self, correct_party, key):
        self.correct_party = correct_party
        self.key = key
        self.num_iterations = 0

    def calculate_parity(self, indexes):
        parity = 0
        for index in indexes:
            parity = (parity + int(self.key.bin[index])) % 2
        return parity

    def calculate_parities(self, iteration):
        parities = []
        for block in iteration:
            parities.append(self.calculate_parity(block))
        return parities

    def estimate_error(self):
        num_errors = 0.0
        for i in range(0, len(self.key)):
            if self.key.bin[i] != self.correct_party.key.bin[i]:
                num_errors += 1
        return num_errors / len(self.key)

    def shuffle_blocks(self, block_size):
        blocks = []

        temp_indices = list(range(0, len(self.key)))
        random.shuffle(temp_indices)

        for i in range(0, len(self.key), block_size):
            blocks.append(temp_indices[i:min(i + block_size, len(self.key) - 1)])

        return blocks

    def get_iteration_blocks(self, iter_num):
        pass

    @staticmethod
    def _get_block_containing_index(iteration, index):
        for i in range(0, len(iteration)):
            if index in iteration[i]:
                return i

    def run_algorithm(self):
        iterations = [[]]

        for iter_num in range(0, self.num_iterations):
            iterations.append(self.get_iteration_blocks(iter_num))
            parities = self.calculate_parities(iterations[iter_num])
            correct_parities = self.correct_party.calculate_parities(iterations[iter_num])

            for i in range(0, len(correct_parities)):
                if parities[i] != correct_parities[i]:
                    correcting_block = i
                    for j in range(0, iter_num + 1):
                        print(iter_num, j, correcting_block)
                        if correcting_block is None:
                            continue
                        corrected_index = self._binary(iterations[iter_num - j][correcting_block])
                        if iter_num - j - 1 >= 0:
                            correcting_block = self._get_block_containing_index(iterations[iter_num - j - 1],
                                                                                corrected_index)

    def _binary(self, block):
        first_half_size = math.ceil(len(block) / 2.0)
        correct_first_half_par = self.correct_party.calculate_parity(block[:first_half_size])

        first_half_par = self.calculate_parity(block[:first_half_size])

        if first_half_par != correct_first_half_par:
            if first_half_size == 1:
                self.key.invert(block[0])
                return block[0]
            else:
                return self._binary(block[:first_half_size])
        else:
            if len(block) - first_half_size == 1:
                self.key.invert(block[-1])
                return block[-1]
            else:
                return self._binary(block[first_half_size:])


class OriginalCascade(CascadeTemplate):

    def __init__(self, correct_party, key):
        CascadeTemplate.__init__(self, correct_party, key)
        self.error_rate = self.estimate_error()
        self.num_iterations = 4

    def get_iteration_blocks(self, iter_num):
        block_size = math.ceil(0.73 / self.error_rate)
        if iter_num == 0:
            blocks = []
            for i in range(0, len(self.key), block_size):  # create list of block indexes [[0,1,2,3],[4,5,6,7]]
                blocks.append(list(range(i, min(i + block_size, len(self.key) - 1))))
            return blocks

        return self.shuffle_blocks(block_size*pow(2, iter_num))

