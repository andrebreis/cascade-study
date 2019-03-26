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

    def cascade_effect(self, current_block, current_iter, iterations, parities, correct_parities):
        errors_to_process = [(current_iter, current_block)]

        while errors_to_process:
            (iteration, processing_block) = errors_to_process.pop()
            if parities[iteration][processing_block] != correct_parities[iteration][processing_block]:
                correcting_index = self._binary(iterations[iteration][processing_block])
                self.key.invert(correcting_index)
                parities[iteration].invert(processing_block)
                for i in range(0, current_iter + 1):
                    if i != iteration:
                        block_to_process = self._get_block_containing_index(iterations[i], correcting_index)
                        parities[i].invert(block_to_process)
                        errors_to_process.append((i, block_to_process))
                errors_to_process.sort(key=lambda x: x[0])

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
                self.status.start_block()
                self.cascade_effect(i, iter_num, iterations, parities, correct_parities)

            self.status.save_iteration_info(self.key)

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
