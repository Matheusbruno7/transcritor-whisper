# Portuguese Audio Transcriber (Whisper)

[🇧🇷 Português](README.md) | 🇺🇸 English

Turns recordings of **meetings, classes and interviews** in Portuguese into timestamped text and `.srt` subtitles, using the **Whisper** speech recognition model (`faster-whisper`). Runs for free on a Google Colab GPU or on your own computer.

## Example

A 35-second clip ([exemplo/reuniao_exemplo.mp3](exemplo/reuniao_exemplo.mp3), synthetic voice) transcribed on a **regular laptop CPU** with the `small` model in 12 seconds. See [`exemplo/`](exemplo/) for the `.txt` and `.srt` outputs.

## How it works

1. **Audio cleanup (ffmpeg):** mono 16 kHz, band-pass to the voice range, background noise reduction and loudness normalization. The original file is never modified.
2. **Transcription (Whisper)**, tuned to avoid the model's most common failures:
   - `vad_filter`: skips silence and noise, where Whisper tends to "hallucinate" sentences;
   - `condition_on_previous_text=False`: one mistake doesn't spill into the next segments;
   - confidence and repetition thresholds to drop suspicious segments;
   - `initial_prompt`: lets you pass names and acronyms from the subject.
3. **Output:** `.txt` with start/end time per segment, plus an `.srt` subtitle file.

## Usage

**Google Colab (best for long recordings):** open [`transcritor_colab.ipynb`](transcritor_colab.ipynb), enable the free T4 GPU, put the audio in a Google Drive folder and run the cells in order.

**Locally** (Python 3.9+, ideally with [ffmpeg](https://ffmpeg.org/)):

```bash
pip install -r requirements.txt
python transcrever.py meeting.mp4                  # large-v3 model (most accurate)
python transcrever.py class.mp3 --modelo small     # faster on CPU
```

Uses CUDA automatically when an NVIDIA GPU is available; otherwise runs on CPU.

## Privacy

Audio is processed **locally** (your computer or your own Colab session). Nothing is sent to third-party transcription services, which matters for meetings with sensitive information.

## How this project was built

Built **together with AI (Anthropic's Claude)**. I defined the need (transcribing long Portuguese meetings accurately without sending audio to third parties) and tested the settings on my own recordings; the AI wrote the code.

## Stack

Python · faster-whisper (Whisper large-v3) · ffmpeg · Google Colab (GPU)

---

**Matheus Bruno de Souza** · [Portfolio](https://matheusbruno7.github.io/portfolio/) · [LinkedIn](https://www.linkedin.com/in/matheusbrsouza)
