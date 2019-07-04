import multiprocessing
import uuid
from argparse import ArgumentParser
import sys

from joblib import Parallel, delayed

from datasets.generator import generate_dataset, read_keypair
from implementations.biconf import CascadeBiconf
from implementations.option7 import Option7
from implementations.option8 import Option8
from implementations.original import OriginalCascade
from implementations.yanetal import YanetalCascade
from study import results, charts
from study.status import Status, NO_LOG, FINAL_DATA, ALL_DATA
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

    parser_list = subparsers.add_parser('process_results', help='Process results')
    parser_list.set_defaults(func=process_results)

    parser_list = subparsers.add_parser('create_graph', help='Create graph')
    parser_list.set_defaults(func=create_chart)

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
    parser.add_argument('-o', '--out', default='', type=str, help='Name of the file to output dataset')
    parser.add_argument('-nc', '--num-cores', type=int, default=num_cores, choices=range(1, num_cores + 1),
                        help='Number of cores to allocate for the execution')
    parser.add_argument('-v', '--verbose', action='store_const', const=50, default=15)

    args = parser.parse_args(cmd)
    if args.out == '':
        args.out = str(args.key_len) + '-' + str(args.error_rate).replace('.', '') + '.csv'
    generate_dataset(get_datasets_path(args.out), args.key_len, args.error_rate, args.num_cores, args.size,
                     args.verbose)


def run_study(stats_file, dataset_file, algorithm, line_num, runs, stats_level, block_reuse):
    correct_key, key, error_rate = read_keypair(get_datasets_path(dataset_file), line_num)
    for _ in range(0, runs):
        seed = str(uuid.uuid4())
        stats = Status(stats_file, dataset_file, line_num, seed, stats_level)
        run = algorithm(Key(correct_key.hex), Key(key.hex), error_rate, stats, seed, block_reuse)
        run.run_algorithm()


def run_algorithm(cmd=None):
    algorithms = {
        'original': OriginalCascade,
        'biconf': CascadeBiconf,
        'yanetal': YanetalCascade,
        'option7': Option7,
        'option8': Option8
    }

    if not cmd:
        cmd = sys.argv[2:]

    num_cores = multiprocessing.cpu_count()

    parser = ArgumentParser(description='Run algorithm',
                            usage='run_algorithm algorithm dataset -o out -r runs -nc num_cores -nl num_lines ' +
                                  '-sl stats_level -bi')
    parser.add_argument('algorithm', type=str, choices=algorithms.keys(), help='Name of the algorithm to run')
    parser.add_argument('dataset', type=str, help='Name of the file containing the dataset')
    parser.add_argument('-o', '--out', default='', type=str, help='Name of the file to output results')
    parser.add_argument('-r', '--runs', default=1, type=int, help='Number of algorithm runs per key')
    parser.add_argument('-nc', '--num-cores', type=int, default=num_cores, choices=range(1, num_cores + 1),
                        help='Number of cores to allocate for the execution')
    parser.add_argument('-nl', '--num-lines', type=int, default=DATASET_SIZE, help='Number of lines to process')
    parser.add_argument('-sl', '--stats-level', type=int, default=FINAL_DATA, choices=[NO_LOG, FINAL_DATA, ALL_DATA],
                        help='Stats level: 1 - NO LOG, 2 - FINAL DATA, 3 - ALL DATA')
    parser.add_argument('-bi', '--block-inference', action='store_const', const=True, default=False,
                        help='Run algorithm with block parity inference optimization')
    parser.add_argument('-v', '--verbose', action='store_const', const=50, default=15)

    args = parser.parse_args(cmd)
    if args.out == '':
        args.out = args.algorithm + '/' + args.algorithm + '-' + args.dataset.replace('.csv', '.res.csv')
    Parallel(n_jobs=args.num_cores, verbose=args.verbose)(
        delayed(run_study)(get_results_path(args.out), args.dataset, algorithms[args.algorithm], i, args.runs,
                           args.stats_level, args.block_inference) for i in
        range(0, args.num_lines))


def replicate_line(infile, outfile, algorithm, line_num, stats_level, block_reuse):
    stats = Status.from_line(outfile, infile, line_num, stats_level)
    correct_key, key, error_rate = read_keypair(get_datasets_path(stats.dataset_file), stats.dataset_line)
    run = algorithm(correct_key, key, error_rate, stats, stats.seed, block_reuse)
    run.run_algorithm()


def replicate_run(cmd=None):
    algorithms = {
        'original': OriginalCascade,
        'biconf': CascadeBiconf,
        'yanetal': YanetalCascade,
        'option7': Option7,
        'option8': Option8
    }

    if not cmd:
        cmd = sys.argv[2:]

    num_cores = multiprocessing.cpu_count()

    parser = ArgumentParser(description='Replicate run',
                            usage='replicate_run algorithm infile -o out -nc num_cores -nl num_lines -bi')
    parser.add_argument('algorithm', type=str, choices=algorithms.keys(), help='Name of the algorithm to run')
    parser.add_argument('infile', type=str, help='Name of the results file to validate')
    parser.add_argument('-o', '--out', default='', type=str, help='Name of the file to output results')
    parser.add_argument('-nc', '--num-cores', type=int, default=num_cores, choices=range(1, num_cores + 1),
                        help='Number of cores to allocate for the execution')
    parser.add_argument('-nl', '--num-lines', type=int, default=DATASET_SIZE, help='Number of lines to process')
    parser.add_argument('-sl', '--stats-level', type=int, default=FINAL_DATA, choices=[NO_LOG, FINAL_DATA, ALL_DATA],
                        help='Stats level: 1 - NO LOG, 2 - FINAL DATA, 3 - ALL DATA')
    parser.add_argument('-bi', '--block-inference', action='store_const', const=True, default=False,
                        help='Run algorithm with block parity inference optimization')
    parser.add_argument('-v', '--verbose', action='store_const', const=50, default=15)

    args = parser.parse_args(cmd)
    if args.out == '':
        args.out = args.infile.replace('.csv', '.replica.csv')

    Parallel(n_jobs=args.num_cores, verbose=args.verbose)(
        delayed(replicate_line)(get_results_path(args.infile), get_results_path(args.out), algorithms[args.algorithm],
                                i, args.stats_level, args.block_inference) for i in range(1, args.num_lines+1)
    )


def process_result(infile, outfile):
    f = open(outfile, 'a')
    data = results.get_stats(infile)
    f.write('\n' + ','.join(map(lambda x: str(x), data)))
    f.close()


def process_results(cmd=None):
    if not cmd:
        cmd = sys.argv[2:]

    parser = ArgumentParser(description='Process results',
                            usage='process_results files -o out')
    parser.add_argument('files', nargs='+')
    parser.add_argument('-o', '--out', default='res.csv', type=str, help='Name of the file to output results')

    args = parser.parse_args(cmd)

    results.create_file_header(args.out)
    for file in args.files:
        process_result(file, args.out)


def create_chart(cmd=None):
    if not cmd:
        cmd = sys.argv[2:]

    parser = ArgumentParser(description='Create chart',
                            usage='create_graph infile xaxis yaxis -vk variance_key [-l line_name restrictions]*')
    parser.add_argument('infile', type=str, help='Name of the results file to use')
    parser.add_argument('xaxis', type=str, help='Name of the parameter of the x axis')
    parser.add_argument('yaxis', type=str, help='Name of the parameter of the y axis')
    parser.add_argument('-vk', '--variance-key', default=None, help="Name of the parameter for the variance")
    parser.add_argument('-r', '--restrictions', nargs='+')
    parser.add_argument('-l', '--lines', action='append', nargs='+', metavar=('line_name', 'restrictions'))
    parser.add_argument('-xt', '--xtick', default=None, help="Tick distance of the x axis")
    parser.add_argument('-yt', '--ytick', default=None, help="Tick distance of the y axis")
    parser.add_argument('-xf', '--xformat', default='.f', help="Tick format of the x axis")
    parser.add_argument('-yf', '--yformat', default='.f', help="Tick format of the y axis")
    parser.add_argument('-yr', '--yrange', default=None, nargs='+', metavar=('min', 'max'), help="Range of the y axis")
    parser.add_argument('-t', '--title', default='', help="Title of the chart")
    parser.add_argument('-o', '--out', default='', type=str, help='Name of the file to output results')

    args = parser.parse_args(cmd)
    if args.title == '':
        args.title = args.yaxis + ' by ' + args.xaxis
    if args.out == '':
        args.out = args.title + '.png'

    graph_options = {
        'variance_key': args.variance_key,
        'title': args.title,
        'restrictions': args.restrictions,
        'lines': args.line,
        'xtick': args.xtick,
        'ytick': args.ytick,
        'xformat': args.xformat,
        'yformat': args.yformat,
        'xrange': args.xrange,
        'yrange': args.yrange,
    }

    charts.create_chart(args.infile, args.xaxis, args.yaxis, graph_options, get_results_path(args.out))


if __name__ == '__main__':
    execute()
