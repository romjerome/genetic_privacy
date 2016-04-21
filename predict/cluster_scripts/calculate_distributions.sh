#!/usr/bin/env bash
set -euo pipefail

ulimit -Sv 1000000

POPULATION_DIR="$1"
POPULATION_BASE="$(basename "${POPULATION_DIR}")"
CODE_DIR="/n/fs/grad/pe5/genetic_privacy/predict"
SCRATCH_POP_DIR="/scratch/${USER}/${POPULATION_BASE}"
REMOTE_POP_DIR="/scratch/network/${USER}/${POPULATION_BASE}"
OUTPUT_DIR="/n/fs/grad/pe5/genetic_privacy_output"

echo "Population directory is ${POPULATION_DIR}"

mkdir -p "/scratch/${USER}/db"
mkdir -p "${OUTPUT_DIR}"

cp -r "${POPULATION_DIR}" "${SCRATCH_POP_DIR}"

echo "Dividing up labeled nodes."
srun --mem=4GB "${CODE_DIR}/divide_work.py" "${POPULATION_DIR}" 5 \
     --num_labeled 50 --output_dir "${OUTPUT_DIR}"

for FILENAME in ../${OUTPUT_DIR}/partition_*_labeled_nodes.pickle
do
    NUM="$(basename "$FILENAME" | grep -o -E '[0-9]+')"
    echo "Assigning group ${NUM}"
    srun remote_subset_shared.sh "${REMOTE_POP_DIR}" "$FILENAME" \
         "${OUTPUT_DIR}" "labeled_${NUM}.db"
done
