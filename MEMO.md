# 在本地运行大语言模型语音对话

https://twitter.com/lewangx/status/1730172194553286874



# 本地运行 snowboy + faster-whisper

## 运行 snowboy 唤醒词检测

```bash
# 安装命令行依赖 
brew install swig sox

# 安装 portaudio，pyaudio 依赖这个
examples/C++/install_portaudio.sh
brew install portaudio

# 安装 pyaudio，先更新 pip 和 setuptools
pip install --upgrade pip setuptools
pip install pyaudio 

cd swig/Python3
# 修改 Makefile 中的 python3-config 为 python3.10-config
make

cd examples/Python3
# 修改 snowboydecoder.py 中的 from . import snowboydetect 为 import snowboydetect
# 运行 demo
python demo.py resources/models/snowboy.umdl

```

**自定义唤醒词模型制作**

https://snowboy.hahack.com/



## 运行 faster-whisper 语音转文本

使用 https://github.com/SYSTRAN/faster-whisper 项目首页的示例代码，安装完 faster-whisper 之后，直接运行。

**安装 faster-whisper**

```bash
pip install faster-whisper
```

**示例代码**

使用 CPU 运行，将模型改为 small，并修改模型创建参数，运行时会自动下载 small 模型，无需提前下载。

```python
from faster_whisper import WhisperModel

model_size = "small"

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe("audio.mp3", beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
```

## 语音识别

使用 SpeechRecognition 来录音，然后调用 faster-whisper 来做语音识别。

```bash
pip install SpeechRecognition
```

修改 snowboy 的示例代码 demo4.py

```python
#!env python

import snowboydecoder
import sys
import signal
import speech_recognition as sr
import os

"""
This demo file shows you how to use the new_message_callback to interact with
the recorded audio after a keyword is spoken. It uses the speech recognition
library in order to convert the recorded audio into text.

Information on installing the speech recognition library can be found at:
https://pypi.python.org/pypi/SpeechRecognition/
"""


interrupted = False

import time
from faster_whisper import WhisperModel

# model_size = "large-v3"
whisper_model_size = "models/faster-whisper-small"
whisper_model = WhisperModel(whisper_model_size, device="cpu", compute_type="int8")

def audioRecorderCallback(fname):
    print("converting audio to text")
    r = sr.Recognizer()
    with sr.AudioFile(fname) as source:
        audio = r.record(source)  # read the entire audio file
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        start_time = time.time()
        segments, info = whisper_model.transcribe(fname, beam_size=5)

        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        print("cost", time.time() - start_time)
        # print(r.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    os.remove(fname)



def detectedCallback():
  print('recording audio...', end='', flush=True)

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.38)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=detectedCallback,
               audio_recorder_callback=audioRecorderCallback,
               interrupt_check=interrupt_callback,
               sleep_time=0.01)

detector.terminate()
```

## 文本转语音

使用网易开源的 EmotiVoice 来进行文本转语音

**安装依赖**

```bash
pip install torch torchaudio
pip install numpy numba scipy transformers soundfile yacs g2p_en jieba pypinyin
```

**下载 EmotiVoice**

```bash
git clone https://github.com/netease-youdao/EmotiVoice.git --depth=1
```

**安装预训练模型**

需要进入 EmotiVoice 目录

```bash
git clone https://www.modelscope.cn/syq163/WangZeJun.git
rm -rf outputs
git clone https://www.modelscope.cn/syq163/outputs.git
```

**运行 UI 交互界面**

```shell
# 安装依赖
pip install streamlit
# 运行界面
streamlit run demo_page.py --server.port 6006 --logger.level debug
```

**运行类似 OpenAI 的 API**

```bash
# 安装 ffmpeg 用来转 mp3
brew install ffmpeg
# 安装依赖
pip install fastapi pydub uvicorn
# 运行 API
python -m uvicorn openaiapi:app --reload
```

示例代码

```python
#!env python

import requests

# 设置API端点
api_endpoint = "http://127.0.0.1:8000/v1/audio/speech"

# 设置请求标头
headers = {
    "Content-Type": "application/json"
}

# 要转换的文本内容
text_to_convert = "你好，欢迎使用OpenAI的TTS模型。"

# 构建JSON请求体
request_body = {
    "input": text_to_convert,
    "voice": "8051",
    "model": "emoti-voice",
    "language": "zh-us"  # 选择语音风格（可选，根据需要添加）
}

# 发送POST请求
response = requests.post(api_endpoint, json=request_body, headers=headers)

# 解析API响应
if response.status_code == 200:
    # 从响应中获取语音文件
    audio_data = response.content
    # 处理语音数据，例如保存为文件或进行其他处理
    # 将语音数据保存为本地文件
    with open("output_audio.mp3", "wb") as audio_file:
        audio_file.write(audio_data)
    print("语音文件已保存为output_audio.mp3")
else:
    print("API请求失败：", response.status_code, response.text)
```

测试

```bash
python test_emotivoice_api.py && afplay output_audio.mp3
```

## 调用 OpenAI API

安装依赖

```bash
pip install socksio
```

示例代码

```python
from openai import OpenAI
client = OpenAI(
    api_key = ""
)

print("call openai api")

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)

```

