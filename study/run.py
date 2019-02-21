import math
import random
import time

from bitstring import BitArray

from implementations.original import OriginalCascade
from implementations.template import CascadeTemplate
from study.statistics import Statistics


def replicate(stats, line):
    line = str(line)
    correct_key = BitArray(bin=stats.status[line].correct_key)
    key = BitArray(bin=stats.status[line].initial_key)
    seed = float(stats.status[line].seed)
    run = OriginalCascade(CascadeTemplate(correct_key, correct_key, None, None), key, stats, seed)
    run.run_algorithm()
    print(run.correct_party.key == run.key)


if __name__ == '__main__':

    size = 8
    c_key = BitArray(bin='1'*pow(2, size))
    max_err = math.ceil(pow(2, size)*0.05)
    key = BitArray(bin='1' * pow(2, size))
    for i in range(0, max_err):
        index = random.randint(0, pow(2, size)-1)
        key.invert(index)

    stats = Statistics('testfile.csv')

    # run = OriginalCascade(CascadeTemplate(stats.status['1'].correct_key, stats.status['1'].correct_key, None, None), stats.status['1'].initial_key, stats, stats.status['1'].seed)
    # run.run_algorithm()
    run = OriginalCascade(CascadeTemplate(c_key, c_key, None, None), key, stats, time.time())
    run.run_algorithm()

    stats = Statistics('testfile2.csv', infile='testfile.csv')
    replicate(stats, 1)
    # print(run.correct_party.key == run.key)
    # replicate(stats, 1)
