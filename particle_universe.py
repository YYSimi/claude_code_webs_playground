#!/usr/bin/env python3
"""
Particle Universe
A physics simulation exploring emergent behavior through simple forces
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass
from typing import List
import argparse


@dataclass
class Particle:
    """A particle with position, velocity, and properties"""
    position: np.ndarray
    velocity: np.ndarray
    mass: float
    charge: float = 0.0  # For electromagnetic-like forces
    color: tuple = (0.5, 0.5, 1.0)


class ParticleSystem:
    """A system of interacting particles"""

    def __init__(self, num_particles=100, world_size=100):
        self.world_size = world_size
        self.particles: List[Particle] = []
        self.time = 0
        self.dt = 0.1

        # Initialize particles
        for _ in range(num_particles):
            pos = np.random.uniform(0, world_size, 2)
            vel = np.random.normal(0, 0.5, 2)
            mass = np.random.uniform(0.5, 2.0)
            charge = np.random.choice([-1, 0, 1])

            # Color by charge
            if charge > 0:
                color = (1.0, 0.3, 0.3)  # Red for positive
            elif charge < 0:
                color = (0.3, 0.3, 1.0)  # Blue for negative
            else:
                color = (0.5, 0.5, 0.5)  # Gray for neutral

            self.particles.append(Particle(pos, vel, mass, charge, color))

    def gravitational_force(self, p1: Particle, p2: Particle, G=0.1):
        """Calculate gravitational attraction between particles"""
        r_vec = p2.position - p1.position
        r = np.linalg.norm(r_vec)

        if r < 1:  # Avoid division by zero
            return np.zeros(2)

        # F = G * m1 * m2 / r^2
        force_mag = G * p1.mass * p2.mass / (r**2)
        force_vec = force_mag * (r_vec / r)

        return force_vec

    def electromagnetic_force(self, p1: Particle, p2: Particle, k=1.0):
        """Calculate electromagnetic-like force"""
        if p1.charge == 0 or p2.charge == 0:
            return np.zeros(2)

        r_vec = p2.position - p1.position
        r = np.linalg.norm(r_vec)

        if r < 1:
            return np.zeros(2)

        # Like charges repel, opposite charges attract
        # F = k * q1 * q2 / r^2
        force_mag = k * p1.charge * p2.charge / (r**2)
        force_vec = force_mag * (r_vec / r)

        return force_vec

    def damping_force(self, particle: Particle, damping=0.01):
        """Simple velocity damping"""
        return -damping * particle.velocity

    def update(self, use_gravity=True, use_em=True, use_damping=True):
        """Update all particles for one time step"""
        forces = [np.zeros(2) for _ in self.particles]

        # Calculate all pairwise forces
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles):
                if i != j:
                    if use_gravity:
                        forces[i] += self.gravitational_force(p1, p2, G=2.0)

                    if use_em:
                        forces[i] += self.electromagnetic_force(p1, p2, k=10.0)

            if use_damping:
                forces[i] += self.damping_force(p1, damping=0.02)

        # Update positions and velocities
        for i, particle in enumerate(self.particles):
            acceleration = forces[i] / particle.mass
            particle.velocity += acceleration * self.dt
            particle.position += particle.velocity * self.dt

            # Wrap around world edges (toroidal topology)
            particle.position = particle.position % self.world_size

        self.time += self.dt

    def get_state(self):
        """Get current state for visualization"""
        positions = np.array([p.position for p in self.particles])
        colors = [p.color for p in self.particles]
        sizes = np.array([p.mass * 50 for p in self.particles])

        return positions, colors, sizes

    def total_energy(self):
        """Calculate total kinetic energy"""
        ke = sum(0.5 * p.mass * np.dot(p.velocity, p.velocity) for p in self.particles)
        return ke

    def center_of_mass(self):
        """Calculate center of mass"""
        total_mass = sum(p.mass for p in self.particles)
        com = sum(p.mass * p.position for p in self.particles) / total_mass
        return com


class VortexSystem(ParticleSystem):
    """Particles arranged in a vortex pattern"""

    def __init__(self, num_particles=100, world_size=100):
        self.world_size = world_size
        self.particles: List[Particle] = []
        self.time = 0
        self.dt = 0.1

        # Create particles in a circular pattern with rotational velocity
        center = np.array([world_size/2, world_size/2])

        for i in range(num_particles):
            angle = 2 * np.pi * i / num_particles
            radius = 20 + np.random.normal(0, 3)

            pos = center + radius * np.array([np.cos(angle), np.sin(angle)])

            # Tangential velocity for rotation
            tangent = np.array([-np.sin(angle), np.cos(angle)])
            vel = tangent * (2 + np.random.normal(0, 0.2))

            mass = np.random.uniform(0.8, 1.2)
            charge = np.random.choice([-1, 1])

            color = (1.0, 0.3, 0.3) if charge > 0 else (0.3, 0.3, 1.0)

            self.particles.append(Particle(pos, vel, mass, charge, color))


class BinarySystem(ParticleSystem):
    """Two large masses with smaller particles orbiting"""

    def __init__(self, num_particles=50, world_size=100):
        self.world_size = world_size
        self.particles: List[Particle] = []
        self.time = 0
        self.dt = 0.1

        center = np.array([world_size/2, world_size/2])

        # Two large central masses
        pos1 = center + np.array([-15, 0])
        pos2 = center + np.array([15, 0])

        vel1 = np.array([0, 1.5])
        vel2 = np.array([0, -1.5])

        self.particles.append(Particle(pos1, vel1, mass=20.0, charge=1, color=(1, 0.5, 0)))
        self.particles.append(Particle(pos2, vel2, mass=20.0, charge=1, color=(0.5, 1, 0)))

        # Smaller orbiting particles
        for _ in range(num_particles):
            angle = np.random.uniform(0, 2*np.pi)
            radius = np.random.uniform(25, 45)

            # Orbit around center
            pos = center + radius * np.array([np.cos(angle), np.sin(angle)])

            # Orbital velocity
            tangent = np.array([-np.sin(angle), np.cos(angle)])
            orbital_speed = np.sqrt(50 / radius)  # Keplerian
            vel = tangent * orbital_speed * np.random.uniform(0.8, 1.2)

            mass = np.random.uniform(0.1, 0.5)
            charge = np.random.choice([-1, 0, 1])

            if charge > 0:
                color = (1.0, 0.3, 0.3)
            elif charge < 0:
                color = (0.3, 0.3, 1.0)
            else:
                color = (0.8, 0.8, 0.8)

            self.particles.append(Particle(pos, vel, mass, charge, color))


def run_simulation(system_type='random', particles=100, frames=500,
                   save_animation=True, save_frames=False):
    """Run and visualize particle simulation"""
    print(f"🌌 Particle Universe Simulation")
    print(f"   System type: {system_type}")
    print(f"   Particles: {particles}")
    print(f"   Simulating {frames} frames...\n")

    # Create system
    if system_type == 'random':
        system = ParticleSystem(num_particles=particles, world_size=100)
    elif system_type == 'vortex':
        system = VortexSystem(num_particles=particles, world_size=100)
    elif system_type == 'binary':
        system = BinarySystem(num_particles=particles, world_size=100)
    else:
        system = ParticleSystem(num_particles=particles, world_size=100)

    # Set up visualization
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, system.world_size)
    ax.set_ylim(0, system.world_size)
    ax.set_aspect('equal')
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')

    positions, colors, sizes = system.get_state()
    scatter = ax.scatter(positions[:, 0], positions[:, 1],
                        c=colors, s=sizes, alpha=0.8, edgecolors='white', linewidth=0.5)

    title = ax.set_title('Particle Universe', color='white', fontsize=16)
    ax.tick_params(colors='white')

    energy_history = []

    def update_frame(frame):
        if frame % 50 == 0:
            energy = system.total_energy()
            energy_history.append(energy)
            print(f"Frame {frame}/{frames} - Energy: {energy:.2f}")

        # Update physics
        system.update(use_gravity=True, use_em=True, use_damping=True)

        # Update visualization
        positions, colors, sizes = system.get_state()
        scatter.set_offsets(positions)
        scatter.set_color(colors)
        scatter.set_sizes(sizes)

        title.set_text(f'Particle Universe - t={system.time:.1f}')

        return scatter, title

    anim = animation.FuncAnimation(fig, update_frame, frames=frames,
                                  interval=20, blit=False, repeat=False)

    if save_animation:
        filename = f'particle_universe_{system_type}.gif'
        print(f"\nSaving animation to {filename}...")
        anim.save(filename, writer='pillow', fps=30)
        print(f"✓ Animation saved!")

    plt.close()

    # Plot energy over time
    if energy_history:
        plt.figure(figsize=(10, 6))
        plt.plot(energy_history, linewidth=2, color='cyan')
        plt.xlabel('Time Step (×50)', fontsize=12)
        plt.ylabel('Total Kinetic Energy', fontsize=12)
        plt.title('System Energy Over Time', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'energy_{system_type}.png', dpi=200, facecolor='white')
        print(f"✓ Energy plot saved!")
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Particle universe simulation')
    parser.add_argument('--type', type=str, default='random',
                       choices=['random', 'vortex', 'binary', 'all'],
                       help='Type of system to simulate')
    parser.add_argument('--particles', type=int, default=80,
                       help='Number of particles')
    parser.add_argument('--frames', type=int, default=400,
                       help='Number of frames to simulate')

    args = parser.parse_args()

    if args.type == 'all':
        for sys_type in ['random', 'vortex', 'binary']:
            run_simulation(sys_type, particles=args.particles,
                          frames=args.frames, save_animation=True)
            print()
    else:
        run_simulation(args.type, particles=args.particles,
                      frames=args.frames, save_animation=True)

    print("\n✨ The universe has been simulated")
    print("   Emergence through gravitational and electromagnetic forces")


if __name__ == "__main__":
    main()
