import pyaudio
import wave
import requests
import json
import subprocess
import os
from config import COMMANDS

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output"


def record():

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    #print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    #print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME + ".wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    subprocess.call(['flac', '--best', '-f', '-s', 'output.wav'])

    with open(WAVE_OUTPUT_FILENAME + '.flac', 'rb') as f:
        speech = f.read()

    os.remove(WAVE_OUTPUT_FILENAME + '.wav')
    os.remove(WAVE_OUTPUT_FILENAME + '.flac')

    return speech


def transcribe(speech):
    url = 'https://www.google.com'
    path = '/speech-api/v2/recognize'
    params = {
        'output': 'json',
        'key': 'AIzaSyCnl6MRydhw_5fLXIdASxkLJzcJh5iX0M4',
        'lang': 'en-US'
    }
    headers = {
        'Content-type': 'audio/x-flac; rate=44100',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'
    }
    r = requests.post(url + path, speech, params=params, headers=headers)

    if r.text.split('\n')[0] == u'{"result":[]}':
        data = json.loads(r.text.split('\n')[1])
    else:
        data = json.loads(r.text.split('\n')[0])

    return data


def detect_command(data):
    match = False
    for alt in data['result'][0]['alternative']:
        for com in COMMANDS.keys():
            if alt['transcript'] == com:
                match = True
                for step in COMMANDS[com]:
                    subprocess.call(step)
                break
        if match:
            break
