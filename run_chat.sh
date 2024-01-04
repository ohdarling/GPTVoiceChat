#!/bin/bash

echo "activate virutal env"
source venv/bin/activate

echo "start voice chat"
python voicechat.py snowboy/resources/models/snowboy.umdl
