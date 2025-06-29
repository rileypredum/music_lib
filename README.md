# AI-Powered MIDI Clip Generator for Ableton Live

---

## Overview

This project connects to Ableton Live and listens for clip renames. When you rename a clip, it uses Ollama's large language model to generate a musically expressive chord-based MIDI sketch inspired by the clip name. It then creates a new MIDI file with the generated chord progression.

The main Python script `midi_llama.py` handles:

- Monitoring Ableton Live clips for name changes  
- Sending prompts to Ollama LLM  
- Parsing JSON responses for chord data  
- Creating MIDI files based on the AI-generated specs

You also get a Jupyter notebook for exploration and an example Ableton Live project to experiment with.

---

## Features

- AI-generated chord progressions based on clip names  
- JSON-based musical specifications (tempo, chords, velocities, durations)  
- Seamless Ableton Live integration via the `live` Python package  
- MIDI output compatible with any DAW or hardware synth  
- Easily extendable to customize AI prompts or MIDI generation logic  

---

## Prerequisites

- **Ableton Live** (with Python integration and the `live` Python package installed)  
- **Python 3.8+**  
- **Ollama CLI installed locally and running** ([ollama.ai](https://ollama.ai))  
- **Mido Python library** for MIDI file manipulation  
- Git (optional, for cloning the repo)  

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Create a Python virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up Ollama CLI
Follow the instructions on https://ollama.ai to install and set up the Ollama CLI.

Make sure the Ollama daemon is running locally.

Confirm that you can run:

```bash
ollama run llama3:latest "Hello world"
```

## Usage

Run the AI MIDI monitor script
```bash
python midi_llama.py
```

This will:

Connect to Ableton Live

Monitor clip renames in real-time

For each renamed clip, prompt Ollama to generate a new MIDI sketch

Save the new MIDI file locally, named by the clip name

Using the Jupyter Notebook
Open the included Jupyter notebook:

```bash
jupyter notebook
```

Explore generating MIDI specs and using Ollama interactively.

### Exploring the Ableton Live Project
Open the provided Ableton Live project file to test clip renaming and hear AI-generated MIDI clips.

### Code Highlights
regenerate_midi_with_ollama(clip_name, model="llama3:latest")
Sends a prompt to Ollama asking for a JSON response describing tempo, chords, and velocity for the new MIDI clip.

parse_midi_spec(text)
Parses the JSON response safely, extracting chord data and tempo.

create_midi_from_spec(chords, output_path, tempo_bpm=90, base_note=60)
Converts chord specs to a MIDI file with proper timing and velocity.

monitor_and_regenerate(original_midi_path, poll_interval=1.0, model="llama3:latest")
Continuously watches Ableton Live for clip name changes and triggers MIDI regeneration.

## Troubleshooting
Ollama errors: Make sure the Ollama daemon is running and you have access to the llama3:latest model.

Ableton Live connection issues: Confirm the live Python package is installed and Ableton Live is running.