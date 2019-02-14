import math
import random
import time


class CascadeTemplate(object):

    def __init__(self, correct_party, key, stats):
        self.correct_party = correct_party
        self.key = key
        self.num_iterations = 0
        self.stats = stats
        self.id = str(time.time())

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
        # TODO: random.seed(random_seed) and save seed
        random.shuffle(temp_indices)

        for i in range(0, len(self.key), block_size):
            blocks.append(temp_indices[i:min(i + block_size, len(self.key))])

        return blocks

    def get_iteration_blocks(self, iter_num):
        pass

    @staticmethod
    def _get_block_containing_index(iteration, index):
        for i in range(0, len(iteration)):
            if index in iteration[i]:
                return i

    def run_algorithm(self):
        iterations = []

        self.stats.initialize_run(self.id, self.correct_party.key.bin, self.key.bin, self.estimate_error())

        for iter_num in range(0, self.num_iterations):
            iterations.append(self.get_iteration_blocks(iter_num))
            parities = self.calculate_parities(iterations[iter_num])

            correct_parities = self.correct_party.calculate_parities(iterations[iter_num])
            self.stats.register_channel_use(self.id, {'len': len(correct_parities)})

            for i in range(0, len(correct_parities)):
                if parities[i] != correct_parities[i]:
                    corrected_index = iterations[iter_num][i][0]
                    for j in range(0, iter_num + 1):
                        correcting_block = self._get_block_containing_index(iterations[iter_num - j],
                                                                            corrected_index)
                        if correcting_block is None:
                            continue
                        corrected_index = self._binary(iterations[iter_num - j][correcting_block])
                        if corrected_index is not None:
                            self.key.invert(corrected_index)

        self.stats.end_run(self.id, self.key.bin)

    def _binary(self, block):
        """
        Finds the index of an odd error in the given block
        :param block list indexes of the bits of key forming the block to perform the protocol
        :returns the index of the error
        """
        first_half_size = math.ceil(len(block) / 2)
        correct_first_half_par = self.correct_party.calculate_parity(block[:first_half_size])
        self.stats.register_channel_use(self.id, {'len': 1})

        first_half_par = self.calculate_parity(block[:first_half_size])

        if first_half_par != correct_first_half_par:
            if first_half_size == 1:
                return block[0]
            else:
                return self._binary(block[:first_half_size])
        else:
            if len(block) - first_half_size == 1:
                return block[-1]
            else:
                return self._binary(block[first_half_size:])
