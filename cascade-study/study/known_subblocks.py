import known


class KnownSubblocks(object):
    def __init__(self, key_length):
        self.row_length = key_length + 1
        self.matrix = known.init(self.row_length)

    def is_known(self, block, parity):
        return known.insert_if_unknown(self.matrix, block, parity)

    def __del__(self):
        known.delete(self.matrix)
