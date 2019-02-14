import os

from study.status import Status


class Statistics(object):

    def __init__(self, filename):
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        if not os.path.isfile(filename):
            with open(filename, 'w') as f:
                f.write('correct key, initial key, final key, error rate, correct, ber, efficiency, channel_uses\n')
        self.filename = filename
        self.status = {}

    def initialize_run(self, id, c_key, key, error):
        self.status[id] = Status(c_key, key, error)

    def register_channel_use(self, id, channel_use):
        self.status[id].channel_uses.append(channel_use['len'])

    def end_run(self, id, key):
        self.status[id].final_key = key

        self.status[id].calculate_parameters()

        self.status[id].flush_to_file(self.filename)
        del self.status[id]
