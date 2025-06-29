import subprocess
import mido
import time
import re
import uuid

class MusicLib:
    @staticmethod
    def generate_chord_progression_midi(
        time_signature: tuple,
        time_division: int,
        root_notes: list,
        vibe: str,
        bars: int = 4,
        filename: str = None,
        model: str = "llama3:latest"
    ):
        valid_divisions = {1, 2, 4, 8, 16}
        if time_division not in valid_divisions:
            raise ValueError(f"time_division must be one of {valid_divisions}")
        if bars < 1:
            raise ValueError("bars must be >= 1")

        if not filename:
            roots_str = "-".join(root_notes)
            vibe_slug = re.sub(r"[^a-z0-9]+", "-", vibe.lower()).strip("-")
            filename = f"chordprog_{time_signature[0]}-{time_signature[1]}_div{time_division}_bars{bars}_roots_{roots_str}_{vibe_slug}.mid"

        print("🎹 Preparing to compose your chord progression...")
        time.sleep(0.5)
        print(f"⏱️  Time signature: {time_signature[0]}/{time_signature[1]}, Note division: 1/{time_division}")
        print(f"🎼  Roots: {', '.join(root_notes)} | Vibe: {vibe} | Bars: {bars}")
        time.sleep(0.5)
        print("🤖 Summoning Ollama to voice the chords creatively...")
        time.sleep(0.5)

        # Add a random UUID comment to make each prompt unique
        nonce = uuid.uuid4().hex[:8]

        prompt = (
            f"Create a unique and creative chord voicing progression for a {vibe} style. "
            f"Use the root notes {root_notes} and express each chord as a list of semitone intervals from the root "
            f"(e.g., [0, 4, 7]). Vary the chord types and extensions. Be inventive — no two runs should sound the same.\n"
            f"Return only one list of intervals per chord root.\n"
            f"# unique_id={nonce}"
        )

        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                check=True
            )
            chords_str = result.stdout.strip()
            print("✅ Ollama delivered the chords! Crafting MIDI...")
        except subprocess.CalledProcessError as e:
            print("❌ Ollama call failed. Please try again.")
            raise RuntimeError(f"Ollama call failed: {e}")

        chord_lines = [line.strip() for line in chords_str.splitlines() if line.strip()]
        chords_intervals = []
        for line in chord_lines:
            nums = [int(n) for n in line.strip("[] ").split(",") if n.strip().isdigit()]
            chords_intervals.append(nums if nums else [0, 4, 7])  # default major triad

        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)

        ticks_per_beat = mid.ticks_per_beat
        note_length_ticks = ticks_per_beat * 4 // time_division

        def note_name_to_midi(note):
            note_map = {"C":0,"C#":1,"D":2,"D#":3,"E":4,"F":5,"F#":6,"G":7,"G#":8,"A":9,"A#":10,"B":11}
            base = note_map.get(note.upper())
            if base is None:
                raise ValueError(f"Invalid root note: {note}")
            return 60 + base  # Middle C (MIDI 60)

        print("🎶 Laying down chords on the digital staff...")
        time_val = 0
        beats_per_bar = time_signature[0]
        chords_per_bar = beats_per_bar * time_division // 4
        total_chords_needed = bars * chords_per_bar

        chord_roots_expanded = (root_notes * ((total_chords_needed // len(root_notes)) + 1))[:total_chords_needed]
        chords_intervals_expanded = (chords_intervals * ((total_chords_needed // len(chords_intervals)) + 1))[:total_chords_needed]

        for root_note, intervals in zip(chord_roots_expanded, chords_intervals_expanded):
            root_midi = note_name_to_midi(root_note)
            chord_notes = [root_midi + i for i in intervals]

            for note in chord_notes:
                track.append(mido.Message("note_on", note=note, velocity=100, time=time_val))
                time_val = 0

            duration = note_length_ticks
            for note in chord_notes:
                track.append(mido.Message("note_off", note=note, velocity=0, time=duration))
                duration = 0

        print("💾 Saving your masterpiece...")
        time.sleep(0.5)
        mid.save(filename)
        print(f"🎉 Done! MIDI file saved as: {filename}")
        return filename
