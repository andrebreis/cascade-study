import multiprocessing
import time
import uuid
from argparse import ArgumentParser
import sys
from secrets import randbits

from joblib import Parallel, delayed

from datasets.generator import generate_dataset, read_keypair
from implementations.original import OriginalCascade
from study.statistics import Statistics
from utils.key import Key
from utils.study_utils import DATASET_SIZE, get_datasets_path, get_results_path


def create_argument_parser():
    cmd = sys.argv[1:2]

    parser = ArgumentParser(description='Cascade study')
    subparsers = parser.add_subparsers(title='command', dest='command')

    parser_list = subparsers.add_parser('create_dataset', help='Create a dataset for the study')
    parser_list.set_defaults(func=create_dataset)

    parser_list = subparsers.add_parser('run_algorithm', help='Run an algorithm on a dataset')
    parser_list.set_defaults(func=run_algorithm)

    if len(cmd) == 0:
        parser.print_help()
        return
    args = parser.parse_args(cmd)
    args.func()


def create_dataset(cmd=None):
    if not cmd:
        cmd = sys.argv[2:]

    parser = ArgumentParser(description='Create dataset', usage='create_dataset keylen error_rate [-s size] [-o out]')
    parser.add_argument('key_len', type=int, help='Key length for the dataset')
    parser.add_argument('error_rate', type=float, help='Error rate for the dataset')
    parser.add_argument('-s', '--size', type=int, default=DATASET_SIZE, required=False, help='Size of the dataset')
    parser.add_argument('-o', '--out', default='dataset.csv', type=str, help='Name of the file to output dataset')

    args = parser.parse_args(cmd)
    generate_dataset(get_datasets_path(args.out), args.key_len, args.error_rate, args.size)


def run_study(stats, filename, algorithm, i):
    correct_key, key = read_keypair(filename, i)
    for _ in range(0, 100):
        run = algorithm(Key(correct_key.hex), Key(key.hex), stats, uuid.uuid4())
        run.run_algorithm()


def run_algorithm(cmd=None):

    algorithms = {
        'original': OriginalCascade
    }

    if not cmd:
        cmd = sys.argv[2:]

    parser = ArgumentParser(description='Run algorithm', usage='run_algorithm algorithm dataset [-o out]')
    parser.add_argument('algorithm', type=str, choices=algorithms.keys(), help='Name of the algorithm to run')
    parser.add_argument('dataset', type=str, help='Name of the file containing the dataset')
    parser.add_argument('-o', '--out', default='out.csv', type=str, help='Name of the file to output results')

    args = parser.parse_args(cmd)
    statistics = Statistics(get_results_path(args.out))

    num_cores = multiprocessing.cpu_count()

    Parallel(n_jobs=num_cores, verbose=50)(
        delayed(run_study)(statistics, args.dataset, algorithms[args.algorithm], i) for i in range(0, DATASET_SIZE))


if __name__ == '__main__':
    create_argument_parser()
