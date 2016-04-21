#!/usr/bin/env bash
set -euo pipefail

ulimit -Sv 1000000


POPULATION_DIR="$1"
LABELED_FILENAME="$2"
OUTPUT_DIR="$3"
DB_NAME="$4"
WORK_DIR="/scratch/${USER}"
LOCAL_POPULATION_ROOT="${WORK_DIR}/population"
CODE_DIR="/n/fs/grad/pe5/genetic_privacy/predict"

mkdir -p "${WORK_DIR}"

# Clean population files from previous runs
find  "${LOCAL_POPULATION_ROOT}"\
    -mindepth 1 \
    -maxdepth 1 \
    -type d \
    -not -name "${POPULATION_DIR}" \
    -exec rm -rf {} \;

if [ ! -d "${LOCAL_POPULATION_ROOT}/${POPULATION_DIR}" ]; then
    cp -r "${POPULATION_DIR}" "${LOCAL_POPULATION_ROOT}"
fi

python3 "${CODE_DIR}/parallel_distributions.py" "${POPULATION_DIR}"\
        "${LABELED_FILENAME}" "${WORK_DIR}" --database "${DB_NAME}"

mv "${WORK_DIR}/${DB_NAME}" "${OUTPUT_DIR}/${DB_NAME}_tmp"
mv "${OUTPUT_DIR}/${DB_NAME}_tmp" "${OUTPUT_DIR}/${DB_NAME}"
