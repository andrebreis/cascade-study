import math
import random

from study.block_parity_inference import BlockParityInference
from study.subblock_reuse import KnownSubblocks


class CascadeTemplate(object):

    def __init__(self, correct_key, key, error_rate, status, seed, block_parity_inference, subblock_reuse=True):
        self.correct_key = correct_key
        self.key = key
        self.error_rate = error_rate
        self.num_iterations = 0
        self.status = status
        self.seed = seed
        self.block_parity_inference = block_parity_inference
        self.subblock_reuse = None
        if self.block_parity_inference:
            self.inferred_blocks = BlockParityInference(len(correct_key))
        if subblock_reuse:
            self.subblock_reuse = KnownSubblocks()

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
        errors_to_process = [(current_iter, len(iterations[current_iter][current_block]), current_block,
                              iterations[current_iter][current_block])]

        while errors_to_process:
            (iteration, _, processing_block_idx, processing_block) = errors_to_process.pop()
            if parities[iteration][processing_block_idx] != correct_parities[iteration][processing_block_idx]:
                correcting_index = self._binary(processing_block, iteration, processing_block_idx)
                self.key.invert(correcting_index)
                parities[iteration].invert(processing_block_idx)
                for i in range(0, current_iter + 1):
                    if i != iteration:
                        block_to_process = self._get_block_containing_index(iterations[i], correcting_index)
                        parities[i].invert(block_to_process)
                        errors_to_process.append((i, len(iterations[i][block_to_process]), block_to_process,
                                                  iterations[i][block_to_process]))
                if self.subblock_reuse:
                    new_blocks = self.subblock_reuse.get_blocks_with_index(correcting_index)
                    for block in new_blocks:
                        errors_to_process.append((block[0], len(block[2]), block[1], block[2]))
                errors_to_process.sort(key=lambda x: x[1])

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

            unknown_blocks = []
            not_first_iteration = (iter_num > 0)  # Can always skip the last block parity after the first iteration
            if self.block_parity_inference:
                for i in range(0, len(iterations[iter_num]) - not_first_iteration):
                    row = self.inferred_blocks.create_row(iterations[iter_num][i], correct_parities[iter_num][i])
                    if not self.inferred_blocks.can_be_inferred(row):
                        unknown_blocks.append(row)
                for i in range(0, len(unknown_blocks)):
                    self.inferred_blocks.insert_row(unknown_blocks[i])
                self.status.start_iteration({'len': len(unknown_blocks)})
            else:
                self.status.start_iteration({'len': len(correct_parities[iter_num]) - not_first_iteration})

            for i in range(0, len(correct_parities[iter_num])):
                self.status.start_block()
                self.cascade_effect(i, iter_num, iterations, parities, correct_parities)

            self.status.save_iteration_info(self.key)

    def _binary(self, block, iteration, block_number):
        """
        Finds the index of an odd error in the given block
        :param block list indexes of the bits of key forming the block to perform the protocol
        :returns the index of the error
        """
        first_half_size = math.ceil(len(block) / 2)
        correct_first_half_par = self.correct_key.calculate_block_parity(block[:first_half_size])

        if self.block_parity_inference:
            row = self.inferred_blocks.create_row(block[:first_half_size], correct_first_half_par)
            if not self.inferred_blocks.can_be_inferred(row):
                self.inferred_blocks.insert_row(row)
                self.status.add_channel_use({'len': 1})
        else:
            self.status.add_channel_use({'len': 1})

        if self.subblock_reuse:
            if first_half_size != 1:
                self.subblock_reuse.add_block(iteration, block_number, block[:first_half_size])
            if len(block) - first_half_size != 1:
                self.subblock_reuse.add_block(iteration, block_number, block[first_half_size:])

        first_half_par = self.key.calculate_block_parity(block[:first_half_size])

        if first_half_par != correct_first_half_par:
            if first_half_size == 1:
                return block[0]
            else:
                return self._binary(block[:first_half_size], iteration, block_number)
        else:
            if len(block) - first_half_size == 1:
                return block[-1]
            else:
                return self._binary(block[first_half_size:], iteration, block_number)
