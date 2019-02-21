from bitstring import BitArray

from implementations.original import OriginalCascade
from implementations.template import CascadeTemplate
from study.statistics import Statistics

if __name__ == '__main__':

    c_key = '1111111111111111111111111111111111111111'
    key =   '1011111111100011111111011111111111111100'

    stats = Statistics('testfile.csv')

    run = OriginalCascade(CascadeTemplate(BitArray(bin=c_key), BitArray(bin=c_key), None), BitArray(bin=key), stats)
    run.run_algorithm()
    print(run.correct_party.key, run.key)
