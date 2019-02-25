import math
import multiprocessing
import random
import time

from joblib import Parallel, delayed

from datasets.generator import read_keypair
from implementations.original import OriginalCascade
from study.statistics import Statistics


def run_study(filename, i):
    correct_key, key = read_keypair(filename, i)
    stats = Statistics('firstrun.csv')
    run = OriginalCascade(correct_key, key, stats, time.time())
    run.run_algorithm()


if __name__ == '__main__':
    num_cores = multiprocessing.cpu_count()

    Parallel(n_jobs=num_cores, verbose=50)(
        delayed(run_study)('../datasets/csv/1024-5.csv', i) for i in range(0, 1000))
    # size = 8
    # c_key = Key('1'*pow(2, size))
    # max_err = math.ceil(pow(2, size)*0.05)
    # key = Key('1' * pow(2, size))
    # for i in range(0, max_err):
    #     index = random.randint(0, pow(2, size)-1)
    #     key.invert(index)
    # #
    # stats = Statistics('testfile.csv')
    #
    # run = OriginalCascade(c_key, key, stats, time.time())
    # run.run_algorithm()
    #
    # stats = Statistics('testfile2.csv', infile='testfile.csv')
    # replicate(stats, 1)
    # print(run.correct_party.key == run.key)
    # replicate(stats, 1)
