import os
import shutil
import uuid
import wave
import datetime
from models import Clip, SessionLocal, init_db
from sqlalchemy.exc import IntegrityError
import whisper
import json

UPLOADS_DIR = r"C:\\Users\\SFEco\\OneDrive\\Desktop\\AI\\MyThoughts\\MyThoughtsServer\\upload_server\\uploads"
WAV_DIR = os.path.join("data", "wav")
ASR_DIR = os.path.join("data", "asr")
os.makedirs(WAV_DIR, exist_ok=True)
os.makedirs(ASR_DIR, exist_ok=True)

init_db()

# Transcription task
def transcribe_clip(clip_id):
    session = SessionLocal()
    clip = session.query(Clip).filter_by(clip_id=clip_id).first()
    if not clip:
        print(f"[ASR] No clip found for {clip_id}")
        session.close()
        return
    wav_path = os.path.join(WAV_DIR, f"{clip_id}.wav")
    asr_path = os.path.join(ASR_DIR, f"{clip_id}.json")
    if not os.path.exists(wav_path):
        print(f"[ASR] WAV file missing: {wav_path}")
        session.close()
        return
    print(f"[ASR] Transcribing {wav_path}")
    model = whisper.load_model("medium.en")
    result = model.transcribe(wav_path, word_timestamps=True)
    with open(asr_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    clip.status = "transcribed"
    session.commit()
    print(f"[ASR] Saved transcript to {asr_path}")
    session.close()

def pipeline_process_clip(clip_id):
    print(f"[Pipeline] Processing {clip_id}")
    transcribe_clip(clip_id)
    session = SessionLocal()
    clip = session.query(Clip).filter_by(clip_id=clip_id).first()
    if clip:
        clip.status = "processed"
        session.commit()
        print(f"[Pipeline] {clip_id} marked as processed.")
    session.close()

def scan_and_enqueue():
    session = SessionLocal()
    clips = session.query(Clip).filter_by(status="pending").all()
    for clip in clips:
        print(f"[Enqueue] Found pending clip {clip.clip_id}")
        pipeline_process_clip(clip.clip_id)
        clip.status = "queued"
    session.commit()
    session.close()

def ingest_wavs():
    session = SessionLocal()
    for fname in os.listdir(UPLOADS_DIR):
        if fname.lower().endswith(".wav"):
            src_path = os.path.join(UPLOADS_DIR, fname)
            try:
                # Extract metadata
                with wave.open(src_path, 'rb') as wf:
                    n_channels = wf.getnchannels()
                    framerate = wf.getframerate()
                    n_frames = wf.getnframes()
                    duration = n_frames / float(framerate)
                stat = os.stat(src_path)
                started_at = datetime.datetime.fromtimestamp(stat.st_ctime)
                ended_at = datetime.datetime.fromtimestamp(stat.st_mtime)
                size_bytes = stat.st_size
                # Generate unique clip_id
                clip_id = str(uuid.uuid4())
                # Move/copy file
                dest_path = os.path.join(WAV_DIR, f"{clip_id}.wav")
                shutil.move(src_path, dest_path)
                # Insert into DB
                clip = Clip(
                    clip_id=clip_id,
                    device_id="test_device",  # Placeholder; update as needed
                    started_at=started_at,
                    ended_at=ended_at,
                    duration_ms=int(duration*1000),
                    bytes=size_bytes,
                    status="pending"
                )
                session.add(clip)
                session.commit()
                print(f"Ingested {fname} as {clip_id}")
            except (IntegrityError, Exception) as e:
                session.rollback()
                print(f"Failed to ingest {fname}: {e}")
    session.close()

if __name__ == "__main__":
    ingest_wavs()
    scan_and_enqueue()
