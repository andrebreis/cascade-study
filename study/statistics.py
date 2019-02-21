import os

from study.status import Status


class Statistics(object):

    def __init__(self, filename, infile=None):
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        if not os.path.isfile(filename):
            with open(filename, 'w') as f:
                f.write('correct key,initial key,final key,error rate,correct,ber,efficiency,channel_uses,seed\n')
        self.filename = filename
        self.status = {}
        if infile is not None:
            self.read_status(infile)

    def read_status(self, file):
        if not os.path.isfile(file):
            print('%s does not exist, ignoring...' % file)
            return

        with open(file, 'r') as f:
            lines = f.readlines()
            for i in range(1, len(lines)):
                if lines[i] != '\n':
                    self.status[str(i)] = Status.from_line(lines[i])

    def initialize_run(self, id, c_key, key, error, seed):
        self.status[id] = Status(c_key, key, error, seed)

    def start_iteration(self, id, channel_use):
        self.status[id].start_iteration(channel_use)

    def start_block(self, id):
        self.status[id].start_block()

    def register_channel_use(self, id, channel_use):
        self.status[id].add_channel_use(channel_use)

    def end_run(self, id, key):
        self.status[id].final_key = key

        self.status[id].calculate_parameters()

        self.status[id].flush_to_file(self.filename)
        del self.status[id]
