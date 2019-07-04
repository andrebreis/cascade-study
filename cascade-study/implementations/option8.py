import math

from datasets.generator import _generate_keypair
from implementations.template import CascadeTemplate
from study.status import Status
from utils.key import Key


class Option8(CascadeTemplate):

    def __init__(self, correct_party, key, error_rate, status, seed, block_parity_inference):
        CascadeTemplate.__init__(self, correct_party, key, error_rate, status, seed, block_parity_inference)
        self.num_iterations = 14

    def get_iteration_blocks(self, iter_num):
        alpha = math.log2(1/self.error_rate)-0.5
        block_size = pow(2, math.ceil(alpha))
        if iter_num == 0:
            blocks = []
            for i in range(0, len(self.key), block_size):  # create list of block indexes [[0,1,2,3],[4,5,6,7]]
                blocks.append(list(range(i, min(i + block_size, len(self.key)))))
            return blocks
        if iter_num == 1:
            return self.shuffle_blocks(pow(2, math.ceil((alpha+12)/2)))
        if iter_num == 2:
            return self.shuffle_blocks(math.ceil(len(self.correct_key)/4))

        return self.shuffle_blocks(math.ceil(len(self.correct_key)/2))

    def run_algorithm(self):
        CascadeTemplate.run_algorithm(self)
        self.status.end_run(self.key)

if __name__ == '__main__':
    c_key, key = _generate_keypair(16384, 0.01)
    run = Option8(Key(c_key.hex), Key(key.hex), 0.01, Status('asd', 1, 'asd', 1000, 2), 1000, False)
    run.run_algorithm()
