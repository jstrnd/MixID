from pydub import AudioSegment

def slice_audio(file_path, chunk_duration=30):
    audio = AudioSegment.from_mp3(file_path)
    duration_ms = len(audio)

    chunk_paths = []
    for i in range(0, duration_ms, chunk_duration * 1000):
        chunk = audio[i:i + chunk_duration * 1000]
        out_path = f"{file_path}_chunk_{i//1000}.mp3"
        chunk.export(out_path, format="mp3")
        chunk_paths.append((out_path, i // 1000))  # path and time in seconds

    return chunk_paths
