import os

DATASET_SIZE = 100000


def get_datasets_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasets', 'csv', filename))


def get_results_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results', filename))
