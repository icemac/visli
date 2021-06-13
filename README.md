# visli

Cut video files into slices.

## Requirements

* Python 3.9+
* ffmpeg installed and on $PATH

## Help

* python3 visli.py -h

## General usage

* python3 visli.py /path/to/video-file

## Run tests

### Preparation

* python3 -m venv .
* bin/pip install -r dev-requirements.txt

### Actually run the tests

* bin/pytest
