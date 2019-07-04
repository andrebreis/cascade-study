import math

from implementations.template import CascadeTemplate


class YanetalCascade(CascadeTemplate):

    def __init__(self, correct_party, key, error_rate, status, seed, block_parity_inference):
        CascadeTemplate.__init__(self, correct_party, key, error_rate, status, seed, block_parity_inference)
        self.num_iterations = 10

    def get_iteration_blocks(self, iter_num):
        block_size = math.ceil(0.8 / self.error_rate)
        if iter_num == 0:
            blocks = []
            for i in range(0, len(self.key), block_size):  # create list of block indexes [[0,1,2,3],[4,5,6,7]]
                blocks.append(list(range(i, min(i + block_size, len(self.key)))))
            return blocks
        if iter_num == 1:
            return self.shuffle_blocks(block_size * 5)
        return self.shuffle_blocks(math.ceil(len(self.correct_key)/2))

    def run_algorithm(self):
        CascadeTemplate.run_algorithm(self)
        self.status.end_run(self.key)
