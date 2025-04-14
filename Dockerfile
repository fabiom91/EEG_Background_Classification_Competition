FROM ubuntu:25.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools

# create a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# set the working directory
WORKDIR /app
# copy the requirements file
COPY requirements.txt .
# activate virtual environment
RUN . /opt/venv/bin/activate
# install the requirements
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN curl https://zenodo.org/records/6587973/files/EDF_format.zip?download=1 -o data/EDF_format.zip && \
    unzip data/EDF_format.zip -d data/ && \
    rm data/EDF_format.zip

RUN curl https://zenodo.org/records/6587973/files/eeg_grades.csv?download=1 -o data/eeg_grades.csv

COPY . .