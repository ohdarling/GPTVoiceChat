#!/bin/bash

source venv/bin/activate
pushd EmotiVoice
python -m uvicorn openaiapi:app --reload
popd
