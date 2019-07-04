import inference


class BlockParityInference(object):
    def __init__(self, key_length):
        self.row_length = key_length + 1
        self.matrix = inference.init(self.row_length)

    def create_row(self, block, parity):
        return inference.create_row(self.matrix, block, parity)

    def can_be_inferred(self, row):
        return inference.can_be_inferred(self.matrix, row)

    def insert_row(self, row):
        return inference.insert_row(self.matrix, row)

    def __del__(self):
        inference.delete(self.matrix)
