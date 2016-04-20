#!/usr/bin/env bash
set -euo pipefail

ulimit -Sv 1000000

python3 ../divide_work.py ../10000 10 --num_labeled 100 --output_dir ../test_output

for FILENAME in ../test_output/partition_*_labeled_nodes.pickle
do
    NUM="$(basename $FILENAME | grep -o -E '[0-9]+')"
    python3 ../parallel_distributions.py ../10000 \
            "$FILENAME" ../test_output --database_name "labeled_${NUM}.db"
done
