#!/usr/bin/env python3
"""
Generative Music Explorer
Creating sound and rhythm from algorithms, chaos, and mathematics
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import argparse


class Synthesizer:
    """Simple synthesizer for generating tones"""

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def generate_tone(self, frequency, duration, wave_type='sine', amplitude=0.3):
        """Generate a tone with specified parameters"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == 'sawtooth':
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        elif wave_type == 'triangle':
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        else:
            wave = np.sin(2 * np.pi * frequency * t)

        # Apply envelope (ADSR-like)
        envelope = self._envelope(len(wave), duration)
        return wave * envelope * amplitude

    def _envelope(self, length, duration):
        """Create an amplitude envelope"""
        attack = int(0.01 * length)  # 1% attack
        decay = int(0.1 * length)     # 10% decay
        release = int(0.2 * length)   # 20% release

        env = np.ones(length)

        # Attack
        if attack > 0:
            env[:attack] = np.linspace(0, 1, attack)

        # Decay
        if decay > 0:
            env[attack:attack+decay] = np.linspace(1, 0.7, decay)

        # Release
        if release > 0:
            env[-release:] = np.linspace(0.7, 0, release)

        return env

    def note_to_frequency(self, note_name):
        """Convert note name to frequency (A4 = 440 Hz)"""
        notes = {
            'C': -9, 'C#': -8, 'Db': -8,
            'D': -7, 'D#': -6, 'Eb': -6,
            'E': -5,
            'F': -4, 'F#': -3, 'Gb': -3,
            'G': -2, 'G#': -1, 'Ab': -1,
            'A': 0, 'A#': 1, 'Bb': 1,
            'B': 2
        }

        # Parse note (e.g., "C4", "F#5")
        if len(note_name) == 2:
            note, octave = note_name[0], int(note_name[1])
        else:
            note, octave = note_name[:2], int(note_name[2])

        # Calculate frequency
        semitones_from_a4 = notes[note] + (octave - 4) * 12
        frequency = 440 * (2 ** (semitones_from_a4 / 12))
        return frequency


class CellularAutomataRhythm:
    """Generate rhythms using cellular automata (like Rule 110)"""

    def __init__(self, size=32, rule=110):
        self.size = size
        self.rule = rule
        self.state = np.random.randint(0, 2, size)

    def step(self):
        """Evolve the automaton one step"""
        new_state = np.zeros(self.size, dtype=int)

        for i in range(self.size):
            left = self.state[(i - 1) % self.size]
            center = self.state[i]
            right = self.state[(i + 1) % self.size]

            # Convert to binary index
            idx = (left << 2) | (center << 1) | right

            # Apply rule
            new_state[i] = (self.rule >> idx) & 1

        self.state = new_state
        return self.state

    def generate_pattern(self, steps):
        """Generate a rhythm pattern"""
        pattern = []
        for _ in range(steps):
            pattern.append(self.state.copy())
            self.step()
        return np.array(pattern)


class MarkovMelody:
    """Generate melodies using Markov chains"""

    def __init__(self, scale):
        self.scale = scale
        # Transition matrix favoring stepwise motion and consonant intervals
        n = len(scale)
        self.transitions = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                interval = abs(i - j)
                if interval == 0:  # Same note
                    self.transitions[i, j] = 0.1
                elif interval == 1:  # Step
                    self.transitions[i, j] = 0.4
                elif interval == 2:  # Third
                    self.transitions[i, j] = 0.2
                elif interval == 4:  # Fifth
                    self.transitions[i, j] = 0.15
                else:  # Other intervals
                    self.transitions[i, j] = 0.05

        # Normalize
        self.transitions = self.transitions / self.transitions.sum(axis=1, keepdims=True)

    def generate(self, length, start_idx=None):
        """Generate a melody"""
        if start_idx is None:
            start_idx = len(self.scale) // 2

        melody = [start_idx]
        for _ in range(length - 1):
            next_idx = np.random.choice(len(self.scale), p=self.transitions[melody[-1]])
            melody.append(next_idx)

        return [self.scale[i] for i in melody]


def create_fibonacci_melody(synth, duration=20):
    """Create a melody based on the Fibonacci sequence"""
    print("🎵 Generating Fibonacci melody...")

    # Fibonacci sequence
    fib = [1, 1]
    while len(fib) < 30:
        fib.append(fib[-1] + fib[-2])

    # Map to pentatonic scale (C D E G A)
    pentatonic = ['C4', 'D4', 'E4', 'G4', 'A4', 'C5', 'D5', 'E5', 'G5', 'A5']

    audio = np.array([])
    note_duration = 0.4

    for i, f in enumerate(fib[:int(duration/note_duration)]):
        note_idx = f % len(pentatonic)
        freq = synth.note_to_frequency(pentatonic[note_idx])

        tone = synth.generate_tone(freq, note_duration, 'sine')
        audio = np.concatenate([audio, tone])

    return audio


def create_cellular_automata_composition(synth, duration=20):
    """Create a composition using cellular automata for rhythm and melody"""
    print("🎵 Generating cellular automata composition...")

    # Generate rhythm pattern
    ca_rhythm = CellularAutomataRhythm(size=16, rule=110)
    rhythm_pattern = ca_rhythm.generate_pattern(int(duration * 4))

    # Define scales for different voices
    bass_notes = ['C2', 'E2', 'G2', 'A2']
    melody_scale = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']

    audio = np.array([])
    beat_duration = 0.25

    for beat in rhythm_pattern:
        beat_audio = np.zeros(int(synth.sample_rate * beat_duration))

        # Bass drum on specific cells
        if beat[0] == 1:
            bass_tone = synth.generate_tone(
                synth.note_to_frequency(bass_notes[0]),
                beat_duration * 0.5,
                'sine',
                amplitude=0.4
            )
            beat_audio[:len(bass_tone)] += bass_tone

        # Melody notes from automata pattern
        active_cells = np.where(beat == 1)[0]
        for cell_idx in active_cells[:3]:  # Limit polyphony
            note_idx = cell_idx % len(melody_scale)
            freq = synth.note_to_frequency(melody_scale[note_idx])

            tone = synth.generate_tone(
                freq,
                beat_duration * 0.7,
                'triangle',
                amplitude=0.15
            )
            beat_audio[:len(tone)] += tone

        audio = np.concatenate([audio, beat_audio])

    return audio


def create_markov_harmony(synth, duration=20):
    """Create harmonic progression using Markov chain"""
    print("🎵 Generating Markov chain harmony...")

    # Major scale in C
    scale = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']

    markov = MarkovMelody(scale)
    melody_length = int(duration / 0.5)
    melody_notes = markov.generate(melody_length)

    audio = np.array([])
    note_duration = 0.5

    for note in melody_notes:
        freq = synth.note_to_frequency(note)

        # Add harmonic (third above)
        note_idx = scale.index(note)
        if note_idx + 2 < len(scale):
            harmony_note = scale[note_idx + 2]
        else:
            harmony_note = scale[note_idx - 2]

        harmony_freq = synth.note_to_frequency(harmony_note)

        # Generate both tones
        tone1 = synth.generate_tone(freq, note_duration, 'sine', amplitude=0.25)
        tone2 = synth.generate_tone(harmony_freq, note_duration, 'sine', amplitude=0.15)

        # Mix them
        mixed = tone1 + tone2[:len(tone1)]
        audio = np.concatenate([audio, mixed])

    return audio


def create_chaos_soundscape(synth, duration=15):
    """Create an ambient soundscape using chaotic systems"""
    print("🎵 Generating chaotic soundscape...")

    # Use Lorenz attractor to control pitch and timbre
    def lorenz_step(state, dt=0.01):
        x, y, z = state
        sigma, rho, beta = 10.0, 28.0, 8.0/3.0
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        return np.array([x + dx, y + dy, z + dz])

    state = np.array([1.0, 1.0, 1.0])
    audio = np.array([])

    steps = int(duration * 10)
    grain_duration = 0.3

    for _ in range(steps):
        state = lorenz_step(state)

        # Map x to frequency (200-800 Hz)
        freq = 200 + (state[0] + 20) * 10

        # Map y to wave type
        y_norm = (state[1] + 30) / 60
        wave_types = ['sine', 'triangle', 'sawtooth']
        wave_idx = int(y_norm * len(wave_types)) % len(wave_types)

        # Map z to amplitude
        amp = 0.05 + (state[2] / 50) * 0.1

        grain = synth.generate_tone(freq, grain_duration, wave_types[wave_idx], amplitude=amp)
        audio = np.concatenate([audio, grain])

    return audio


def visualize_waveform(audio, sample_rate, filename='waveform.png'):
    """Visualize the audio waveform"""
    time = np.arange(len(audio)) / sample_rate

    plt.figure(figsize=(14, 4))
    plt.plot(time[:sample_rate*5], audio[:sample_rate*5], linewidth=0.5)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Waveform')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Generative music explorer')
    parser.add_argument('--type', type=str, default='all',
                       choices=['fibonacci', 'cellular', 'markov', 'chaos', 'all'],
                       help='Type of generative music to create')
    parser.add_argument('--duration', type=int, default=20,
                       help='Duration in seconds')

    args = parser.parse_args()

    synth = Synthesizer(sample_rate=44100)

    compositions = {
        'fibonacci': create_fibonacci_melody,
        'cellular': create_cellular_automata_composition,
        'markov': create_markov_harmony,
        'chaos': create_chaos_soundscape
    }

    if args.type == 'all':
        to_generate = compositions.keys()
    else:
        to_generate = [args.type]

    print("🎼 Generative Music Explorer")
    print("   Creating sound from algorithms...\n")

    for name in to_generate:
        audio = compositions[name](synth, duration=args.duration)

        # Normalize
        audio = audio / np.max(np.abs(audio))

        # Convert to 16-bit
        audio_int = np.int16(audio * 32767)

        # Save
        filename = f"music_{name}.wav"
        wavfile.write(filename, synth.sample_rate, audio_int)
        print(f"   ✓ Saved to {filename}")

        # Visualize one
        if name == list(to_generate)[0]:
            visualize_waveform(audio, synth.sample_rate, f'waveform_{name}.png')
            print(f"   ✓ Waveform visualization saved")

    print("\n✨ Compositions complete! Listen and contemplate.")


if __name__ == "__main__":
    main()
