from speech_to_text import generate_transcript_speaker_diarization
from fastapi import UploadFile
import shutil
from config import config
from pydub import AudioSegment
from pydub import AudioSegment

def process_audio_file(audio_file: UploadFile):
    save_audio_file(audio_file=audio_file)
    print("audio file saved //////////////\n")
    return generate_transcript_speaker_diarization()
        
def save_audio_file(audio_file):
    with open(config.AUDIO_FILE_PATH, "wb") as f:
        shutil.copyfileobj(audio_file.file, f)


def get_audio_duration():
    audio = AudioSegment.from_file(config.AUDIO_FILE_PATH)
    duration_seconds = len(audio) / 1000  # Total duration in seconds

    # Calculate hours, minutes, and seconds
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)
    
    # Build the duration string dynamically based on non-zero values
    duration_parts = [ f"{hours:02}", f"{minutes:02}", f"{seconds:02}" ]
    print("duration = ", ":".join(duration_parts))
    # Combine and return the duration string
    return ":".join(duration_parts)
