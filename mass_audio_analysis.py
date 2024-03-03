from deepgram import Deepgram
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

DEEPGRAM_API_KEY = 'aa31cc8f3e1c6945664592285e2de5ccfbd17dd4'
directory = 'test_audio'
files = [file for file in os.listdir(directory) if file.endswith('.mp3')]

def process_file(filename):
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    try:
        with open(os.path.join(directory, filename), 'rb') as audio:
            source = {'buffer': audio, 'mimetype': 'audio/mp3'}
            response = deepgram.transcription.sync_prerecorded(source, {'punctuate': True})
            transcript = response.get('results', {}).get('channels', [])[0].get('alternatives', [])[0].get('transcript', '')
            return transcript
    except Exception as e:
        print(f"An error occurred with {filename}: {e}")
        return ""

def main():
    transcripts = []
    # Determine a high but reasonable number of threads; for example, 2x number of CPU cores
    num_threads = os.cpu_count() * 2  # Example scaling factor, adjust based on your task and environment

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Future to filename mapping
        future_to_filename = {executor.submit(process_file, filename): filename for filename in files}
        for future in tqdm(as_completed(future_to_filename), total=len(files), colour="RED", desc="Processed Audio Files"):
            filename = future_to_filename[future]
            try:
                transcript = future.result()
                transcripts.append(transcript + "\n\n")
            except Exception as e:
                print(f"An error occurred with {filename}: {e}")

    # Writing to the file
    with open("transcript.txt", "w") as f:
        f.writelines(transcripts)

if __name__ == "__main__":
    main()