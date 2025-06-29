import time
import subprocess
import uuid
import re
import json
import mido
from live import Set

# --- MIDI Spec Prompt + Ollama Interaction ----------------------------------------

def regenerate_midi_with_ollama(clip_name, model="llama3:latest"):
    safe_clip_name = re.sub(r"[^\w\s\-]", "", clip_name)[:50]

    prompt = (
        f"Create a chord-based MIDI sketch inspired by the name '{safe_clip_name}'.\n"
        f"Return your response in JSON format ONLY, no explanation or markdown.\n"
        f"Example structure:\n"
        f"{{\n"
        f"  \"tempo_bpm\": 90,\n"
        f"  \"base_note\": 60,\n"
        f"  \"chords\": [\n"
        f"    {{\"intervals\": [0, 4, 7], \"duration_beats\": 1, \"velocity\": 100}},\n"
        f"    {{\"intervals\": [2, 5, 9], \"duration_beats\": 2, \"velocity\": 90}}\n"
        f"  ]\n"
        f"}}\n\n"
        f"Use a musically expressive interpretation of the clip name."
    )

    print(f"🤖 Asking Ollama to compose for: '{clip_name}'...")
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()

# --- Parse Ollama JSON Output -----------------------------------------------------

def parse_midi_spec(text):
    try:
        spec = json.loads(text)
        chords = spec.get("chords", [])
        tempo = spec.get("tempo_bpm", 90)
        base_note = spec.get("base_note", 60)
        return chords, tempo, base_note
    except json.JSONDecodeError as e:
        print(f"⚠️ Could not parse JSON: {e}")
        return [], 90, 60

# --- Create MIDI File -------------------------------------------------------------

def create_midi_from_spec(chords, output_path, tempo_bpm=90, base_note=60):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    ticks_per_beat = mid.ticks_per_beat
    tempo_us_per_beat = mido.bpm2tempo(tempo_bpm)

    track.append(mido.MetaMessage('set_tempo', tempo=tempo_us_per_beat))

    for chord in chords:
        intervals = chord.get("intervals", [])
        duration_beats = chord.get("duration_beats", 1)
        velocity = chord.get("velocity", 100)

        duration_ticks = int(ticks_per_beat * duration_beats)
        chord_notes = [base_note + i for i in intervals]

        # Note ONs
        for i, note in enumerate(chord_notes):
            track.append(mido.Message("note_on", note=note, velocity=velocity, time=0 if i > 0 else 0))

        # Note OFFs
        for i, note in enumerate(chord_notes):
            track.append(mido.Message("note_off", note=note, velocity=0, time=duration_ticks if i == 0 else 0))

    mid.save(output_path)
    return output_path

# --- Monitor and Regenerate -------------------------------------------------------

def monitor_and_regenerate(original_midi_path, poll_interval=1.0, model="llama3:latest"):
    print("🎛️ Monitoring Ableton Live for clip renames...")
    last_names = {}

    while True:
        live_set = Set(scan=True)
        for t_idx, track in enumerate(live_set.tracks):
            for c_idx, clip in enumerate(track.clips):
                if clip is None:
                    continue

                key = (t_idx, c_idx)
                name = clip.name or ""
                if key in last_names and last_names[key] != name:
                    print(f"🎵 Detected rename: '{name}'. Generating new clip...")

                    try:
                        ollama_output = regenerate_midi_with_ollama(name, model=model)
                        chords, tempo, base_note = parse_midi_spec(ollama_output)

                        if not chords:
                            print("⚠️ No valid chords returned. Skipping.")
                        else:
                            safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name)[:30]
                            new_filename = f"regen_{safe_name}_{uuid.uuid4().hex[:6]}.mid"
                            create_midi_from_spec(chords, new_filename, tempo_bpm=tempo, base_note=base_note)
                            print(f"✅ New MIDI saved as: {new_filename}")
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Ollama error: {e}")
                    except Exception as e:
                        print(f"❌ Unexpected error: {e}")

                last_names[key] = name

        time.sleep(poll_interval)

# --- Entry Point ------------------------------------------------------------------

if __name__ == "__main__":
    ORIGINAL_MIDI = "example_chord_progression.mid"  # Doesn't have to be used anymore
    try:
        monitor_and_regenerate(ORIGINAL_MIDI)
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
    except Exception as e:
        print(f"❌ ERROR: {e}")
