# TTR

This is like a CV version of osu more than DDR, but it's just the name I came up with. There'll be cues for when to tap points on the camera, and you use your finger in the camera to tap them. 


## How to use
This guide is for Windows. No idea how this works on Mac

1. Download UV
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
2. Add it to your PATH:
```bash
source $HOME/.local/bin/env
```
3. Create venv in Python 3.12
```bash
uv venv --python 3.12
```
4. Activate venv
```bash
source .venv/Scripts/activate
```
5. Install requirements
```bash
uv pip install -r requirements.txt
```
6. Add an audio file and a beatmap
7. Run the game:
```bash
python bbr.py <beatmap.json>
```


## Beatmap Format
```json
{
    "audio": <audio-file-name>,
    "offset": <offset froom beginning of audio in ms>,
    "bpm": <bpm of the audio>,
    "eight_counts": [ # Array of arrays of eight counts for the song
        [1, 2, 3, 4],
        [2, 2.5, 7.5, 8],
        ...
    ]
}
```
