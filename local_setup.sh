#!/bin/bash

local_env=dynamic-routing

if ! conda env list | grep $local_env >/dev/null 2>&1; then
    conda create -n $local_env python=3.10 -y
fi;

source activate $local_env
pip install -r deploy/src/requirements.txt
uvicorn src.main:app