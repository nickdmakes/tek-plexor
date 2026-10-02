"""Small deterministic audio fixtures; no network or copyrighted media."""
import math
import struct
import wave
from pathlib import Path


def write_tone(path: Path, seconds=0.2, channels=2):
    path.parent.mkdir(parents=True, exist_ok=True)
    samples = [int(8000 * math.sin(2 * math.pi * 440 * n / 48000))
               for n in range(int(seconds * 48000))]
    with wave.open(str(path), 'wb') as audio:
        audio.setparams((channels, 2, 48000, 0, 'NONE', 'not compressed'))
        interleaved = [sample for sample in samples for _ in range(channels)]
        audio.writeframes(struct.pack('<' + 'h' * len(interleaved), *interleaved))
    return path
