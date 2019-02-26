import os

DATASET_SIZE = 100000


def get_datasets_path(filename):
    return os.path.join('./datasets', filename)


def get_results_path(filename):
    return os.path.join('./results', filename)
