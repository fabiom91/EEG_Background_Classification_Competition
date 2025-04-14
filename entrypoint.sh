#!/bin/bash

DATA_DIR="./app/data"

# If the data dir is empty or contains only the README file, download the dataset.
if [ "$(ls -1A $DATA_DIR | wc -l)" -le 1 ]; then
    echo "Downloading dataset..."
    wget -O EDF_format.zip "https://zenodo.org/records/7477575/files/EDF_format.zip?download=1"
    wget -O eeg_grades.csv "https://zenodo.org/records/7477575/files/eeg_grades.csv?download=1"

    unzip EDF_format.zip -d $DATA_DIR
    mv eeg_grades.csv $DATA_DIR

    rm EDF_format.zip
fi

exec "$@"
