import math

from implementations.template import CascadeTemplate


class OriginalCascade(CascadeTemplate):

    def __init__(self, correct_party, key, error_rate, status, seed, subblock_reuse):
        CascadeTemplate.__init__(self, correct_party, key, error_rate, status, seed, subblock_reuse)
        self.num_iterations = 4

    def get_iteration_blocks(self, iter_num):
        block_size = math.ceil(0.73 / self.error_rate)
        if iter_num == 0:
            blocks = []
            for i in range(0, len(self.key), block_size):  # create list of block indexes [[0,1,2,3],[4,5,6,7]]
                blocks.append(list(range(i, min(i + block_size, len(self.key)))))
            return blocks

        return self.shuffle_blocks(block_size * pow(2, iter_num))

    def run_algorithm(self):
        CascadeTemplate.run_algorithm(self)
        self.status.end_run(self.key)

