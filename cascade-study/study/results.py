from statistics import mean, pvariance
from os import makedirs
from os.path import abspath, basename, dirname, isfile


def create_file_header(filename):
    makedirs(dirname(abspath(filename)), exist_ok=True)
    if not isfile(filename):
        with open(filename, 'w') as f:
            f.write('algorithm,key length,error rate,avg eff,var eff,fer,avg ber,var ber,avg cu,var cu,'
                    'avg msg len,var msg len')


def get_stats(file):
    filename = basename(file)
    algorithm, key_length, _ = filename.split('-')

    f = open(file)
    lines = f.readlines()
    f.close()

    error_rate = []
    correct = []
    ber = []
    efficiency = []
    channel_uses = []
    msg_len = []

    for line in lines[1:]:
        split = line.replace('\n', '').split(',')
        error_rate.append(float(split[2]))
        correct.append(split[4] == 'True')
        if correct[-1]:
            efficiency.append(float(split[6]))
        else:
            ber.append(float(split[5]))
        channel_uses.append(int(split[7]))
        msg_len.append(int(split[8]))

    if not ber:
        ber = [0, 0]

    return algorithm, key_length, error_rate[0], mean(efficiency), pvariance(efficiency), 1 - (
           sum(correct) / len(error_rate)), mean(ber), pvariance(ber), mean(channel_uses), pvariance(channel_uses), \
           mean(msg_len), pvariance(msg_len)
