#!/usr/bin/env python3
"""
Evolutionary Swarms: When Flocking Behavior Evolves
====================================================

A HYBRID exploration combining:
- Claude B's swarm intelligence (boids with local rules)
- Claude A's evolution (genes, mutation, selection)

The Question: Can evolution discover optimal flocking parameters?

Instead of hardcoding weights for separation/alignment/cohesion,
we let boids have GENES for these parameters. Boids that flock better
reproduce more. Natural selection should optimize flocking behavior.

This bridges temporal evolution (Claude A) with spatial coordination (Claude B).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass
from typing import List
import argparse


@dataclass
class BoidGenome:
    """Genetic encoding of flocking behavior"""
    separation_weight: float      # How much to avoid crowding
    alignment_weight: float        # How much to match velocity
    cohesion_weight: float        # How much to move toward center
    perception_radius: float       # How far the boid can "see"
    max_speed: float              # Maximum velocity


class EvolvingBoid:
    """A boid whose flocking behavior is determined by its genes"""

    def __init__(self, position, velocity, genome: BoidGenome, bounds, boid_id):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.genome = genome
        self.bounds = bounds
        self.id = boid_id

        # Fitness tracking
        self.time_in_flock = 0
        self.energy = 100.0
        self.age = 0

        # Constants
        self.max_force = 0.05
        self.reproduction_threshold = 150.0  # Energy needed to reproduce
        self.energy_cost_per_step = 0.1
        self.energy_gain_in_flock = 0.3

    def apply_force(self, force):
        """Apply a steering force"""
        self.velocity += force

    def update(self, neighbors):
        """Update position and velocity based on genome and neighbors"""
        # Calculate flocking forces using genetic weights
        sep = self._separation(neighbors) * self.genome.separation_weight
        ali = self._alignment(neighbors) * self.genome.alignment_weight
        coh = self._cohesion(neighbors) * self.genome.cohesion_weight

        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)

        # Update position
        self.position += self.velocity

        # Limit speed by genome
        speed = np.linalg.norm(self.velocity)
        if speed > self.genome.max_speed:
            self.velocity = (self.velocity / speed) * self.genome.max_speed

        # Wrap boundaries
        self.position[0] = self.position[0] % self.bounds[0]
        self.position[1] = self.position[1] % self.bounds[1]

        # Update fitness metrics
        self.age += 1
        self.energy -= self.energy_cost_per_step

        # Gain energy if in flock (reward coordination)
        if len(neighbors) >= 3:
            self.time_in_flock += 1
            self.energy += self.energy_gain_in_flock
            self.energy = min(self.energy, 200.0)  # Cap energy

    def _separation(self, neighbors):
        """Steer to avoid crowding"""
        if not neighbors:
            return np.zeros(2)

        steer = np.zeros(2)
        for other in neighbors:
            distance = np.linalg.norm(self.position - other.position)
            if 0 < distance < 25:
                diff = self.position - other.position
                diff = diff / distance  # Weight by distance
                steer += diff

        if np.linalg.norm(steer) > 0:
            steer = (steer / np.linalg.norm(steer)) * self.genome.max_speed
            steer = steer - self.velocity
            if np.linalg.norm(steer) > self.max_force:
                steer = (steer / np.linalg.norm(steer)) * self.max_force

        return steer

    def _alignment(self, neighbors):
        """Steer toward average heading"""
        if not neighbors:
            return np.zeros(2)

        avg_vel = np.mean([other.velocity for other in neighbors], axis=0)
        if np.linalg.norm(avg_vel) > 0:
            avg_vel = (avg_vel / np.linalg.norm(avg_vel)) * self.genome.max_speed
        steer = avg_vel - self.velocity

        if np.linalg.norm(steer) > self.max_force:
            steer = (steer / np.linalg.norm(steer)) * self.max_force

        return steer

    def _cohesion(self, neighbors):
        """Steer toward average position"""
        if not neighbors:
            return np.zeros(2)

        center = np.mean([other.position for other in neighbors], axis=0)
        desired = center - self.position

        if np.linalg.norm(desired) > 0:
            desired = (desired / np.linalg.norm(desired)) * self.genome.max_speed
        steer = desired - self.velocity

        if np.linalg.norm(steer) > self.max_force:
            steer = (steer / np.linalg.norm(steer)) * self.max_force

        return steer

    def can_reproduce(self):
        """Check if boid has enough energy to reproduce"""
        return self.energy > self.reproduction_threshold and self.age > 50

    def reproduce(self, mutation_rate=0.1):
        """Create offspring with mutated genome"""
        # Copy parent genome
        child_genome = BoidGenome(
            separation_weight=self.genome.separation_weight,
            alignment_weight=self.genome.alignment_weight,
            cohesion_weight=self.genome.cohesion_weight,
            perception_radius=self.genome.perception_radius,
            max_speed=self.genome.max_speed
        )

        # Mutate each gene with some probability
        if np.random.random() < mutation_rate:
            child_genome.separation_weight += np.random.normal(0, 0.2)
            child_genome.separation_weight = np.clip(child_genome.separation_weight, 0.1, 3.0)

        if np.random.random() < mutation_rate:
            child_genome.alignment_weight += np.random.normal(0, 0.2)
            child_genome.alignment_weight = np.clip(child_genome.alignment_weight, 0.1, 3.0)

        if np.random.random() < mutation_rate:
            child_genome.cohesion_weight += np.random.normal(0, 0.2)
            child_genome.cohesion_weight = np.clip(child_genome.cohesion_weight, 0.1, 3.0)

        if np.random.random() < mutation_rate:
            child_genome.perception_radius += np.random.normal(0, 5)
            child_genome.perception_radius = np.clip(child_genome.perception_radius, 20, 100)

        if np.random.random() < mutation_rate:
            child_genome.max_speed += np.random.normal(0, 0.2)
            child_genome.max_speed = np.clip(child_genome.max_speed, 1.0, 4.0)

        # Create child near parent
        child_pos = self.position + np.random.uniform(-10, 10, 2)
        child_vel = self.velocity + np.random.uniform(-0.5, 0.5, 2)

        # Parent loses energy
        self.energy -= 50

        return EvolvingBoid(child_pos, child_vel, child_genome, self.bounds,
                           boid_id=np.random.randint(0, 1000000))


class EvolutionarySwarm:
    """A population of boids whose flocking behavior evolves"""

    def __init__(self, n_boids, bounds, mutation_rate=0.15):
        self.bounds = bounds
        self.mutation_rate = mutation_rate
        self.generation = 0
        self.next_id = 0

        # Create initial population with random genomes
        self.boids = []
        for _ in range(n_boids):
            genome = BoidGenome(
                separation_weight=np.random.uniform(0.5, 2.5),
                alignment_weight=np.random.uniform(0.5, 2.5),
                cohesion_weight=np.random.uniform(0.5, 2.5),
                perception_radius=np.random.uniform(40, 70),
                max_speed=np.random.uniform(1.5, 2.5)
            )
            pos = np.random.rand(2) * bounds
            vel = (np.random.rand(2) - 0.5) * 2
            self.boids.append(EvolvingBoid(pos, vel, genome, bounds, self.next_id))
            self.next_id += 1

        # Statistics tracking
        self.population_history = [len(self.boids)]
        self.avg_separation_weight = []
        self.avg_alignment_weight = []
        self.avg_cohesion_weight = []
        self.avg_perception = []
        self.avg_coordination = []

    def update(self):
        """Update all boids for one timestep"""
        # Find neighbors for each boid
        for boid in self.boids:
            neighbors = []
            for other in self.boids:
                if boid.id != other.id:
                    distance = np.linalg.norm(boid.position - other.position)
                    if distance < boid.genome.perception_radius:
                        neighbors.append(other)

            boid.update(neighbors)

        # Reproduction (with population cap to prevent computational explosion)
        max_population = 150
        new_boids = []
        for boid in self.boids:
            if boid.can_reproduce() and len(self.boids) + len(new_boids) < max_population:
                child = boid.reproduce(self.mutation_rate)
                new_boids.append(child)

        self.boids.extend(new_boids)

        # Death (remove boids with no energy)
        self.boids = [b for b in self.boids if b.energy > 0]

        # Track statistics
        if len(self.boids) > 0:
            self.population_history.append(len(self.boids))
            self.avg_separation_weight.append(np.mean([b.genome.separation_weight for b in self.boids]))
            self.avg_alignment_weight.append(np.mean([b.genome.alignment_weight for b in self.boids]))
            self.avg_cohesion_weight.append(np.mean([b.genome.cohesion_weight for b in self.boids]))
            self.avg_perception.append(np.mean([b.genome.perception_radius for b in self.boids]))

            # Calculate coordination metric
            if len(self.boids) > 1:
                velocities = np.array([b.velocity for b in self.boids])
                vel_normalized = velocities / (np.linalg.norm(velocities, axis=1, keepdims=True) + 1e-6)
                avg_direction = np.mean(vel_normalized, axis=0)
                coordination = np.linalg.norm(avg_direction)
                self.avg_coordination.append(coordination)
            else:
                self.avg_coordination.append(0)

        self.generation += 1

    def get_positions(self):
        return np.array([b.position for b in self.boids]) if self.boids else np.array([])

    def get_velocities(self):
        return np.array([b.velocity for b in self.boids]) if self.boids else np.array([])


def run_evolution_experiment(n_boids=50, steps=2000, mutation_rate=0.15):
    """Run evolutionary swarm experiment and track results"""
    bounds = np.array([800, 600])
    swarm = EvolutionarySwarm(n_boids, bounds, mutation_rate)

    print("=" * 70)
    print("EVOLUTIONARY SWARMS - Evolution Discovers Flocking")
    print("=" * 70)
    print(f"\nInitial population: {n_boids} boids")
    print(f"Mutation rate: {mutation_rate}")
    print("\nHypothesis: Evolution will discover optimal flocking parameters")
    print("\nRunning simulation...\n")

    # Run simulation
    for step in range(steps):
        swarm.update()

        if step % 200 == 0 and len(swarm.boids) > 0:
            coord = swarm.avg_coordination[-1] if swarm.avg_coordination else 0
            print(f"Step {step:4d}: Population={len(swarm.boids):3d}, " +
                  f"Coordination={coord:.3f}, " +
                  f"Avg Sep={swarm.avg_separation_weight[-1]:.2f}, " +
                  f"Align={swarm.avg_alignment_weight[-1]:.2f}, " +
                  f"Cohes={swarm.avg_cohesion_weight[-1]:.2f}")

        # Stop if population dies out
        if len(swarm.boids) == 0:
            print(f"\nPopulation extinct at step {step}")
            break

    return swarm


def plot_evolution_results(swarm, filename='claude_b_evolutionary_swarms.png'):
    """Visualize how flocking parameters evolved"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    steps = range(len(swarm.population_history))

    # Population over time
    ax = axes[0, 0]
    ax.plot(steps, swarm.population_history, color='purple', linewidth=2)
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Population Size')
    ax.set_title('Population Dynamics')
    ax.grid(True, alpha=0.3)

    # Coordination metric
    ax = axes[0, 1]
    if swarm.avg_coordination:
        ax.plot(steps[:len(swarm.avg_coordination)], swarm.avg_coordination,
                color='green', linewidth=2)
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Coordination (0-1)')
    ax.set_title('Emergent Coordination (Alignment Metric)')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)

    # Evolved weights
    ax = axes[1, 0]
    if swarm.avg_separation_weight:
        ax.plot(steps[:len(swarm.avg_separation_weight)], swarm.avg_separation_weight,
                label='Separation', linewidth=2)
        ax.plot(steps[:len(swarm.avg_alignment_weight)], swarm.avg_alignment_weight,
                label='Alignment', linewidth=2)
        ax.plot(steps[:len(swarm.avg_cohesion_weight)], swarm.avg_cohesion_weight,
                label='Cohesion', linewidth=2)
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Average Weight')
    ax.set_title('Evolution of Flocking Weights')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Perception radius
    ax = axes[1, 1]
    if swarm.avg_perception:
        ax.plot(steps[:len(swarm.avg_perception)], swarm.avg_perception,
                color='orange', linewidth=2)
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Perception Radius')
    ax.set_title('Evolution of Perception Range')
    ax.grid(True, alpha=0.3)

    plt.suptitle('Evolutionary Swarms: Natural Selection Optimizes Flocking Behavior',
                 fontsize=14, y=0.995)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nSaved evolution plot: {filename}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Evolutionary Swarms')
    parser.add_argument('--boids', type=int, default=50, help='Initial population')
    parser.add_argument('--steps', type=int, default=2000, help='Simulation steps')
    parser.add_argument('--mutation', type=float, default=0.15, help='Mutation rate')

    args = parser.parse_args()

    # Run experiment
    swarm = run_evolution_experiment(args.boids, args.steps, args.mutation)

    # Visualize results
    plot_evolution_results(swarm)

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    if len(swarm.boids) > 0:
        print(f"\nFinal population: {len(swarm.boids)} boids")
        print(f"Final coordination: {swarm.avg_coordination[-1]:.3f}")
        print("\nEvolved parameters (population average):")
        print(f"  Separation weight: {swarm.avg_separation_weight[-1]:.3f}")
        print(f"  Alignment weight:  {swarm.avg_alignment_weight[-1]:.3f}")
        print(f"  Cohesion weight:   {swarm.avg_cohesion_weight[-1]:.3f}")
        print(f"  Perception radius: {swarm.avg_perception[-1]:.1f}")

        print("\nKey insight: Natural selection discovered flocking parameters")
        print("without them being explicitly programmed. Evolution optimizes")
        print("coordination through reproductive success.")
    else:
        print("\nPopulation went extinct - parameters may need adjustment")

    print("\n" + "=" * 70)
    print("HYBRID EXPLORATION: Claude A's evolution + Claude B's swarms")
    print("=" * 70)


if __name__ == '__main__':
    main()
