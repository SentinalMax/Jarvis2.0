import pyaudio
import wave
import numpy as np
import audioop
from collections import deque
import os
import time
from deepgram import Deepgram
# pip3 install deepgram-sdk
import json
import os
import sys
from openai import OpenAI
import openai
#import pyttsx3
from audioplayer import AudioPlayer

# Constants for audio recording
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SILENCE_LIMIT = 2  # Silence limit in seconds. The audio recording will stop if this much silence is detected. (DEFAULT = 2)
PREV_AUDIO = 0.5  # Previous audio length in seconds to keep before the silence detected.
THRESHOLD_BUFFER = 15  # Buffer value to add over the noise floor for the silence threshold (DEFAULT = 10)

# Deepgram

with open('KEYS.json', 'r') as file:
    keys_data = json.load(file)

DEEPGRAM_API_KEY = keys_data['deepgram']
OPENAI_API_KEY = keys_data['openai']

def is_silent(snd_data, silence_threshold):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < silence_threshold

def record_audio():
    # Initialize PyAudio
    # portaudio must be install along with pyaudio for dependancy reasons
    # see (https://stackoverflow.com/questions/33513522/when-installing-pyaudio-pip-cannot-find-portaudio-h-in-usr-local-include)
    
    audio = pyaudio.PyAudio()

    # Choose the device
    # print("Available audio input devices:")
    # for i in range(audio.get_device_count()):
    #     dev = audio.get_device_info_by_index(i)
    #     if dev['maxInputChannels'] > 0:
    #         print(f"{i}: {dev['name']}")

    device_index = 3 #int(input("Please select the device index: "))
    # 3 = 2- USB Audio Device (MIC)
    # 12 = HD Pro Webcam C920 (CAMERA)

    # Start the recording stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, input_device_index=device_index,
                        frames_per_buffer=CHUNK_SIZE)

    print("Recording... Speak into the microphone. Recording will stop after a silence.")
    audio2send = []
    cur_data = ''  # Current chunk of audio data
    rel = RATE / CHUNK_SIZE
    slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
    prev_audio = deque(maxlen=int(PREV_AUDIO * rel))  # Prepend audio from before noise was detected
    started = False
    noise_floor = None  # Initialize noise floor (DEFAULT = None)
    silent_chunks = 0  # Count of consecutive silent chunks
    silence_threshold = 1000  # Start with a default threshold of 1000

    while True:
        cur_data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        snd_data = np.frombuffer(cur_data, dtype=np.int16)
        rms_value = audioop.rms(cur_data, 2)

        if noise_floor is None:
            noise_floor = rms_value
        else:
            noise_floor = min(noise_floor, rms_value)

        silence_threshold = noise_floor + THRESHOLD_BUFFER

        # RMS DEBUG
        #print(f"RMS: {rms_value}, Noise Floor: {noise_floor}, Silence Threshold: {silence_threshold}") 

        # If the RMS value of the current audio chunk is below the silence threshold, increase the silent chunk count
        if rms_value < silence_threshold:
            silent_chunks += 1
            if silent_chunks < int(SILENCE_LIMIT * rel):
                continue
            elif started:
                print("Silence detected, stopping recording.")
                break
        else:
            silent_chunks = 0
            if not started:
                print("Starting recording")
            started = True

        if started:
            audio2send.append(cur_data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    return b''.join(audio2send)


def save_audio(data, path):
    # Save the audio file
    wf = wave.open(path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

def deepgram(PATH_TO_FILE):
    # Initializes the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    # Open the audio file
    with open(PATH_TO_FILE, 'rb') as audio:
        # Set the source with the appropriate mimetype
        source = {'buffer': audio, 'mimetype': 'audio/wav'}
        # Send the audio for transcription
        response = deepgram.transcription.sync_prerecorded(source, {'punctuate': True})
        # Parse the JSON response to extract the transcript
        transcript = response.get('results', {}).get('channels', [])[0].get('alternatives', [])[0].get('transcript', '')

        return transcript
    
# Function to simulate Jarvis-like interaction
def chat_with_jarvis(prompt):

    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=OPENAI_API_KEY,
    )

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are Jarvis from Ironman, a a highly intellegent and knowledgeable yet sassy british assistant. You generally speak between one and three sentences. And you call me sir."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
    )

    # Extract the message content from the response
    message_content = response.choices[0].message.content

    return message_content

# def simple_text_to_speech(message):
#     #engine = pyttsx3.init()
#     engine = pyttsx3.init(driverName='sapi5') 
#     voices = engine.getProperty('voices')

#     engine.setProperty('voice', voices[0].id)

#     engine.say(str(message))
#     engine.runAndWait()

def text_to_speech(message):
    speech_file_path = "audio/speech.mp3"
    if os.path.exists(speech_file_path):
        #File exists, delete it
        os.remove(speech_file_path)
        #print(f"The file {save_path} has been deleted.") #DEBUG
     
    openai.api_key = OPENAI_API_KEY
    response = openai.audio.speech.create(
        model="tts-1",
        voice="fable", #british
        input=str(message)
    )
    response.stream_to_file(speech_file_path)

    return speech_file_path
    

def main():
    while True:
        audio_data = record_audio()
        output_folder = "audio"  # Change this to your actual output folder path
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        #timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "recording.wav" #f"recording-{timestamp}.wav"
        save_path = os.path.join(output_folder, filename)

        if os.path.exists(save_path):
        # File exists, delete it
            os.remove(save_path)
            #print(f"The file {save_path} has been deleted.") #DEBUG

        save_audio(audio_data, save_path)
        #print(f"Recording saved to {save_path}") #DEBUG

        # Deepgram
        prompt = deepgram(save_path)
        print(prompt)

        if prompt.lower() in ("goodbye.", "power down.", "power off.", "shutdown.", "exit.", "goodbye jarvis."):
            speech_file_path = text_to_speech("Goodbye, sir.")
            # Playing the audio file
            audio = AudioPlayer(speech_file_path)
            audio.play(block=True)  # Play without blocking
            time.sleep(2)
            sys.exit()
        else:
            # ChatGPT
            jarvis_response = chat_with_jarvis(prompt=prompt)
            print(jarvis_response)

            ### Text to speech ###
            #simple_text_to_speech(jarvis_response)
            speech_file_path = text_to_speech(jarvis_response)

            # Path to your mp3 file
            audio = AudioPlayer(speech_file_path)
            audio.play(block=True)  # Play without blocking

            # If you want to stop the playback
            # audio.stop()

# This check is necessary to run the main function when the script is executed
if __name__ == "__main__":
    main()
