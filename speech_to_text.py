from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
import json
from config import API_KEY, AUDIO_FILE_PATH

print("audio file path")
def generate_transcript_speaker_diarization():
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(API_KEY)

        with open(AUDIO_FILE_PATH, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-3",
            smart_format=True,
            diarize=True,
            summarize=True
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

        print("speech to text generation started............")
        return extract_speaker_segments(json.loads(response.to_json()))

    except Exception as e:
        print(f"Exception: {e}")

def extract_speaker_segments(response):
    try:
        # Access the channels field
        channels = response["results"]["channels"]
        speaker_segments = []

        for channel in channels:
            for alternative in channel["alternatives"]:
                paragraphs = alternative.get("paragraphs", {}).get("paragraphs", [])
                summary_texts = [summary["summary"] for summary in alternative.get("summaries", [])]  # Extract summaries

                for paragraph in paragraphs:
                    speaker = f"Speaker{paragraph.get('speaker', 'Unknown') + 1}"  # Convert 0-based to 1-based index
                    start_time = round(paragraph["start"], 2)
                    end_time = round(paragraph["end"], 2)

                    # Combine all sentences for this paragraph
                    combined_text = " ".join([sentence["text"] for sentence in paragraph["sentences"]])

                    # Format the result as desired
                    speaker_segments.append({
                        "speaker": speaker,
                        "start_time": start_time,
                        "end_time": end_time,
                        "text": combined_text
                    })

        # Sort segments by start_time in descending order
        speaker_segments.sort(key=lambda x: x["start_time"], reverse=True)

        # Format output
        formatted_segments = [
            f"{seg['speaker']} (Start: {seg['start_time']}s, End: {seg['end_time']}s): {seg['text']}"
            for seg in speaker_segments
        ]

        print("Speech-to-text generation process complete.....")
        return formatted_segments, summary_texts

    except Exception as e:
        print(f"Error extracting transcript: {e}")
        return []
