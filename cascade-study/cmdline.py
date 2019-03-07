import multiprocessing
import uuid
from argparse import ArgumentParser
import sys

from joblib import Parallel, delayed

from datasets.generator import generate_dataset, read_keypair
from implementations.biconf import CascadeBiconf
from implementations.original import OriginalCascade
from study.status import Status
from utils.key import Key
from utils.study_utils import DATASET_SIZE, get_datasets_path, get_results_path


def execute():
    cmd = sys.argv[1:2]

    parser = ArgumentParser(description='Cascade study')
    subparsers = parser.add_subparsers(title='command', dest='command')

    parser_list = subparsers.add_parser('create_dataset', help='Create a dataset for the study')
    parser_list.set_defaults(func=create_dataset)

    parser_list = subparsers.add_parser('run_algorithm', help='Run an algorithm on a dataset')
    parser_list.set_defaults(func=run_algorithm)

    parser_list = subparsers.add_parser('replicate_run', help='Replicate other run to validate the results')
    parser_list.set_defaults(func=replicate_run)

    if len(cmd) == 0:
        parser.print_help()
        return
    args = parser.parse_args(cmd)
    args.func()


def create_dataset(cmd=None):
    if not cmd:
        cmd = sys.argv[2:]

    num_cores = multiprocessing.cpu_count()

    parser = ArgumentParser(description='Create dataset',
                            usage='create_dataset keylen error_rate -s size -o out -nc num_cores')
    parser.add_argument('key_len', type=int, help='Key length for the dataset')
    parser.add_argument('error_rate', type=float, help='Error rate for the dataset')
    parser.add_argument('-s', '--size', type=int, default=DATASET_SIZE, help='Size of the dataset')
    parser.add_argument('-o', '--out', default='dataset.csv', type=str, help='Name of the file to output dataset')
    parser.add_argument('-nc', '--num-cores', type=int, default=num_cores, choices=range(1, num_cores + 1),
                        help='Number of cores to allocate for the execution')

    args = parser.parse_args(cmd)
    generate_dataset(get_datasets_path(args.out), args.key_len, args.error_rate, args.num_cores, args.size)


def run_study(stats_file, dataset_file, algorithm, line_num, runs):
    correct_key, key, error_rate = read_keypair(get_datasets_path(dataset_file), line_num)
    for _ in range(0, runs):
        seed = str(uuid.uuid4())
        stats = Status(stats_file, dataset_file, line_num, seed)
        run = algorithm(Key(correct_key.hex), Key(key.hex), error_rate, stats, seed)
        run.run_algorithm()


def run_algorithm(cmd=None):
    algorithms = {
        'original': OriginalCascade,
        'biconf': CascadeBiconf
    }

    if not cmd:
        cmd = sys.argv[2:]

    num_cores = multiprocessing.cpu_count()

    parser = ArgumentParser(description='Run algorithm',
                            usage='run_algorithm algorithm dataset -o out -r runs -nc num_cores -nl num_lines')
    parser.add_argument('algorithm', type=str, choices=algorithms.keys(), help='Name of the algorithm to run')
    parser.add_argument('dataset', type=str, help='Name of the file containing the dataset')
    parser.add_argument('-o', '--out', default='out.csv', type=str, help='Name of the file to output results')
    parser.add_argument('-r', '--runs', default=100, type=int, help='Number of algorithm runs per key')
    parser.add_argument('-nc', '--num-cores', type=int, default=num_cores, choices=range(1, num_cores + 1),
                        help='Number of cores to allocate for the execution')
    parser.add_argument('-nl', '--num-lines', type=int, default=DATASET_SIZE, help='Number of lines to process')

    args = parser.parse_args(cmd)

    Parallel(n_jobs=args.num_cores, verbose=50)(
        delayed(run_study)(get_results_path(args.out), args.dataset, algorithms[args.algorithm], i, args.runs) for i in
        range(0, args.num_lines))


def replicate_line(infile, outfile, algorithm, line_num):
    stats = Status.from_line(outfile, infile, line_num)
    correct_key, key, error_rate = read_keypair(get_datasets_path(stats.dataset_file), stats.dataset_line)
    run = algorithm(correct_key, key, error_rate, stats, stats.seed)
    run.run_algorithm()


def replicate_run(cmd=None):
    algorithms = {
        'original': OriginalCascade,
        'biconf': CascadeBiconf
    }

    if not cmd:
        cmd = sys.argv[2:]

    num_cores = multiprocessing.cpu_count()

    parser = ArgumentParser(description='Replicate run',
                            usage='replicate_run algorithm infile -o out -nc num_cores -nl num_lines')
    parser.add_argument('algorithm', type=str, choices=algorithms.keys(), help='Name of the algorithm to run')
    parser.add_argument('infile', type=str, help='Name of the results file to validate')
    parser.add_argument('-o', '--out', default='replicate_out.csv', type=str, help='Name of the file to output results')
    parser.add_argument('-nc', '--num-cores', type=int, default=num_cores, choices=range(1, num_cores + 1),
                        help='Number of cores to allocate for the execution')
    parser.add_argument('-nl', '--num-lines', type=int, default=DATASET_SIZE, help='Number of lines to process')

    args = parser.parse_args(cmd)

    Parallel(n_jobs=args.num_cores, verbose=50)(
        delayed(replicate_line)(get_results_path(args.infile), get_results_path(args.out), algorithms[args.algorithm],
                                i) for i in range(1, args.num_lines)
    )


if __name__ == '__main__':
    execute()
