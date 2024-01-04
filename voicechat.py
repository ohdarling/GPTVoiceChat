#!env python

from snowboy.examples.Python3 import snowboydecoder
import sys
import signal
import speech_recognition as sr
import os
from emotivoice_api import emotivoice_api
from openai_api import openai_api

os.environ['KMP_DUPLICATE_LIB_OK']='True'

interrupted = False

import time
from faster_whisper import WhisperModel

# model_size = "large-v3"
whisper_model_size = "small"
whisper_model = WhisperModel(whisper_model_size, device="cpu", compute_type="int8")

def audioRecorderCallback(fname):
    print("converting audio to text")
    r = sr.Recognizer()
    with sr.AudioFile(fname) as source:
        audio = r.record(source)  # read the entire audio file
    # recognize speech using Whisper
        
    start_time = time.time()
    segments, info = whisper_model.transcribe(fname, beam_size=5)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    fulltext = ""

    for segment in segments:
        fulltext += segment.text
        fulltext += "\n"
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    print("time cost", time.time() - start_time)

    ai_msg = openai_api(fulltext)

    emotivoice_api(ai_msg)

    os.remove(fname)


def detectedCallback():
  snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
  print('recording audio...', end='', flush=True)

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python voicechat.py your.model")
    sys.exit(-1)

model = sys.argv[1]
print("using model", model)

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# detector = snowboydecoder.HotwordDetector(model, sensitivity=0.38)
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=detectedCallback,
               audio_recorder_callback=audioRecorderCallback,
               interrupt_check=interrupt_callback,
               sleep_time=0.01)

detector.terminate()




