#!/usr/bin/env python3
"""
Evolutionary Swarms - A Hybrid System
Combining Claude A's evolution with Claude B's swarm intelligence

What if flocking behavior itself evolves?
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass
from typing import List, Tuple
import argparse


@dataclass
class SwarmGenome:
    """Genetic encoding of swarm behavior parameters"""
    separation_weight: float  # Avoid crowding neighbors
    alignment_weight: float   # Align with neighbors
    cohesion_weight: float    # Move toward center of neighbors
    perception_radius: float  # How far boids can see
    max_speed: float         # Speed limit

    def mutate(self, mutation_rate=0.1, mutation_strength=0.1):
        """Create a mutated copy"""
        def mutate_value(val, min_val=0.0, max_val=10.0):
            if np.random.random() < mutation_rate:
                val += np.random.normal(0, mutation_strength)
                return np.clip(val, min_val, max_val)
            return val

        return SwarmGenome(
            separation_weight=mutate_value(self.separation_weight, 0, 5),
            alignment_weight=mutate_value(self.alignment_weight, 0, 5),
            cohesion_weight=mutate_value(self.cohesion_weight, 0, 5),
            perception_radius=mutate_value(self.perception_radius, 10, 100),
            max_speed=mutate_value(self.max_speed, 1, 10)
        )

    @staticmethod
    def random():
        """Generate random genome"""
        return SwarmGenome(
            separation_weight=np.random.uniform(0.5, 2.0),
            alignment_weight=np.random.uniform(0.5, 2.0),
            cohesion_weight=np.random.uniform(0.5, 2.0),
            perception_radius=np.random.uniform(20, 60),
            max_speed=np.random.uniform(2, 6)
        )

    @staticmethod
    def crossover(parent1, parent2):
        """Combine two genomes"""
        return SwarmGenome(
            separation_weight=(parent1.separation_weight + parent2.separation_weight) / 2,
            alignment_weight=(parent1.alignment_weight + parent2.alignment_weight) / 2,
            cohesion_weight=(parent1.cohesion_weight + parent2.cohesion_weight) / 2,
            perception_radius=(parent1.perception_radius + parent2.perception_radius) / 2,
            max_speed=(parent1.max_speed + parent2.max_speed) / 2
        )


class Boid:
    """A single boid in the swarm"""

    def __init__(self, x, y, vx, vy):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([vx, vy], dtype=float)

    def update(self, neighbors, genome: SwarmGenome, world_size):
        """Update boid based on Reynolds' rules with evolved parameters"""
        if len(neighbors) == 0:
            # No neighbors - just move forward
            self.position += self.velocity
            self.position %= world_size
            return

        # Separation: avoid crowding
        separation = np.zeros(2)
        for boid in neighbors:
            diff = self.position - boid.position
            dist = np.linalg.norm(diff)
            if dist < genome.perception_radius / 3 and dist > 0:
                separation += diff / dist

        # Alignment: match velocity
        alignment = np.mean([b.velocity for b in neighbors], axis=0) - self.velocity

        # Cohesion: move toward center
        center = np.mean([b.position for b in neighbors], axis=0)
        cohesion = center - self.position

        # Apply evolved weights
        acceleration = (
            genome.separation_weight * separation +
            genome.alignment_weight * alignment +
            genome.cohesion_weight * cohesion
        )

        # Update velocity and position
        self.velocity += acceleration * 0.01

        # Limit speed
        speed = np.linalg.norm(self.velocity)
        if speed > genome.max_speed:
            self.velocity = (self.velocity / speed) * genome.max_speed

        self.position += self.velocity
        self.position %= world_size


class Swarm:
    """A swarm with specific genome"""

    def __init__(self, genome: SwarmGenome, num_boids=30, world_size=200):
        self.genome = genome
        self.world_size = world_size
        self.boids: List[Boid] = []
        self.fitness = None

        # Initialize boids randomly
        for _ in range(num_boids):
            x = np.random.uniform(0, world_size)
            y = np.random.uniform(0, world_size)
            angle = np.random.uniform(0, 2 * np.pi)
            speed = genome.max_speed * 0.5
            vx = speed * np.cos(angle)
            vy = speed * np.sin(angle)
            self.boids.append(Boid(x, y, vx, vy))

    def get_neighbors(self, boid: Boid):
        """Get neighbors within perception radius"""
        neighbors = []
        for other in self.boids:
            if other is boid:
                continue

            dist = np.linalg.norm(boid.position - other.position)
            if dist < self.genome.perception_radius:
                neighbors.append(other)

        return neighbors

    def update(self):
        """Update all boids"""
        for boid in self.boids:
            neighbors = self.get_neighbors(boid)
            boid.update(neighbors, self.genome, self.world_size)

    def compute_fitness(self):
        """Evaluate swarm fitness based on multiple criteria"""
        if self.fitness is not None:
            return self.fitness

        # Run simulation for a bit
        for _ in range(200):
            self.update()

        # Fitness criteria:
        # 1. Alignment (all moving in similar direction)
        velocities = np.array([b.velocity for b in self.boids])
        avg_velocity = np.mean(velocities, axis=0)
        alignment = np.mean([
            np.dot(v, avg_velocity) / (np.linalg.norm(v) * np.linalg.norm(avg_velocity) + 1e-6)
            for v in velocities
        ])

        # 2. Cohesion (staying together)
        positions = np.array([b.position for b in self.boids])
        center = np.mean(positions, axis=0)
        avg_distance_to_center = np.mean([
            np.linalg.norm(p - center) for p in positions
        ])
        cohesion_score = 1 / (1 + avg_distance_to_center / 50)

        # 3. Speed (moving, not static)
        speeds = [np.linalg.norm(b.velocity) for b in self.boids]
        avg_speed = np.mean(speeds)
        speed_score = avg_speed / self.genome.max_speed

        # 4. Separation (not too crowded)
        min_distances = []
        for i, b1 in enumerate(self.boids):
            min_dist = float('inf')
            for j, b2 in enumerate(self.boids):
                if i != j:
                    dist = np.linalg.norm(b1.position - b2.position)
                    min_dist = min(min_dist, dist)
            min_distances.append(min_dist)

        avg_min_dist = np.mean(min_distances)
        separation_score = min(1.0, avg_min_dist / 10)

        # Combined fitness
        self.fitness = (
            0.4 * alignment +
            0.3 * cohesion_score +
            0.2 * speed_score +
            0.1 * separation_score
        )

        return self.fitness


class EvolutionarySwarmOptimizer:
    """Evolve optimal swarm parameters"""

    def __init__(self, population_size=20):
        self.population_size = population_size
        self.swarms: List[Swarm] = []
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []

        # Initialize population
        for _ in range(population_size):
            genome = SwarmGenome.random()
            self.swarms.append(Swarm(genome))

    def evolve_generation(self):
        """Run one generation of evolution"""
        # Evaluate fitness
        fitnesses = [swarm.compute_fitness() for swarm in self.swarms]

        # Track statistics
        self.best_fitness_history.append(max(fitnesses))
        self.avg_fitness_history.append(np.mean(fitnesses))

        # Sort by fitness
        self.swarms.sort(key=lambda s: s.fitness, reverse=True)

        # Selection and reproduction
        new_swarms = []

        # Elitism - keep top 2
        for i in range(2):
            new_swarms.append(Swarm(self.swarms[i].genome))

        # Create rest through crossover and mutation
        while len(new_swarms) < self.population_size:
            # Tournament selection
            parent1 = max(np.random.choice(self.swarms, 3), key=lambda s: s.fitness)
            parent2 = max(np.random.choice(self.swarms, 3), key=lambda s: s.fitness)

            # Crossover
            child_genome = SwarmGenome.crossover(parent1.genome, parent2.genome)

            # Mutation
            child_genome = child_genome.mutate(mutation_rate=0.2, mutation_strength=0.3)

            new_swarms.append(Swarm(child_genome))

        self.swarms = new_swarms
        self.generation += 1

    def run(self, generations=30, verbose=True):
        """Run evolution for multiple generations"""
        for gen in range(generations):
            self.evolve_generation()

            if verbose and gen % 5 == 0:
                best = self.swarms[0]
                if best.fitness is not None:
                    print(f"Gen {gen}: Best fitness = {best.fitness:.4f}")
                    print(f"  Params: sep={best.genome.separation_weight:.2f}, "
                          f"align={best.genome.alignment_weight:.2f}, "
                          f"coh={best.genome.cohesion_weight:.2f}, "
                          f"radius={best.genome.perception_radius:.1f}")

        return self.swarms[0]


def visualize_swarm(swarm: Swarm, steps=500, title="Evolved Swarm", filename="evolved_swarm.gif"):
    """Visualize a swarm's behavior"""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, swarm.world_size)
    ax.set_ylim(0, swarm.world_size)
    ax.set_aspect('equal')
    ax.set_facecolor('#0a0a0a')
    fig.patch.set_facecolor('#0a0a0a')

    positions = np.array([b.position for b in swarm.boids])
    velocities = np.array([b.velocity for b in swarm.boids])

    scatter = ax.scatter(positions[:, 0], positions[:, 1],
                        c='cyan', s=50, alpha=0.8, edgecolors='white', linewidth=0.5)

    quiver = ax.quiver(positions[:, 0], positions[:, 1],
                       velocities[:, 0], velocities[:, 1],
                       color='yellow', alpha=0.6, scale=50, width=0.003)

    title_text = ax.set_title(title, color='white', fontsize=14)
    ax.tick_params(colors='white')

    def update_frame(frame):
        swarm.update()

        positions = np.array([b.position for b in swarm.boids])
        velocities = np.array([b.velocity for b in swarm.boids])

        scatter.set_offsets(positions)

        quiver.set_offsets(positions)
        quiver.set_UVC(velocities[:, 0], velocities[:, 1])

        return scatter, quiver

    anim = animation.FuncAnimation(fig, update_frame, frames=steps,
                                  interval=20, blit=False, repeat=False)

    print(f"Saving animation to {filename}...")
    anim.save(filename, writer='pillow', fps=30)
    print(f"✓ Saved!")
    plt.close()


def plot_evolution(optimizer: EvolutionarySwarmOptimizer, filename='swarm_evolution.png'):
    """Plot fitness over generations"""
    fig, ax = plt.subplots(figsize=(12, 6))

    gens = range(len(optimizer.best_fitness_history))
    ax.plot(gens, optimizer.best_fitness_history,
            label='Best Fitness', linewidth=2, color='cyan')
    ax.plot(gens, optimizer.avg_fitness_history,
            label='Average Fitness', linewidth=1.5, color='orange', alpha=0.7)

    ax.set_xlabel('Generation', fontsize=12)
    ax.set_ylabel('Fitness', fontsize=12)
    ax.set_title('Evolution of Swarm Behavior Parameters', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"✓ Evolution plot saved to {filename}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Evolutionary swarm optimization')
    parser.add_argument('--generations', type=int, default=25,
                       help='Number of generations to evolve')
    parser.add_argument('--population', type=int, default=20,
                       help='Population size')

    args = parser.parse_args()

    print("🧬🐦 Evolutionary Swarms - A Hybrid System")
    print("   Combining evolution with swarm intelligence")
    print("   Claude A + Claude B collaboration\n")

    # Run evolution
    print(f"Evolving swarm parameters over {args.generations} generations...\n")
    optimizer = EvolutionarySwarmOptimizer(population_size=args.population)
    best_swarm = optimizer.run(generations=args.generations, verbose=True)

    print("\n" + "=" * 70)
    print("EVOLVED SWARM PARAMETERS")
    print("=" * 70)
    print(f"Fitness: {best_swarm.fitness:.4f}")
    print(f"\nGenome:")
    print(f"  Separation weight: {best_swarm.genome.separation_weight:.3f}")
    print(f"  Alignment weight:  {best_swarm.genome.alignment_weight:.3f}")
    print(f"  Cohesion weight:   {best_swarm.genome.cohesion_weight:.3f}")
    print(f"  Perception radius: {best_swarm.genome.perception_radius:.1f}")
    print(f"  Max speed:         {best_swarm.genome.max_speed:.2f}")

    # Plot evolution
    plot_evolution(optimizer)

    # Visualize best swarm
    print("\nVisualizing evolved swarm behavior...")
    visualize_swarm(best_swarm, steps=400,
                   title=f"Evolved Swarm (Fitness: {best_swarm.fitness:.3f})",
                   filename="evolved_swarm_best.gif")

    # Compare with random swarm
    print("\nComparing with random (non-evolved) swarm...")
    random_swarm = Swarm(SwarmGenome.random())
    random_fitness = random_swarm.compute_fitness()
    print(f"Random swarm fitness: {random_fitness:.4f}")

    visualize_swarm(random_swarm, steps=400,
                   title=f"Random Swarm (Fitness: {random_fitness:.3f})",
                   filename="evolved_swarm_random.gif")

    improvement = ((best_swarm.fitness - random_fitness) / random_fitness) * 100
    print(f"\n✨ Evolution improved swarm fitness by {improvement:.1f}%")
    print("\nHybrid exploration complete!")
    print("This system combines:")
    print("  - Claude A's genetic algorithm framework")
    print("  - Claude B's swarm intelligence mechanics")
    print("  - Emergent optimization of collective behavior")


if __name__ == "__main__":
    main()
