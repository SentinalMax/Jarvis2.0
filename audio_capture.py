import pyaudio
import wave
import numpy as np
import audioop
from collections import deque
import os
import time

# Constants for audio recording
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SILENCE_LIMIT = 5  # Silence limit in seconds. The audio recording will stop if this much silence is detected.
PREV_AUDIO = 0.5  # Previous audio length in seconds to keep before the silence detected.
THRESHOLD_BUFFER = 10  # Buffer value to add over the noise floor for the silence threshold

def is_silent(snd_data, silence_threshold):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < silence_threshold

def record_audio():
    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Choose the device
    # print("Available audio input devices:")
    # for i in range(audio.get_device_count()):
    #     dev = audio.get_device_info_by_index(i)
    #     if dev['maxInputChannels'] > 0:
    #         print(f"{i}: {dev['name']}")

    device_index = 1 #int(input("Please select the device index: "))

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
    noise_floor = None  # Initialize noise floor
    silent_chunks = 0  # Count of consecutive silent chunks
    silence_threshold = 1000  # Start with a default threshold

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

def main():
    audio_data = record_audio()
    output_folder = "audio"  # Change this to your actual output folder path
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"recording-{timestamp}.wav"
    save_path = os.path.join(output_folder, filename)
    save_audio(audio_data, save_path)
    print(f"Recording saved to {save_path}")

# This check is necessary to run the main function when the script is executed
if __name__ == "__main__":
    main()
