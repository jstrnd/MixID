from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import os
from subprocess import run
from dotenv import load_dotenv
import requests
from utils import slice_audio

load_dotenv()
app = FastAPI()

class MixRequest(BaseModel):
    url: str

@app.post("/identify")
async def identify_mix(request: MixRequest):
    AUDD_API_KEY = os.getenv("AUDD_API_KEY")
    mix_url = request.url
    output_filename = f"mix_{uuid.uuid4().hex}.mp3"

    command = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "-o", output_filename,
        mix_url
    ]
    result = run(command, capture_output=True)
    if result.returncode != 0:
        return {"error": "Failed to download audio", "details": result.stderr.decode()}

    # Slice audio
    chunks = slice_audio(output_filename)
    results = []
    last_track = None

    for chunk_path, timestamp in chunks:
        with open(chunk_path, 'rb') as f:
            files = {'file': f}
            data = {'api_token': AUDD_API_KEY, 'return': 'apple_music,spotify'}
            response = requests.post('https://api.audd.io/', data=data, files=files)
            result = response.json()
            print(result)  # Optional: keep for debugging

            match = result.get("result")
            if match:
                title = match.get("title")
                artist = match.get("artist")
                if title and artist:
                    current_track = f"{artist} – {title}"
                    if current_track != last_track:
                        results.append({
                            "time": f"{timestamp // 60}:{str(timestamp % 60).zfill(2)}",
                            "track": current_track
                        })
                        last_track = current_track

    return {"tracklist": results}