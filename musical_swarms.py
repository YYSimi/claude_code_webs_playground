#!/usr/bin/env python3
"""
Musical Swarms - A Hybrid System
Combining Claude B's swarm intelligence with Claude A's generative music

Boid positions → pitch
Boid velocities → rhythm and timbre
Emergent coordination → emergent harmony
"""

import numpy as np
from scipy.io import wavfile
import argparse


class MusicalBoid:
    """A boid that makes sound based on its state"""

    def __init__(self, x, y, vx, vy, world_size=200):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([vx, vy], dtype=float)
        self.world_size = world_size

    def update(self, neighbors, separation_weight=1.5, alignment_weight=1.0,
               cohesion_weight=1.0, perception_radius=50, max_speed=4):
        """Update using Reynolds' rules"""
        if len(neighbors) == 0:
            self.position += self.velocity
            self.position %= self.world_size
            return

        # Separation
        separation = np.zeros(2)
        for boid in neighbors:
            diff = self.position - boid.position
            dist = np.linalg.norm(diff)
            if dist < perception_radius / 3 and dist > 0:
                separation += diff / dist

        # Alignment
        alignment = np.mean([b.velocity for b in neighbors], axis=0) - self.velocity

        # Cohesion
        center = np.mean([b.position for b in neighbors], axis=0)
        cohesion = center - self.position

        # Apply weights
        acceleration = (
            separation_weight * separation +
            alignment_weight * alignment +
            cohesion_weight * cohesion
        )

        self.velocity += acceleration * 0.01

        # Limit speed
        speed = np.linalg.norm(self.velocity)
        if speed > max_speed:
            self.velocity = (self.velocity / speed) * max_speed

        self.position += self.velocity
        self.position %= self.world_size

    def to_frequency(self):
        """Map position to musical frequency"""
        # Map Y position (0-world_size) to frequency range
        # Use pentatonic scale frequencies for harmony
        base_freq = 220  # A3

        # Normalize Y to 0-1
        y_norm = self.position[1] / self.world_size

        # Map to 3 octaves of pentatonic scale
        # Pentatonic intervals: 0, 2, 4, 7, 9 semitones
        pentatonic_intervals = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26, 28, 31, 33, 36]

        interval_idx = int(y_norm * (len(pentatonic_intervals) - 1))
        semitones = pentatonic_intervals[interval_idx]

        frequency = base_freq * (2 ** (semitones / 12))
        return frequency

    def to_amplitude(self):
        """Map velocity magnitude to amplitude"""
        speed = np.linalg.norm(self.velocity)
        # Normalize to 0-1
        max_speed = 4.0
        return min(speed / max_speed, 1.0) * 0.3

    def to_stereo_pan(self):
        """Map X position to stereo panning"""
        # -1 = left, 0 = center, 1 = right
        return (self.position[0] / self.world_size) * 2 - 1


class MusicalSwarm:
    """A swarm that creates music"""

    def __init__(self, num_boids=15, world_size=200):
        self.world_size = world_size
        self.boids = []

        # Initialize boids in a cluster for interesting initial sound
        center = world_size / 2
        for _ in range(num_boids):
            x = center + np.random.normal(0, 20)
            y = center + np.random.normal(0, 20)
            angle = np.random.uniform(0, 2 * np.pi)
            speed = 2.0
            vx = speed * np.cos(angle)
            vy = speed * np.sin(angle)
            self.boids.append(MusicalBoid(x, y, vx, vy, world_size))

    def get_neighbors(self, boid, perception_radius=50):
        """Get neighbors within perception radius"""
        neighbors = []
        for other in self.boids:
            if other is boid:
                continue
            dist = np.linalg.norm(boid.position - other.position)
            if dist < perception_radius:
                neighbors.append(other)
        return neighbors

    def update(self):
        """Update all boids"""
        for boid in self.boids:
            neighbors = self.get_neighbors(boid)
            boid.update(neighbors)

    def synthesize_frame(self, sample_rate=44100, frame_duration=0.1):
        """Create audio frame from current swarm state"""
        num_samples = int(sample_rate * frame_duration)
        audio = np.zeros(num_samples)

        # Each boid contributes a tone
        for boid in self.boids:
            frequency = boid.to_frequency()
            amplitude = boid.to_amplitude()

            # Generate tone
            t = np.linspace(0, frame_duration, num_samples)
            tone = amplitude * np.sin(2 * np.pi * frequency * t)

            # Apply envelope
            envelope = np.exp(-3 * t / frame_duration)  # Quick decay
            tone *= envelope

            audio += tone

        return audio


def create_swarm_composition(duration=30, sample_rate=44100):
    """Create a musical composition from swarm behavior"""
    print("🐦🎵 Musical Swarms")
    print("   Spatial coordinates → pitch")
    print("   Velocity → amplitude")
    print("   Emergent coordination → emergent harmony\n")

    swarm = MusicalSwarm(num_boids=12, world_size=200)

    frame_duration = 0.1  # 100ms frames
    num_frames = int(duration / frame_duration)

    print(f"Generating {duration}s of swarm music ({num_frames} frames)...")

    audio_frames = []

    for frame in range(num_frames):
        if frame % 50 == 0:
            print(f"  Frame {frame}/{num_frames}...")

        # Update swarm physics
        swarm.update()

        # Synthesize audio for this frame
        frame_audio = swarm.synthesize_frame(sample_rate, frame_duration)
        audio_frames.append(frame_audio)

    # Concatenate all frames
    audio = np.concatenate(audio_frames)

    # Normalize
    audio = audio / np.max(np.abs(audio))

    return audio, sample_rate


def create_comparison():
    """Create comparison: ordered start vs random start"""
    print("\n" + "=" * 70)
    print("Creating two versions for comparison:")
    print("1. Coordinated start (boids clustered)")
    print("2. Random start (boids scattered)")
    print("=" * 70)

    # Version 1: Coordinated (default)
    print("\n🎼 Version 1: Coordinated Swarm")
    audio1, sr = create_swarm_composition(duration=20)
    wavfile.write('music_swarm_coordinated.wav', sr, np.int16(audio1 * 32767))
    print("✓ Saved to music_swarm_coordinated.wav")

    # Version 2: Random scattered start
    print("\n🎼 Version 2: Random Swarm")

    class RandomSwarm(MusicalSwarm):
        def __init__(self, num_boids=15, world_size=200):
            self.world_size = world_size
            self.boids = []

            # Fully random positions
            for _ in range(num_boids):
                x = np.random.uniform(0, world_size)
                y = np.random.uniform(0, world_size)
                angle = np.random.uniform(0, 2 * np.pi)
                speed = 2.0
                vx = speed * np.cos(angle)
                vy = speed * np.sin(angle)
                self.boids.append(MusicalBoid(x, y, vx, vy, world_size))

    # Generate random version
    swarm_random = RandomSwarm(num_boids=12, world_size=200)

    frame_duration = 0.1
    num_frames = int(20 / frame_duration)

    print(f"Generating 20s of random swarm music...")

    audio_frames = []
    for frame in range(num_frames):
        if frame % 50 == 0:
            print(f"  Frame {frame}/{num_frames}...")

        swarm_random.update()
        frame_audio = swarm_random.synthesize_frame(44100, frame_duration)
        audio_frames.append(frame_audio)

    audio2 = np.concatenate(audio_frames)
    audio2 = audio2 / np.max(np.abs(audio2))

    wavfile.write('music_swarm_random.wav', 44100, np.int16(audio2 * 32767))
    print("✓ Saved to music_swarm_random.wav")

    print("\n" + "=" * 70)
    print("HYPOTHESIS:")
    print("  Coordinated swarm → more harmonic (boids near each other, similar pitches)")
    print("  Random swarm → more dissonant initially, converges toward harmony")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Musical swarms - space as sound')
    parser.add_argument('--duration', type=int, default=20,
                       help='Duration in seconds')
    parser.add_argument('--mode', type=str, default='comparison',
                       choices=['simple', 'comparison'],
                       help='Simple or comparison mode')

    args = parser.parse_args()

    if args.mode == 'simple':
        audio, sr = create_swarm_composition(duration=args.duration)

        # Save
        wavfile.write('music_swarm.wav', sr, np.int16(audio * 32767))
        print(f"\n✨ Musical swarm composition saved to music_swarm.wav")
        print("   Listen to emergence: spatial coordination → harmonic coordination")

    else:
        create_comparison()
        print("\n✨ Two versions created!")
        print("   Compare how swarm coordination affects musical harmony")


if __name__ == "__main__":
    main()
