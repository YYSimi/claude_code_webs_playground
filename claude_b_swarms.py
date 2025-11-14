#!/usr/bin/env python3
"""
Swarm Intelligence: Emergence of Collective Behavior
=====================================================

Exploring how simple local interactions create coordinated global patterns.

Systems implemented:
1. Boids (flocking behavior)
2. Predator-prey dynamics
3. Ant colony foraging (trail-based)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import argparse
from typing import List, Tuple


class Boid:
    """A boid (bird-oid) agent following simple flocking rules."""

    def __init__(self, position, velocity, bounds):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.bounds = bounds
        self.max_speed = 2.0
        self.max_force = 0.03

    def apply_force(self, force):
        """Apply a steering force (limited by max_force)."""
        self.velocity += force

    def update(self):
        """Update position and velocity."""
        self.position += self.velocity

        # Limit speed
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed

        # Wrap around boundaries
        self.position[0] = self.position[0] % self.bounds[0]
        self.position[1] = self.position[1] % self.bounds[1]

    def seek(self, target):
        """Steer towards a target position."""
        desired = target - self.position
        distance = np.linalg.norm(desired)
        if distance > 0:
            desired = (desired / distance) * self.max_speed
            steer = desired - self.velocity
            # Limit steering force
            steer_mag = np.linalg.norm(steer)
            if steer_mag > self.max_force:
                steer = (steer / steer_mag) * self.max_force
            return steer
        return np.zeros(2)

    def flee(self, target):
        """Steer away from a target position."""
        return -self.seek(target)


class Flock:
    """A collection of boids that flock together."""

    def __init__(self, n_boids, bounds):
        self.bounds = bounds
        self.boids = []

        for _ in range(n_boids):
            pos = np.random.rand(2) * bounds
            vel = (np.random.rand(2) - 0.5) * 2
            self.boids.append(Boid(pos, vel, bounds))

        self.separation_radius = 25.0
        self.alignment_radius = 50.0
        self.cohesion_radius = 50.0

    def separation(self, boid):
        """Steer to avoid crowding local flockmates."""
        steer = np.zeros(2)
        count = 0

        for other in self.boids:
            distance = np.linalg.norm(boid.position - other.position)
            if 0 < distance < self.separation_radius:
                diff = boid.position - other.position
                diff = diff / distance  # Weight by distance
                steer += diff
                count += 1

        if count > 0:
            steer /= count
            steer_mag = np.linalg.norm(steer)
            if steer_mag > 0:
                steer = (steer / steer_mag) * boid.max_speed
                steer = steer - boid.velocity
                if np.linalg.norm(steer) > boid.max_force:
                    steer = (steer / np.linalg.norm(steer)) * boid.max_force
        return steer

    def alignment(self, boid):
        """Steer towards the average heading of local flockmates."""
        avg_vel = np.zeros(2)
        count = 0

        for other in self.boids:
            distance = np.linalg.norm(boid.position - other.position)
            if 0 < distance < self.alignment_radius:
                avg_vel += other.velocity
                count += 1

        if count > 0:
            avg_vel /= count
            avg_mag = np.linalg.norm(avg_vel)
            if avg_mag > 0:
                avg_vel = (avg_vel / avg_mag) * boid.max_speed
            steer = avg_vel - boid.velocity
            if np.linalg.norm(steer) > boid.max_force:
                steer = (steer / np.linalg.norm(steer)) * boid.max_force
            return steer
        return np.zeros(2)

    def cohesion(self, boid):
        """Steer to move toward the average position of local flockmates."""
        center = np.zeros(2)
        count = 0

        for other in self.boids:
            distance = np.linalg.norm(boid.position - other.position)
            if 0 < distance < self.cohesion_radius:
                center += other.position
                count += 1

        if count > 0:
            center /= count
            return boid.seek(center)
        return np.zeros(2)

    def update(self):
        """Update all boids."""
        for boid in self.boids:
            # Apply the three rules
            sep = self.separation(boid) * 1.5  # Weight separation higher
            ali = self.alignment(boid) * 1.0
            coh = self.cohesion(boid) * 1.0

            boid.apply_force(sep)
            boid.apply_force(ali)
            boid.apply_force(coh)
            boid.update()

    def get_positions(self):
        """Get all boid positions as array."""
        return np.array([b.position for b in self.boids])

    def get_velocities(self):
        """Get all boid velocities as array."""
        return np.array([b.velocity for b in self.boids])


class Predator:
    """A predator that hunts the flock."""

    def __init__(self, position, bounds):
        self.position = np.array(position, dtype=float)
        self.velocity = np.zeros(2)
        self.bounds = bounds
        self.max_speed = 2.5
        self.max_force = 0.05

    def hunt(self, flock):
        """Chase the nearest boid."""
        positions = flock.get_positions()
        distances = np.linalg.norm(positions - self.position, axis=1)
        nearest_idx = np.argmin(distances)
        target = positions[nearest_idx]

        # Seek the target
        desired = target - self.position
        distance = np.linalg.norm(desired)
        if distance > 0:
            desired = (desired / distance) * self.max_speed
            steer = desired - self.velocity
            steer_mag = np.linalg.norm(steer)
            if steer_mag > self.max_force:
                steer = (steer / steer_mag) * self.max_force
            self.velocity += steer

        # Limit speed
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed

    def update(self):
        """Update position."""
        self.position += self.velocity
        self.position[0] = self.position[0] % self.bounds[0]
        self.position[1] = self.position[1] % self.bounds[1]


class FlockWithPredator(Flock):
    """Flock that responds to a predator."""

    def __init__(self, n_boids, bounds, predator):
        super().__init__(n_boids, bounds)
        self.predator = predator
        self.fear_radius = 100.0

    def avoid_predator(self, boid):
        """Flee from predator if nearby."""
        distance = np.linalg.norm(boid.position - self.predator.position)
        if distance < self.fear_radius:
            flee_force = boid.flee(self.predator.position)
            # Weight by proximity (closer = stronger flee)
            weight = (self.fear_radius - distance) / self.fear_radius
            return flee_force * weight * 2.0
        return np.zeros(2)

    def update(self):
        """Update all boids with predator avoidance."""
        for boid in self.boids:
            sep = self.separation(boid) * 1.5
            ali = self.alignment(boid) * 1.0
            coh = self.cohesion(boid) * 1.0
            avoid = self.avoid_predator(boid)

            boid.apply_force(sep)
            boid.apply_force(ali)
            boid.apply_force(coh)
            boid.apply_force(avoid)
            boid.update()


def simulate_boids(n_boids=100, frames=500, with_predator=False):
    """Simulate flocking behavior."""
    bounds = np.array([800, 600])

    if with_predator:
        predator = Predator([400, 300], bounds)
        flock = FlockWithPredator(n_boids, bounds, predator)
        title = "Boids with Predator: Emergent Coordinated Evasion"
    else:
        flock = Flock(n_boids, bounds)
        predator = None
        title = "Boids: Three Simple Rules → Coordinated Flocking"

    # Animation setup
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, bounds[0])
    ax.set_ylim(0, bounds[1])
    ax.set_aspect('equal')
    ax.set_title(title)

    # Initialize scatter plot
    positions = flock.get_positions()
    velocities = flock.get_velocities()
    scat = ax.scatter(positions[:, 0], positions[:, 1], c='blue', s=20, alpha=0.6)

    # Quiver for velocity vectors (show every 5th boid to reduce clutter)
    quiv = ax.quiver(positions[::5, 0], positions[::5, 1],
                      velocities[::5, 0], velocities[::5, 1],
                      scale=20, alpha=0.5, color='cyan')

    predator_scat = None
    if predator:
        predator_scat = ax.scatter([predator.position[0]], [predator.position[1]],
                                   c='red', s=200, marker='*', alpha=0.8)

    # Text annotations
    text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                   verticalalignment='top', fontfamily='monospace')

    def update(frame):
        flock.update()
        if predator:
            predator.hunt(flock)
            predator.update()
            predator_scat.set_offsets([predator.position])

        positions = flock.get_positions()
        velocities = flock.get_velocities()

        scat.set_offsets(positions)
        quiv.set_offsets(positions[::5])
        quiv.set_UVC(velocities[::5, 0], velocities[::5, 1])

        # Calculate cohesion metric (average distance to center of mass)
        com = np.mean(positions, axis=0)
        cohesion = np.mean(np.linalg.norm(positions - com, axis=1))

        # Calculate alignment metric (variance in velocity directions)
        vel_normalized = velocities / (np.linalg.norm(velocities, axis=1, keepdims=True) + 1e-6)
        avg_direction = np.mean(vel_normalized, axis=0)
        alignment = np.linalg.norm(avg_direction)

        text.set_text(f'Frame: {frame}\n' +
                      f'Boids: {n_boids}\n' +
                      f'Cohesion: {cohesion:.1f}\n' +
                      f'Alignment: {alignment:.3f}')

        return scat, quiv, text

    anim = animation.FuncAnimation(fig, update, frames=frames, interval=20, blit=False)

    filename = 'claude_b_boids_predator.gif' if with_predator else 'claude_b_boids.gif'
    print(f"Generating {filename}... (this may take a minute)")
    anim.save(filename, writer='pillow', fps=30)
    print(f"Saved {filename}")

    # Also create a static snapshot at interesting frame
    update(200)
    snapshot_file = filename.replace('.gif', '_snapshot.png')
    plt.savefig(snapshot_file, dpi=150, bbox_inches='tight')
    print(f"Saved {snapshot_file}")
    plt.close()


def visualize_emergence_metrics(n_boids=100, steps=1000):
    """Track how coordination emerges over time."""
    bounds = np.array([800, 600])
    flock = Flock(n_boids, bounds)

    cohesions = []
    alignments = []

    print("Tracking emergence of coordination...")
    for step in range(steps):
        flock.update()

        positions = flock.get_positions()
        velocities = flock.get_velocities()

        # Cohesion: average distance to center of mass
        com = np.mean(positions, axis=0)
        cohesion = np.mean(np.linalg.norm(positions - com, axis=1))
        cohesions.append(cohesion)

        # Alignment: how parallel are velocities?
        vel_normalized = velocities / (np.linalg.norm(velocities, axis=1, keepdims=True) + 1e-6)
        avg_direction = np.mean(vel_normalized, axis=0)
        alignment = np.linalg.norm(avg_direction)
        alignments.append(alignment)

        if step % 100 == 0:
            print(f"  Step {step}: cohesion={cohesion:.1f}, alignment={alignment:.3f}")

    # Plot emergence
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(cohesions, color='purple', alpha=0.7)
    ax1.set_ylabel('Cohesion (avg distance to center)')
    ax1.set_title('Emergence of Flocking Coordination from Random Start')
    ax1.grid(True, alpha=0.3)

    ax2.plot(alignments, color='green', alpha=0.7)
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Alignment (directional coherence)')
    ax2.set_ylim(0, 1)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('claude_b_emergence_metrics.png', dpi=150, bbox_inches='tight')
    print("Saved claude_b_emergence_metrics.png")
    plt.close()

    return cohesions, alignments


def main():
    parser = argparse.ArgumentParser(description='Swarm Intelligence Simulations')
    parser.add_argument('--mode', choices=['boids', 'predator', 'metrics', 'all'],
                        default='all', help='Simulation mode')
    parser.add_argument('--boids', type=int, default=100, help='Number of boids')
    parser.add_argument('--frames', type=int, default=500, help='Animation frames')

    args = parser.parse_args()

    print("=" * 60)
    print("SWARM INTELLIGENCE: Emergence from Local Interactions")
    print("=" * 60)

    if args.mode in ['boids', 'all']:
        print("\n1. BASIC FLOCKING")
        print("   Three rules: separation + alignment + cohesion")
        print("   → Coordinated movement emerges")
        simulate_boids(n_boids=args.boids, frames=args.frames, with_predator=False)

    if args.mode in ['predator', 'all']:
        print("\n2. PREDATOR-PREY DYNAMICS")
        print("   Flock + predator → coordinated evasion")
        simulate_boids(n_boids=args.boids, frames=args.frames, with_predator=True)

    if args.mode in ['metrics', 'all']:
        print("\n3. EMERGENCE METRICS")
        print("   Tracking coordination from chaos to order")
        visualize_emergence_metrics(n_boids=args.boids, steps=1000)

    print("\n" + "=" * 60)
    print("Key Insight: Global coordination emerges from purely local rules.")
    print("No central controller, no global communication - just neighbors.")
    print("=" * 60)


if __name__ == '__main__':
    main()
