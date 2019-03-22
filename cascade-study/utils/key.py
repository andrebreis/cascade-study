from bitstring import BitArray


class Key(BitArray):

    def __new__(cls, hex_str=''):
        return super(Key, cls).__new__(cls, hex=hex_str)

    def __init__(self, hex_str=''):
        super(Key, self).__init__(self, hex=hex_str)

    def calculate_block_parity(self, block_indexes):
        parity = 0
        bitstring = self.bin
        for index in block_indexes:
            parity = (parity + int(bitstring[index])) % 2
        return parity

    def calculate_parities(self, block_list):
        parities = ''
        for block in block_list:
            parities += str(self.calculate_block_parity(block))
        return BitArray(bin=parities)

    def hamming_distance(self, other_key):
        num_errors = 0
        self_bitstring = self.bin
        other_bitstring = other_key.bin
        for i in range(0, len(self_bitstring)):
            if self_bitstring[i] != other_bitstring[i]:
                num_errors += 1
        return num_errors
