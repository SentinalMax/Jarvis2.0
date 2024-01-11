import openai
from pydub import AudioSegment
from pydub.playback import play

openai.api_key = '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'

speech_file_path = "audio/speech.mp3"
response = openai.audio.speech.create(
  model="tts-1",
  voice="fable",
  input="The quick brown fox jumped over the lazy dog."
)
response.stream_to_file(speech_file_path)

# Path to your mp3 file
speech_file_path = "audio/speech.mp3"

# Load the audio file
audio = AudioSegment.from_mp3(speech_file_path)

# Play the audio
play(audio)
