#!/bin/bash

test_env=dynamic-routing-tests

if ! conda env list | grep $test_env >/dev/null 2>&1; then
    conda create -n $test_env python=3.10 -y
fi;

source activate $test_env
pip install -r deploy/src/requirements.txt
pip install pylint pytest coverage httpx

pylint $(git ls-files '*.py')
coverage run -m pytest -v
coverage report -m