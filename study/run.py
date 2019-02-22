import math
import random
import time

from bitstring import BitArray

from implementations.original import OriginalCascade
from implementations.template import CascadeTemplate
from study.statistics import Statistics
from utils.key import Key


def replicate(stats, line):
    line = str(line)
    correct_key = Key(stats.status[line].correct_key)
    key = Key(stats.status[line].initial_key)
    seed = float(stats.status[line].seed)
    run = OriginalCascade(c_key, key, stats, seed)
    run.run_algorithm()
    print(run.correct_key == run.key)


if __name__ == '__main__':

    size = 8
    c_key = Key('1'*pow(2, size))
    max_err = math.ceil(pow(2, size)*0.05)
    key = Key('1' * pow(2, size))
    for i in range(0, max_err):
        index = random.randint(0, pow(2, size)-1)
        key.invert(index)

    stats = Statistics('testfile.csv')

    run = OriginalCascade(c_key, key, stats, time.time())
    run.run_algorithm()

    stats = Statistics('testfile2.csv', infile='testfile.csv')
    replicate(stats, 1)
    # print(run.correct_party.key == run.key)
    # replicate(stats, 1)
