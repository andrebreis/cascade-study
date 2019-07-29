
class KnownSubblocks(object):
    def __init__(self):
        self.known = []

    def add_block(self, iteration, block_nr, block):
        new_block = set(block)
        if (iteration, block_nr, new_block) not in self.known:
            self.known.append((iteration, block_nr, new_block))

    def get_blocks_with_index(self, index, iteration):
        blocks = []
        for block in self.known:
            if iteration != block[0] and index in block[-1]:
                blocks.append((block[0], block[1], list(block[2])))
        return blocks

