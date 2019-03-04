import math
import random


class CascadeTemplate(object):

    def __init__(self, correct_key, key, error_rate, status, seed):
        self.correct_key = correct_key
        self.key = key
        self.error_rate = error_rate
        self.num_iterations = 0
        self.status = status
        self.seed = seed

    def estimate_error(self):
        return self.key.hamming_distance(self.correct_key) / len(self.key)

    def shuffle_blocks(self, block_size):
        blocks = []

        temp_indices = list(range(0, len(self.key)))
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
        parities = []
        correct_parities = []

        self.status.initialize_run(self.correct_key, self.error_rate, self.estimate_error())
        random.seed(self.seed)

        for iter_num in range(0, self.num_iterations):
            iterations.append(self.get_iteration_blocks(iter_num))
            parities.append(self.key.calculate_parities(iterations[iter_num]))
            correct_parities.append(self.correct_key.calculate_parities(iterations[iter_num]))

            self.status.start_iteration({'len': len(correct_parities[iter_num])})

            for i in range(0, len(correct_parities[iter_num])):
                corrected_index = iterations[iter_num][i][0]
                for j in range(0, iter_num + 1):
                    correcting_block = self._get_block_containing_index(iterations[iter_num - j],
                                                                        corrected_index)
                    if correcting_block is None:
                        continue
                    if parities[iter_num - j].bin[correcting_block] != \
                            correct_parities[iter_num - j].bin[correcting_block]:
                        self.status.start_block()
                        corrected_index = self._binary(iterations[iter_num - j][correcting_block])
                        if corrected_index is not None:
                            self.key.invert(corrected_index)
                            for k in range(0, len(parities)):
                                corrected_block = self._get_block_containing_index(iterations[k], corrected_index)
                                parities[k].invert(corrected_block)

        self.status.end_run(self.key)

    def _binary(self, block, iteration_num=0):
        """
        Finds the index of an odd error in the given block
        :param block list indexes of the bits of key forming the block to perform the protocol
        :returns the index of the error
        """
        first_half_size = math.ceil(len(block) / 2)
        correct_first_half_par = self.correct_key.calculate_block_parity(block[:first_half_size])
        self.status.add_channel_use({'len': 1})
        iteration_num += 1
        first_half_par = self.key.calculate_block_parity(block[:first_half_size])

        if first_half_par != correct_first_half_par:
            if first_half_size == 1:
                return block[0]
            else:
                return self._binary(block[:first_half_size], iteration_num)
        else:
            if len(block) - first_half_size == 1:
                return block[-1]
            else:
                return self._binary(block[first_half_size:], iteration_num)
