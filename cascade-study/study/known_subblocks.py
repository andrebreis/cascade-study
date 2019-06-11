import known


class KnownSubblocks(object):
    def __init__(self, key_length):
        self.row_length = key_length + 1
        self.matrix = known.init(self.row_length)

    def create_row(self, block, parity):
        return known.create_row(self.matrix, block, parity)

    def is_known(self, row):
        return known.is_known(self.matrix, row)

    def insert_row(self, row):
        return known.insert_row(self.matrix, row)

    def __del__(self):
        known.delete(self.matrix)
