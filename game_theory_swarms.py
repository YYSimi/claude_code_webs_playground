#!/usr/bin/env python3
"""
Game Theory Swarms
Combining Claude A's game theory with Claude B's swarm intelligence

Each boid has a cooperation strategy. They play games with neighbors.
Question: Do cooperative strategies cluster spatially?
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from enum import Enum
import argparse


class Strategy(Enum):
    """Cooperation strategies from game theory"""
    ALWAYS_COOPERATE = "AlwaysC"
    ALWAYS_DEFECT = "AlwaysD"
    TIT_FOR_TAT = "TFT"
    PAVLOV = "Pavlov"
    GRUDGER = "Grudger"
    RANDOM = "Random"


class GameTheoryBoid:
    """A boid with a cooperation strategy"""

    def __init__(self, x, y, vx, vy, strategy, world_size=200):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([vx, vy], dtype=float)
        self.strategy = strategy
        self.world_size = world_size

        # Game history with neighbors
        self.history = {}  # neighbor_id -> (my_moves, their_moves)
        self.score = 0
        self.cooperation_rate = 1.0  # Track individual cooperation

        # Strategy colors for visualization
        self.color = self._get_strategy_color()

    def _get_strategy_color(self):
        """Map strategy to color"""
        colors = {
            Strategy.ALWAYS_COOPERATE: (0.2, 0.8, 0.2),  # Green
            Strategy.ALWAYS_DEFECT: (0.8, 0.2, 0.2),     # Red
            Strategy.TIT_FOR_TAT: (0.2, 0.6, 0.9),       # Blue
            Strategy.PAVLOV: (0.9, 0.7, 0.2),            # Yellow
            Strategy.GRUDGER: (0.7, 0.2, 0.8),           # Purple
            Strategy.RANDOM: (0.5, 0.5, 0.5),            # Gray
        }
        return colors.get(self.strategy, (0.5, 0.5, 0.5))

    def decide_move(self, neighbor_id, opponent_last_move=None):
        """Decide whether to cooperate or defect"""
        my_last = None
        if neighbor_id in self.history and len(self.history[neighbor_id][0]) > 0:
            my_last = self.history[neighbor_id][0][-1]

        if self.strategy == Strategy.ALWAYS_COOPERATE:
            return 'C'

        elif self.strategy == Strategy.ALWAYS_DEFECT:
            return 'D'

        elif self.strategy == Strategy.TIT_FOR_TAT:
            if opponent_last_move is None:
                return 'C'  # Start cooperating
            return opponent_last_move

        elif self.strategy == Strategy.PAVLOV:
            # Win-stay, lose-shift
            if my_last is None:
                return 'C'

            # Check last outcome
            if opponent_last_move is None:
                return 'C'

            # If both cooperated or I defected and they cooperated (I won), stay
            if (my_last == 'C' and opponent_last_move == 'C') or \
               (my_last == 'D' and opponent_last_move == 'C'):
                return my_last
            else:
                # Switch
                return 'D' if my_last == 'C' else 'C'

        elif self.strategy == Strategy.GRUDGER:
            if neighbor_id in self.history:
                # If ever defected, defect forever
                if 'D' in self.history[neighbor_id][1]:
                    return 'D'
            return 'C'

        elif self.strategy == Strategy.RANDOM:
            return 'C' if np.random.random() < 0.5 else 'D'

        return 'C'

    def play_game(self, neighbor_id, opponent_move, my_move):
        """Play one round and update scores"""
        # Prisoner's Dilemma payoffs
        if my_move == 'C' and opponent_move == 'C':
            payoff = 3
        elif my_move == 'C' and opponent_move == 'D':
            payoff = 0
        elif my_move == 'D' and opponent_move == 'C':
            payoff = 5
        else:  # Both defect
            payoff = 1

        self.score += payoff

        # Update history
        if neighbor_id not in self.history:
            self.history[neighbor_id] = ([], [])

        self.history[neighbor_id][0].append(my_move)
        self.history[neighbor_id][1].append(opponent_move)

        # Update cooperation rate
        total_moves = sum(len(h[0]) for h in self.history.values())
        if total_moves > 0:
            total_cooperations = sum(h[0].count('C') for h in self.history.values())
            self.cooperation_rate = total_cooperations / total_moves

    def update(self, neighbors, separation_weight=1.5, alignment_weight=1.0,
               cohesion_weight=1.0, perception_radius=50, max_speed=4):
        """Update position using Reynolds' rules"""
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


class GameTheorySwarm:
    """A swarm where boids play games with neighbors"""

    def __init__(self, num_boids=60, world_size=200, strategy_distribution=None):
        self.world_size = world_size
        self.boids = []

        if strategy_distribution is None:
            # Equal distribution of strategies
            strategy_distribution = {
                Strategy.ALWAYS_COOPERATE: 0.15,
                Strategy.ALWAYS_DEFECT: 0.15,
                Strategy.TIT_FOR_TAT: 0.25,
                Strategy.PAVLOV: 0.15,
                Strategy.GRUDGER: 0.15,
                Strategy.RANDOM: 0.15,
            }

        # Initialize boids with strategies
        for i in range(num_boids):
            x = np.random.uniform(0, world_size)
            y = np.random.uniform(0, world_size)
            angle = np.random.uniform(0, 2 * np.pi)
            speed = 2.0
            vx = speed * np.cos(angle)
            vy = speed * np.sin(angle)

            # Assign strategy based on distribution
            r = np.random.random()
            cumulative = 0
            assigned_strategy = Strategy.TIT_FOR_TAT
            for strategy, prob in strategy_distribution.items():
                cumulative += prob
                if r <= cumulative:
                    assigned_strategy = strategy
                    break

            self.boids.append(GameTheoryBoid(x, y, vx, vy, assigned_strategy, world_size))

        self.game_interaction_radius = 30  # Range for playing games

    def get_neighbors(self, boid, radius):
        """Get neighbors within radius"""
        neighbors = []
        for other in self.boids:
            if other is boid:
                continue
            dist = np.linalg.norm(boid.position - other.position)
            if dist < radius:
                neighbors.append(other)
        return neighbors

    def play_games(self):
        """Each boid plays games with nearby neighbors"""
        # Build neighbor pairs
        played_pairs = set()

        for i, boid in enumerate(self.boids):
            neighbors = self.get_neighbors(boid, self.game_interaction_radius)

            for neighbor in neighbors:
                j = self.boids.index(neighbor)
                if (i, j) in played_pairs or (j, i) in played_pairs:
                    continue

                # Get last moves
                boid_last = neighbor.history.get(i, ([], []))[1]
                neighbor_last = boid.history.get(j, ([], []))[1]

                boid_last_move = boid_last[-1] if boid_last else None
                neighbor_last_move = neighbor_last[-1] if neighbor_last else None

                # Decide moves
                boid_move = boid.decide_move(j, neighbor_last_move)
                neighbor_move = neighbor.decide_move(i, boid_last_move)

                # Play game
                boid.play_game(j, neighbor_move, boid_move)
                neighbor.play_game(i, boid_move, neighbor_move)

                played_pairs.add((i, j))

    def update(self):
        """Update swarm - play games then move"""
        # Play games
        self.play_games()

        # Update positions
        for boid in self.boids:
            neighbors = self.get_neighbors(boid, 50)
            boid.update(neighbors)

    def get_spatial_clustering(self):
        """Measure if cooperative strategies cluster spatially"""
        # For each strategy, calculate average distance to same-strategy neighbors
        clustering = {}

        for strategy in Strategy:
            strategy_boids = [b for b in self.boids if b.strategy == strategy]
            if len(strategy_boids) < 2:
                continue

            avg_dist_same = []
            avg_dist_diff = []

            for boid in strategy_boids:
                # Distance to same strategy
                same_dists = [np.linalg.norm(boid.position - other.position)
                             for other in strategy_boids if other is not boid]
                if same_dists:
                    avg_dist_same.append(np.mean(same_dists))

                # Distance to different strategies
                diff_boids = [b for b in self.boids if b.strategy != strategy]
                diff_dists = [np.linalg.norm(boid.position - other.position)
                             for other in diff_boids]
                if diff_dists:
                    avg_dist_diff.append(np.mean(diff_dists))

            if avg_dist_same and avg_dist_diff:
                # Clustering metric: ratio of avg distance (lower = more clustered)
                clustering[strategy] = np.mean(avg_dist_same) / np.mean(avg_dist_diff)

        return clustering


def visualize_swarm(swarm, steps=400, filename='game_theory_swarm.gif'):
    """Visualize the swarm with strategy colors"""
    print(f"Visualizing {steps} steps...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Swarm visualization
    ax1.set_xlim(0, swarm.world_size)
    ax1.set_ylim(0, swarm.world_size)
    ax1.set_aspect('equal')
    ax1.set_title('Game Theory Swarm (color = strategy)', fontsize=14)
    ax1.set_facecolor('#1a1a1a')

    positions = np.array([b.position for b in swarm.boids])
    colors = [b.color for b in swarm.boids]
    sizes = [100 for _ in swarm.boids]

    scatter = ax1.scatter(positions[:, 0], positions[:, 1],
                         c=colors, s=sizes, alpha=0.8, edgecolors='white', linewidth=0.5)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=(0.2, 0.8, 0.2), label='Always Cooperate'),
        Patch(facecolor=(0.8, 0.2, 0.2), label='Always Defect'),
        Patch(facecolor=(0.2, 0.6, 0.9), label='Tit for Tat'),
        Patch(facecolor=(0.9, 0.7, 0.2), label='Pavlov'),
        Patch(facecolor=(0.7, 0.2, 0.8), label='Grudger'),
        Patch(facecolor=(0.5, 0.5, 0.5), label='Random'),
    ]
    ax1.legend(handles=legend_elements, loc='upper right')

    # Stats visualization
    ax2.set_xlim(0, steps)
    ax2.set_ylim(0, 1)
    ax2.set_title('Cooperation Rates by Strategy', fontsize=14)
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Cooperation Rate')
    ax2.grid(True, alpha=0.3)

    strategy_lines = {}
    strategy_data = {s: [] for s in Strategy}

    for strategy in Strategy:
        line, = ax2.plot([], [], label=strategy.value, linewidth=2)
        strategy_lines[strategy] = line

    ax2.legend(loc='best')

    def update_frame(frame):
        if frame % 50 == 0:
            print(f"  Frame {frame}/{steps}")

        swarm.update()

        # Update positions
        positions = np.array([b.position for b in swarm.boids])
        scatter.set_offsets(positions)

        # Update cooperation rates
        for strategy in Strategy:
            strategy_boids = [b for b in swarm.boids if b.strategy == strategy]
            if strategy_boids:
                avg_coop = np.mean([b.cooperation_rate for b in strategy_boids])
                strategy_data[strategy].append(avg_coop)

                x_data = list(range(len(strategy_data[strategy])))
                strategy_lines[strategy].set_data(x_data, strategy_data[strategy])

        return scatter, *strategy_lines.values()

    anim = animation.FuncAnimation(fig, update_frame, frames=steps,
                                  interval=20, blit=False, repeat=False)

    plt.tight_layout()
    print(f"Saving animation...")
    anim.save(filename, writer='pillow', fps=30)
    print(f"✓ Saved to {filename}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Game theory swarms')
    parser.add_argument('--steps', type=int, default=300,
                       help='Simulation steps')
    parser.add_argument('--boids', type=int, default=60,
                       help='Number of boids')

    args = parser.parse_args()

    print("🎮🐦 Game Theory Swarms")
    print("   Spatial dynamics + strategic interaction")
    print("   Question: Do cooperative strategies cluster?\n")

    swarm = GameTheorySwarm(num_boids=args.boids)

    # Run simulation with visualization
    visualize_swarm(swarm, steps=args.steps)

    # Analyze clustering
    print("\n" + "=" * 70)
    print("SPATIAL CLUSTERING ANALYSIS")
    print("=" * 70)
    clustering = swarm.get_spatial_clustering()

    for strategy, ratio in sorted(clustering.items(), key=lambda x: x[1]):
        print(f"{strategy.value:20s}: {ratio:.3f} (< 1.0 = clustered)")

    print("\n" + "=" * 70)
    print("This hybrid combines:")
    print("  • Claude A's game theory strategies")
    print("  • Claude B's swarm movement")
    print("  • Spatial distribution of cooperation")
    print("=" * 70)


if __name__ == "__main__":
    main()
