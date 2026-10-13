"""
Generate sample audio files for testing the Endless music player.
Creates short synthesized tracks as .wav files with proper metadata.
"""

import wave
import struct
import math
import os
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
from mutagen.wave import WAVE
from PIL import Image, ImageDraw, ImageFont
import io


SAMPLE_RATE = 44100
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_music")

# Each track: (filename, title, artist, album, duration_sec, notes_config)
TRACKS = [
    {
        "filename": "morning_light.wav",
        "title": "Morning Light",
        "artist": "Synthwave Dreams",
        "album": "Dawn Sessions",
        "duration": 15,
        "notes": [(261.63, 0.5), (329.63, 0.5), (392.0, 0.5), (523.25, 1.0)],  # C E G C'
        "color": "#FFB347",
    },
    {
        "filename": "midnight_drive.wav",
        "title": "Midnight Drive",
        "artist": "Neon Pulse",
        "album": "City Lights",
        "duration": 18,
        "notes": [(220.0, 0.6), (277.18, 0.6), (329.63, 0.6), (440.0, 0.8)],  # A C# E A'
        "color": "#7B68EE",
    },
    {
        "filename": "ocean_breeze.wav",
        "title": "Ocean Breeze",
        "artist": "Ambient Shores",
        "album": "Tidal Waves",
        "duration": 20,
        "notes": [(293.66, 0.7), (349.23, 0.7), (440.0, 0.5), (523.25, 0.9)],  # D F A C'
        "color": "#20B2AA",
    },
    {
        "filename": "golden_hour.wav",
        "title": "Golden Hour",
        "artist": "Synthwave Dreams",
        "album": "Dawn Sessions",
        "duration": 12,
        "notes": [(349.23, 0.4), (440.0, 0.4), (523.25, 0.4), (659.25, 1.2)],  # F A C' E'
        "color": "#FFD700",
    },
    {
        "filename": "starfall.wav",
        "title": "Starfall",
        "artist": "Neon Pulse",
        "album": "City Lights",
        "duration": 16,
        "notes": [(196.0, 0.5), (246.94, 0.5), (293.66, 0.5), (392.0, 1.0)],  # G B D G'
        "color": "#FF69B4",
    },
]


def generate_tone(freq, duration, sample_rate=SAMPLE_RATE, volume=0.3):
    """Generate a sine wave tone with fade in/out."""
    n_samples = int(sample_rate * duration)
    samples = []
    fade_samples = min(int(sample_rate * 0.05), n_samples // 4)

    for i in range(n_samples):
        t = i / sample_rate
        # Base sine + soft overtone for warmth
        val = volume * (
            0.7 * math.sin(2 * math.pi * freq * t)
            + 0.2 * math.sin(2 * math.pi * freq * 2 * t)
            + 0.1 * math.sin(2 * math.pi * freq * 3 * t)
        )

        # Fade in
        if i < fade_samples:
            val *= i / fade_samples
        # Fade out
        elif i > n_samples - fade_samples:
            val *= (n_samples - i) / fade_samples

        samples.append(val)

    return samples


def generate_track_audio(track_info):
    """Generate a full track by looping the note pattern."""
    duration = track_info["duration"]
    notes = track_info["notes"]
    all_samples = []

    # Calculate how long one pattern cycle is
    cycle_duration = sum(d for _, d in notes)

    elapsed = 0.0
    while elapsed < duration:
        for freq, note_dur in notes:
            remaining = duration - elapsed
            actual_dur = min(note_dur, remaining)
            if actual_dur <= 0:
                break
            all_samples.extend(generate_tone(freq, actual_dur))
            elapsed += actual_dur

    # Final fade out (last 1 second)
    fade_len = min(SAMPLE_RATE, len(all_samples))
    for i in range(fade_len):
        all_samples[-(i + 1)] *= i / fade_len

    return all_samples


def create_cover_art(title, color, size=(300, 300)):
    """Generate a simple gradient cover art image."""
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)

    # Parse hex color
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    # Draw gradient background
    for y in range(size[1]):
        ratio = y / size[1]
        cr = int(r * (1 - ratio * 0.5))
        cg = int(g * (1 - ratio * 0.5))
        cb = int(b * (1 - ratio * 0.5))
        draw.line([(0, y), (size[0], y)], fill=(cr, cg, cb))

    # Draw some decorative circles
    for i in range(3):
        cx = size[0] // 2 + (i - 1) * 60
        cy = size[1] // 2
        radius = 30 + i * 10
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=(255, 255, 255, 180),
            width=2,
        )

    # Add title text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except (OSError, IOError):
        font = ImageFont.load_default()

    # Center the text
    bbox = draw.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size[0] - tw) // 2
    ty = size[1] - th - 30
    draw.text((tx, ty), title, fill=(255, 255, 255), font=font)

    return img


def save_wav(samples, filepath):
    """Save samples as a WAV file."""
    with wave.open(filepath, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(SAMPLE_RATE)
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            wav.writeframes(struct.pack("<h", int(clamped * 32767)))


def add_metadata(filepath, track_info, cover_img):
    """Add ID3 metadata and cover art to the WAV file."""
    audio = WAVE(filepath)

    # Add ID3 tags
    audio.add_tags()
    audio.tags.add(TIT2(encoding=3, text=track_info["title"]))
    audio.tags.add(TPE1(encoding=3, text=track_info["artist"]))
    audio.tags.add(TALB(encoding=3, text=track_info["album"]))

    # Add cover art
    buf = io.BytesIO()
    cover_img.save(buf, format="PNG")
    audio.tags.add(
        APIC(
            encoding=3,
            mime="image/png",
            type=3,  # Cover (front)
            desc="Cover",
            data=buf.getvalue(),
        )
    )

    audio.save()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("🎵 Generating test music files...\n")

    for track in TRACKS:
        filepath = os.path.join(OUTPUT_DIR, track["filename"])

        # Generate audio
        print(f"  ♪ {track['title']} by {track['artist']} ({track['duration']}s)")
        samples = generate_track_audio(track)
        save_wav(samples, filepath)

        # Generate cover art & add metadata
        cover = create_cover_art(track["title"], track["color"])
        add_metadata(filepath, track, cover)

    print(f"\n✅ Created {len(TRACKS)} test tracks in: {OUTPUT_DIR}")
    print("   Open the Music Player and add the 'test_music' folder to try it out!")


if __name__ == "__main__":
    main()
