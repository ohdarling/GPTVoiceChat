#!/bin/bash

function section_start() {
    echo
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo $1
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
}

# setup venv
section_start "Setup virutal env"
python3.10 -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools

# install snowboy dependencies
section_start "brew install dependencies"
brew install swig sox portaudio ffmpeg

section_start "install python packages"
pip install -r requirements.txt

section_start "clone snowboy repo"
git clone https://github.com/Kitt-AI/snowboy --depth=1

section_start "make snowboy lib"
pushd snowboy/swig/Python3
sed -i '' 's/python3-config/python3.10-config/g' Makefile
make
popd
exit 0

# install emotvoice
section_start "clone EmotiVoice repo"
git clone https://github.com/netease-youdao/EmotiVoice.git --depth=1

section_start "clone EmotiVoice model"
pushd EmotiVoice
git clone https://www.modelscope.cn/syq163/WangZeJun.git --depth=1
rm -r outputs
git clone https://www.modelscope.cn/syq163/outputs.git --depth=1
popd

