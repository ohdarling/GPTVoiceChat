#!env python

import requests
import subprocess

# 设置API端点
api_endpoint = "http://127.0.0.1:8000/v1/audio/speech"

# 设置请求标头
headers = {
    "Content-Type": "application/json"
}

# 要转换的文本内容
text_to_convert = "你好，世界"


def emotivoice_api(text_to_convert):
    print("call emotivoice api")
    # 构建JSON请求体
    request_body = {
        "input": text_to_convert,
        "voice": "8051",
        "prompt": "", # 开心 / 悲伤
        "model": "emoti-voice",
        "response_format": "mp3",
        "language": "zh_us"
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
        subprocess.run(['afplay', 'output_audio.mp3'])
    else:
        print("API请求失败：", response.status_code, response.text)

# emotivoice_api(text_to_convert)
        