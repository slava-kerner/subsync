#!/bin/bash

set -e

python3 -m coverage erase
python3 -m coverage run --branch --source diq -m unittest discover -v tests/
python3 -m coverage report
python3 -m coverage erase
