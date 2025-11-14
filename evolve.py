#!/usr/bin/env python3
"""
EVOLVE - An Artificial Life Simulation
Where simple creatures compete, reproduce, and evolve
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass
from typing import List, Tuple
import argparse


@dataclass
class Genome:
    """A creature's genetic code"""
    speed: float  # How fast it moves (0-1)
    perception: float  # How far it can see food (0-1)
    efficiency: float  # Energy efficiency (0-1)
    size: float  # Size of the creature (affects energy needs)
    color: Tuple[float, float, float]  # RGB color (cosmetic, but fun)

    def mutate(self, mutation_rate=0.1):
        """Create a mutated copy of this genome"""
        def mutate_value(val, min_val=0.1, max_val=1.0):
            if np.random.random() < mutation_rate:
                val += np.random.normal(0, 0.1)
                return np.clip(val, min_val, max_val)
            return val

        return Genome(
            speed=mutate_value(self.speed),
            perception=mutate_value(self.perception),
            efficiency=mutate_value(self.efficiency),
            size=mutate_value(self.size, 0.3, 2.0),
            color=tuple(np.clip(c + (np.random.normal(0, 0.1) if np.random.random() < mutation_rate else 0), 0, 1)
                       for c in self.color)
        )

    @staticmethod
    def random():
        """Generate a random genome"""
        return Genome(
            speed=np.random.uniform(0.3, 0.8),
            perception=np.random.uniform(0.3, 0.8),
            efficiency=np.random.uniform(0.3, 0.8),
            size=np.random.uniform(0.5, 1.5),
            color=(np.random.random(), np.random.random(), np.random.random())
        )


class Creature:
    """A living entity in the simulation"""

    def __init__(self, x, y, genome, energy=100.0):
        self.x = x
        self.y = y
        self.genome = genome
        self.energy = energy
        self.age = 0
        self.alive = True

    def update(self, world_size, food_positions):
        """Update the creature's state for one time step"""
        if not self.alive:
            return

        self.age += 1

        # Energy consumption based on size and efficiency
        energy_cost = (self.genome.size * 0.5) / self.genome.efficiency
        self.energy -= energy_cost

        # Find nearest food within perception range
        nearest_food = None
        nearest_dist = self.genome.perception * world_size

        for food_pos in food_positions:
            dist = np.sqrt((self.x - food_pos[0])**2 + (self.y - food_pos[1])**2)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_food = food_pos

        # Move toward food if detected
        if nearest_food is not None:
            dx = nearest_food[0] - self.x
            dy = nearest_food[1] - self.y
            dist = np.sqrt(dx**2 + dy**2)
            if dist > 0:
                # Normalize and apply speed
                move_dist = self.genome.speed * 2
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist
        else:
            # Random walk if no food detected
            self.x += np.random.normal(0, 0.5)
            self.y += np.random.normal(0, 0.5)

        # Wrap around world edges
        self.x = self.x % world_size
        self.y = self.y % world_size

        # Die if out of energy
        if self.energy <= 0:
            self.alive = False

    def can_reproduce(self):
        """Check if creature has enough energy to reproduce"""
        return self.energy > 150 and self.age > 10

    def reproduce(self):
        """Create offspring"""
        if not self.can_reproduce():
            return None

        # Reproduction costs energy
        self.energy -= 80

        # Create offspring with mutated genome
        offspring = Creature(
            x=self.x + np.random.normal(0, 2),
            y=self.y + np.random.normal(0, 2),
            genome=self.genome.mutate(),
            energy=50
        )
        return offspring


class World:
    """The simulation environment"""

    def __init__(self, size=100, initial_creatures=20, food_count=50):
        self.size = size
        self.creatures: List[Creature] = []
        self.food: List[Tuple[float, float]] = []
        self.generation = 0
        self.stats_history = {
            'population': [],
            'avg_speed': [],
            'avg_perception': [],
            'avg_efficiency': [],
            'avg_size': []
        }

        # Initialize creatures
        for _ in range(initial_creatures):
            self.creatures.append(Creature(
                x=np.random.uniform(0, size),
                y=np.random.uniform(0, size),
                genome=Genome.random()
            ))

        # Initialize food
        self.respawn_food(food_count)

    def respawn_food(self, count):
        """Add food to the world"""
        for _ in range(count):
            self.food.append((
                np.random.uniform(0, self.size),
                np.random.uniform(0, self.size)
            ))

    def update(self):
        """Update the world for one time step"""
        self.generation += 1

        # Update all creatures
        for creature in self.creatures:
            if creature.alive:
                creature.update(self.size, self.food)

        # Check for food consumption
        new_food = []
        for food_pos in self.food:
            eaten = False
            for creature in self.creatures:
                if not creature.alive:
                    continue
                dist = np.sqrt((creature.x - food_pos[0])**2 + (creature.y - food_pos[1])**2)
                if dist < 2:  # Eating range
                    creature.energy += 40
                    eaten = True
                    break
            if not eaten:
                new_food.append(food_pos)
        self.food = new_food

        # Respawn some food
        if len(self.food) < 30:
            self.respawn_food(5)

        # Reproduction
        new_creatures = []
        for creature in self.creatures:
            if creature.alive and creature.can_reproduce():
                offspring = creature.reproduce()
                if offspring:
                    new_creatures.append(offspring)

        self.creatures.extend(new_creatures)

        # Remove dead creatures
        self.creatures = [c for c in self.creatures if c.alive]

        # Track statistics
        if self.creatures:
            self.stats_history['population'].append(len(self.creatures))
            self.stats_history['avg_speed'].append(np.mean([c.genome.speed for c in self.creatures]))
            self.stats_history['avg_perception'].append(np.mean([c.genome.perception for c in self.creatures]))
            self.stats_history['avg_efficiency'].append(np.mean([c.genome.efficiency for c in self.creatures]))
            self.stats_history['avg_size'].append(np.mean([c.genome.size for c in self.creatures]))

    def get_state(self):
        """Get current state for visualization"""
        if not self.creatures:
            return [], [], []

        creature_x = [c.x for c in self.creatures]
        creature_y = [c.y for c in self.creatures]
        creature_colors = [c.genome.color for c in self.creatures]
        creature_sizes = [(c.genome.size * 20) ** 2 for c in self.creatures]

        food_x = [f[0] for f in self.food]
        food_y = [f[1] for f in self.food]

        return (creature_x, creature_y, creature_colors, creature_sizes), (food_x, food_y)


def run_simulation(generations=500, visualize=True, save_stats=True):
    """Run the evolution simulation"""
    print("🧬 Initializing artificial life simulation...")
    print("   Creating primordial soup...\n")

    world = World(size=100, initial_creatures=30, food_count=60)

    if visualize:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # World visualization
        ax1.set_xlim(0, world.size)
        ax1.set_ylim(0, world.size)
        ax1.set_aspect('equal')
        ax1.set_title('Artificial Life Ecosystem')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')

        creature_scatter = ax1.scatter([], [], s=[], c=[], alpha=0.7, edgecolors='black', linewidth=0.5)
        food_scatter = ax1.scatter([], [], s=30, c='green', marker='s', alpha=0.6)

        # Stats visualization
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Value')
        ax2.set_title('Evolution Statistics')
        ax2.grid(True, alpha=0.3)

        lines = {
            'population': ax2.plot([], [], label='Population', linewidth=2)[0],
            'avg_speed': ax2.plot([], [], label='Avg Speed', linewidth=1.5)[0],
            'avg_perception': ax2.plot([], [], label='Avg Perception', linewidth=1.5)[0],
            'avg_efficiency': ax2.plot([], [], label='Avg Efficiency', linewidth=1.5)[0],
        }
        ax2.legend()

        def update_frame(frame):
            if frame % 10 == 0:
                print(f"Generation {frame}: {len(world.creatures)} creatures alive")

            if len(world.creatures) == 0:
                print("\n💀 Extinction event! All creatures have died.")
                return creature_scatter, food_scatter

            world.update()

            # Update world visualization
            (cx, cy, colors, sizes), (fx, fy) = world.get_state()
            creature_scatter.set_offsets(np.c_[cx, cy])
            creature_scatter.set_color(colors)
            creature_scatter.set_sizes(sizes)
            food_scatter.set_offsets(np.c_[fx, fy])

            # Update stats
            gens = range(len(world.stats_history['population']))
            if gens:
                lines['population'].set_data(gens, world.stats_history['population'])
                lines['avg_speed'].set_data(gens, [x * 50 for x in world.stats_history['avg_speed']])
                lines['avg_perception'].set_data(gens, [x * 50 for x in world.stats_history['avg_perception']])
                lines['avg_efficiency'].set_data(gens, [x * 50 for x in world.stats_history['avg_efficiency']])

                ax2.set_xlim(0, max(gens) + 10)
                ax2.set_ylim(0, max(max(world.stats_history['population']), 100))

            return creature_scatter, food_scatter

        anim = animation.FuncAnimation(fig, update_frame, frames=generations,
                                      interval=50, blit=False, repeat=False)

        plt.tight_layout()
        anim.save('evolution.gif', writer='pillow', fps=20)
        print(f"\n✨ Simulation complete! Saved to evolution.gif")
        plt.close()
    else:
        # Run without visualization
        for gen in range(generations):
            if gen % 50 == 0:
                print(f"Generation {gen}: {len(world.creatures)} creatures alive")
            world.update()
            if len(world.creatures) == 0:
                print(f"\n💀 Extinction at generation {gen}")
                break

    # Plot final statistics
    if save_stats and world.stats_history['population']:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        gens = range(len(world.stats_history['population']))

        axes[0, 0].plot(gens, world.stats_history['population'], linewidth=2, color='blue')
        axes[0, 0].set_title('Population Over Time')
        axes[0, 0].set_xlabel('Generation')
        axes[0, 0].set_ylabel('Number of Creatures')
        axes[0, 0].grid(True, alpha=0.3)

        axes[0, 1].plot(gens, world.stats_history['avg_speed'], linewidth=2, color='red', label='Speed')
        axes[0, 1].plot(gens, world.stats_history['avg_perception'], linewidth=2, color='green', label='Perception')
        axes[0, 1].plot(gens, world.stats_history['avg_efficiency'], linewidth=2, color='purple', label='Efficiency')
        axes[0, 1].set_title('Trait Evolution')
        axes[0, 1].set_xlabel('Generation')
        axes[0, 1].set_ylabel('Average Value')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        axes[1, 0].plot(gens, world.stats_history['avg_size'], linewidth=2, color='orange')
        axes[1, 0].set_title('Average Size Over Time')
        axes[1, 0].set_xlabel('Generation')
        axes[1, 0].set_ylabel('Size')
        axes[1, 0].grid(True, alpha=0.3)

        # Distribution of traits in final population
        if world.creatures:
            final_speeds = [c.genome.speed for c in world.creatures]
            final_perceptions = [c.genome.perception for c in world.creatures]
            final_efficiencies = [c.genome.efficiency for c in world.creatures]

            axes[1, 1].hist([final_speeds, final_perceptions, final_efficiencies],
                           bins=15, alpha=0.7, label=['Speed', 'Perception', 'Efficiency'])
            axes[1, 1].set_title('Final Population Trait Distribution')
            axes[1, 1].set_xlabel('Trait Value')
            axes[1, 1].set_ylabel('Count')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('evolution_stats.png', dpi=300, bbox_inches='tight')
        print(f"📊 Statistics saved to evolution_stats.png")
        plt.close()

    return world


def main():
    parser = argparse.ArgumentParser(description='Artificial life evolution simulator')
    parser.add_argument('--generations', type=int, default=300,
                       help='Number of generations to simulate')
    parser.add_argument('--no-viz', action='store_true',
                       help='Run without animation (faster)')

    args = parser.parse_args()

    world = run_simulation(
        generations=args.generations,
        visualize=not args.no_viz,
        save_stats=True
    )

    if world.creatures:
        print(f"\n🎉 Simulation complete!")
        print(f"   Final population: {len(world.creatures)}")
        print(f"   Generations survived: {world.generation}")
        print(f"\n   Average traits of survivors:")
        print(f"   Speed: {np.mean([c.genome.speed for c in world.creatures]):.3f}")
        print(f"   Perception: {np.mean([c.genome.perception for c in world.creatures]):.3f}")
        print(f"   Efficiency: {np.mean([c.genome.efficiency for c in world.creatures]):.3f}")
        print(f"   Size: {np.mean([c.genome.size for c in world.creatures]):.3f}")


if __name__ == "__main__":
    main()
