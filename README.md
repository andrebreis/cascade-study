# A look into the the Cascade Protocol

This repository will hold a study on the optimization of the Cascade Protocol. This protocol is being studied in order to be used in the Information Reconciliation step of Quantum Key Distribution Post Processing

## Installation

## Usage 

### Create Dataset

To create a dataset of pairs of keys with a desired error rate, the following command is available:

```
cascade-study create_dataset <key length> <error rate> [options]
```

Available options are:
```
-s --size  <dataset size>         Set the number of key pairs in the dataset (default is 10000)
-o --out <output filename>        Set the name of the output file (default is <key length)-<error rate>.csv
-nc --num-cores <number of cores> Set the number of processor cores to use to create the dataset
-v --verbose                      Set the printing of the number of completed tasks to verbose
```

### Run Algorithm

To run an algorithm for a dataset, the following command is available:

```
cascade-study run_algorithm <algorithm> <dataset file> [options]
```

The possible algorithms are `original`, `biconf`, `yanetal`, `option7` and `option8`. The available options are:

```
-bi --block-inference             Use the Block Parity Inference optimization
-nl --num-lines  <dataset size>   Set the number of key pairs to process
-r --runs <num runs>              Set the number of algorithm runs per key pair (using different seeds). Default = 1
-sl --stats-level <1|2|3>         Set the level of stats to output (1 = no stats, 2 = regular output (default), 3 = BER for all iterations)   
-o --out <output filename>        Set the name of the output file (default is <algorithm>-<key length)-<error rate>.res.csv
-nc --num-cores <number of cores> Set the number of processor cores to use to run the algorithm
-v --verbose                      Set the printing of the number of completed tasks to verbose
```

### Replicate Run

To validate the results a run of the algorithm (verify the integrity or replicability of results):

```
cascade-study replicate_run <algorithm> <results file> [options]
```

Available options are:
```
-bi --block-inference             Use the Block Parity Inference optimization
-nl --num-lines  <dataset size>   Set the number of key pairs to process
-r --runs <num runs>              Set the number of algorithm runs per key pair (using different seeds). Default = 1
-sl --stats-level <1|2|3>         Set the level of stats to output (1 = no stats, 2 = regular output (default), 3 = BER for all iterations)   
-o --out <output filename>        Set the name of the output file (default is <algorithm>-<key length)-<error rate>.res.csv
-nc --num-cores <number of cores> Set the number of processor cores to use to run the algorithm
-v --verbose                      Set the printing of the number of completed tasks to verbose
```

This will output a replica file with the results of running the algorithm with the same keys and random seeds. In order to obtain a correct validation, both the `algorithm` argument and the `block-inference` flag must have the same values as the original run. The original dataset file must also be available. The results can be compared by a line by line comparison. This can easily be achieved by using a bash script like:

```
if [ "‘sort <original file>‘" == "‘sort <replica file>‘" ]; then echo ’Valid results’;
fi
```

### Process results

To process the files with results from `run_algorithm`, the following command is available:

```
cascade-study process_results <results file>* [-o <output_file>]
```

This will process all input files into a file with the average and variance for each field. To extract the name of the algorithm and key length, it expects the files to be named: `<algorithm>`-`<key length>`-[irrelevant].
  
 ### Create chart
 
 To create charts from the data in a file like the process results output file, the following command is available:
 
 ```
 cascade-study create_chart <input file> <x axis name> <y axis name> [options]
 ```

<x axis name> and <y axis name> should be the name of the columns of the csv input file to use for the axis (e.g. avg eff)

The following options are available:

```
-l --line <line name> <column to restrict> <value to restrict> Set the constant parameter to draw a line (usually the algorithm). 
Can be used multiple times to create multiple lines.
-vk --variance key <column name>  Set the name of the column for the error bars (Length = twice the standard deviation)
-r --restrictions <column to restrict> <value to restrict> Show only the results for the parameter with the given name to the given value (usually restrict the key length or error rate, depending on the x axis)
-xt <tick distance>               Set the distance between ticks for the x axis
-yt <tick distance>               Set the distance between ticks for the y axis
-xr <min> <max>                   Set the range for the x axis
-yr <min> <max>                   Set the range for the y axis
-xf <format>                      Set the format for the ticks on the x axis (e.g. .4f)
-yf <format>                      Set the format for the ticks on the y axis (e.g. .4f)
-t --title <title>                Set the title of the chart.
-o --out <output file>            Set the output file name. Defaults to the title if has no input
```


