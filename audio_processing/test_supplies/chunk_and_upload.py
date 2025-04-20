from pydub import AudioSegment
import math
import os
import shutil

# Set ffmpeg and ffprobe paths directly (no which)
AudioSegment.converter = r"C:\\Users\\SFEco\\OneDrive\\Desktop\\AI\\ffmpeg-7.1.1-full_build\\ffmpeg-7.1.1-full_build\\bin\\ffmpeg.exe"
AudioSegment.ffprobe   = r"C:\\Users\\SFEco\\OneDrive\\Desktop\\AI\\ffmpeg-7.1.1-full_build\\ffmpeg-7.1.1-full_build\\bin\\ffprobe.exe"

# CONFIGURABLE: Set this to your source folder for long audio files
SOURCE_DIR = "."  # Now points to current folder (test_supplies)
INPUT_FILE = "01. 2012-01-17 - Lecture 1_ History of the Present.mp3"  # Your MP3 file
OUTPUT_DIR = r"C:\\Users\\SFEco\\OneDrive\\Desktop\\AI\\MyThoughts\\MyThoughtsServer\\upload_server\\uploads"    # Output to uploads folder (absolute path)
CHUNK_LENGTH_SEC = 240        # 4 minutes


def chunk_audio_to_uploads(input_path, output_dir=OUTPUT_DIR, chunk_length_sec=CHUNK_LENGTH_SEC):
    audio = AudioSegment.from_file(input_path)  # Accepts mp3, wav, etc.
    total_length_sec = len(audio) / 1000
    num_chunks = math.ceil(total_length_sec / chunk_length_sec)
    basename = os.path.splitext(os.path.basename(input_path))[0]

    os.makedirs(output_dir, exist_ok=True)
    for i in range(num_chunks):
        start_ms = i * chunk_length_sec * 1000
        end_ms = min((i + 1) * chunk_length_sec * 1000, len(audio))
        chunk = audio[start_ms:end_ms]
        out_name = f"{basename}_part{i+1}.wav"
        out_path = os.path.join(output_dir, out_name)
        chunk.export(out_path, format="wav")
        print(f"Chunk {i+1} saved: {out_path}")

if __name__ == "__main__":
    abs_input = os.path.abspath(os.path.join(SOURCE_DIR, INPUT_FILE))
    chunk_audio_to_uploads(abs_input)
