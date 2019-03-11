import math

from datasets.generator import _generate_keypair
from implementations.template import CascadeTemplate
from study.status import Status
from utils.key import Key


class CascadeBiconf(CascadeTemplate):

    def __init__(self, correct_key, key, error_rate, status, seed):
        CascadeTemplate.__init__(self, correct_key, key, error_rate, status, seed)
        self.num_iterations = 2
        self.biconf_iterations = 10

    def get_iteration_blocks(self, iter_num):
        block_size = math.ceil(0.92 / self.error_rate)
        if iter_num == 0:
            blocks = []
            for i in range(0, len(self.key), block_size):  # create list of block indexes [[0,1,2,3],[4,5,6,7]]
                blocks.append(list(range(i, min(i + block_size, len(self.key)))))
            return blocks
        elif iter_num == 1:
            return self.shuffle_blocks(block_size * 3)

        block_size = math.ceil(len(self.key)/2)
        return self.shuffle_blocks(block_size)

    def run_biconf(self):
        max_iter = 0
        num_successive_iter_no_errors = 0
        while num_successive_iter_no_errors < self.biconf_iterations:
            iteration = self.get_iteration_blocks(self.num_iterations)

            parities = self.key.calculate_parities(iteration)
            correct_parities = self.correct_key.calculate_parities(iteration)
            self.status.start_iteration({'len': len(correct_parities)})

            if parities.bin[0] != correct_parities.bin[0]:
                num_successive_iter_no_errors = 0
                for i in range(0, len(iteration)):
                    self.status.start_block()
                    correcting_index = self._binary(iteration[i])
                    if correcting_index is not None:
                        self.key.invert(correcting_index)
            else:
                num_successive_iter_no_errors += 1
                if num_successive_iter_no_errors > max_iter:
                    max_iter = num_successive_iter_no_errors
                    self.status.save_iteration_info(self.key)

    def run_algorithm(self):
        CascadeTemplate.run_algorithm(self)
        self.run_biconf()
        self.status.end_run(self.key)
