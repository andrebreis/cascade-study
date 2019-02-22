from bitstring import BitArray


class Key(BitArray):

    def __new__(cls, binary_str):
        return super(Key, cls).__new__(cls, bin=binary_str)

    def __init__(self, binary_str):
        super(Key, self).__init__(self, bin=binary_str)

    def calculate_block_parity(self, block_indexes):
        parity = 0
        for index in block_indexes:
            parity = (parity + int(self.bin[index])) % 2
        return parity

    def calculate_parities(self, block_list):
        parities = ''
        for block in block_list:
            parities += str(self.calculate_block_parity(block))
        return BitArray(bin=parities)

    def hamming_distance(self, other_key):
        num_errors = 0
        for i in range(0, len(self.bin)):
            if self.bin[i] != other_key.bin[i]:
                num_errors += 1
        return num_errors
