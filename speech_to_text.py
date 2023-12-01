from deepgram import Deepgram
import json

DEEPGRAM_API_KEY = 'aa31cc8f3e1c6945664592285e2de5ccfbd17dd4'
PATH_TO_FILE = 'audio/test.wav'

def main():
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
        print(transcript)

main()
