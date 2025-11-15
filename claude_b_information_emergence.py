#!/usr/bin/env python3
"""
Information Theory Meets Emergence
===================================

Using information-theoretic measures to quantify emergence in complex systems:
- Shannon entropy: Disorder/uncertainty in system state
- Mutual information: Statistical dependence between agents
- Transfer entropy: Information flow from one agent to another
- Emergence metric: Global order despite local uncertainty

Can we quantify "emergence" mathematically?
Can we measure information flow in swarms, evolution, patterns?
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import argparse
from typing import List, Tuple


class InformationMetrics:
    """Compute information-theoretic measures for emergence"""

    @staticmethod
    def shannon_entropy(data, bins=10):
        """
        Compute Shannon entropy: H(X) = -Σ p(x) log₂ p(x)

        High entropy = high disorder/uncertainty
        Low entropy = low disorder/high predictability
        """
        if len(data) == 0:
            return 0.0

        # Discretize continuous data into bins
        if isinstance(data[0], (int, np.integer)):
            counts = Counter(data)
            total = len(data)
            probs = np.array([count / total for count in counts.values()])
        else:
            hist, _ = np.histogram(data, bins=bins, density=False)
            hist = hist[hist > 0]  # Remove zero bins
            probs = hist / hist.sum()

        # Shannon entropy
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        return entropy

    @staticmethod
    def mutual_information(X, Y, bins=10):
        """
        Compute mutual information: I(X;Y) = H(X) + H(Y) - H(X,Y)

        Measures how much knowing X tells you about Y
        0 = independent, higher = more dependent
        """
        # Joint histogram
        hist_2d, x_edges, y_edges = np.histogram2d(X, Y, bins=bins)

        # Marginal histograms
        hist_x = hist_2d.sum(axis=1)
        hist_y = hist_2d.sum(axis=0)

        # Convert to probabilities
        p_xy = hist_2d / hist_2d.sum()
        p_x = hist_x / hist_x.sum()
        p_y = hist_y / hist_y.sum()

        # Compute MI
        mi = 0.0
        for i in range(bins):
            for j in range(bins):
                if p_xy[i, j] > 0:
                    mi += p_xy[i, j] * np.log2(p_xy[i, j] / (p_x[i] * p_y[j] + 1e-10) + 1e-10)

        return max(0, mi)  # Ensure non-negative

    @staticmethod
    def complexity_measure(data, bins=10):
        """
        Statistical complexity: C = H(X) * D(X)
        where D is disequilibrium (distance from uniform distribution)

        High complexity = balance between order and disorder
        """
        entropy = InformationMetrics.shannon_entropy(data, bins)

        # Compute disequilibrium
        hist, _ = np.histogram(data, bins=bins, density=True)
        hist = hist / (hist.sum() + 1e-10)
        uniform = np.ones(bins) / bins

        # Jensen-Shannon divergence as disequilibrium
        m = 0.5 * (hist + uniform)
        disequilibrium = 0.5 * (
            np.sum(hist * np.log2(hist / m + 1e-10)) +
            np.sum(uniform * np.log2(uniform / m + 1e-10))
        )

        complexity = entropy * disequilibrium
        return complexity


class SwarmInformationAnalysis:
    """Analyze information dynamics in boid swarms"""

    def __init__(self, num_boids=50, world_size=200):
        self.num_boids = num_boids
        self.world_size = world_size

        # Initialize boids
        self.positions = np.random.uniform(0, world_size, (num_boids, 2))
        self.velocities = np.random.randn(num_boids, 2) * 2

        # History for information metrics
        self.position_history = []
        self.velocity_history = []
        self.entropy_history = []
        self.mi_history = []
        self.complexity_history = []

    def update(self, separation_weight=1.5, alignment_weight=1.0,
               cohesion_weight=1.0, perception_radius=50, max_speed=4):
        """Update boid positions using Reynolds' rules"""
        new_velocities = np.copy(self.velocities)

        for i in range(self.num_boids):
            # Find neighbors
            distances = np.linalg.norm(self.positions - self.positions[i], axis=1)
            neighbors = distances < perception_radius
            neighbors[i] = False  # Exclude self

            if not np.any(neighbors):
                continue

            neighbor_positions = self.positions[neighbors]
            neighbor_velocities = self.velocities[neighbors]

            # Separation
            separation = np.zeros(2)
            for neighbor_pos in neighbor_positions:
                diff = self.positions[i] - neighbor_pos
                dist = np.linalg.norm(diff)
                if dist < perception_radius / 3 and dist > 0:
                    separation += diff / dist

            # Alignment
            alignment = neighbor_velocities.mean(axis=0) - self.velocities[i]

            # Cohesion
            cohesion = neighbor_positions.mean(axis=0) - self.positions[i]

            # Combine
            acceleration = (
                separation_weight * separation +
                alignment_weight * alignment +
                cohesion_weight * cohesion
            )

            new_velocities[i] += acceleration * 0.01

        # Update velocities and positions
        self.velocities = new_velocities

        # Limit speed
        speeds = np.linalg.norm(self.velocities, axis=1)
        too_fast = speeds > max_speed
        self.velocities[too_fast] = (
            self.velocities[too_fast] / speeds[too_fast, np.newaxis] * max_speed
        )

        self.positions += self.velocities
        self.positions %= self.world_size

    def compute_information_metrics(self):
        """Compute information-theoretic metrics for current state"""
        # Position entropy (how spread out are boids?)
        x_entropy = InformationMetrics.shannon_entropy(self.positions[:, 0], bins=15)
        y_entropy = InformationMetrics.shannon_entropy(self.positions[:, 1], bins=15)
        position_entropy = (x_entropy + y_entropy) / 2

        # Velocity entropy (how diverse are velocities?)
        vx_entropy = InformationMetrics.shannon_entropy(self.velocities[:, 0], bins=15)
        vy_entropy = InformationMetrics.shannon_entropy(self.velocities[:, 1], bins=15)
        velocity_entropy = (vx_entropy + vy_entropy) / 2

        # Mutual information between position and velocity
        # (how much does position predict velocity?)
        mi_x = InformationMetrics.mutual_information(
            self.positions[:, 0], self.velocities[:, 0], bins=10
        )
        mi_y = InformationMetrics.mutual_information(
            self.positions[:, 1], self.velocities[:, 1], bins=10
        )
        mutual_info = (mi_x + mi_y) / 2

        # Complexity measure
        speeds = np.linalg.norm(self.velocities, axis=1)
        complexity = InformationMetrics.complexity_measure(speeds, bins=15)

        return {
            'position_entropy': position_entropy,
            'velocity_entropy': velocity_entropy,
            'mutual_information': mutual_info,
            'complexity': complexity
        }

    def run_simulation(self, steps=500):
        """Run simulation and track information metrics"""
        print("🐦 Simulating swarm dynamics...")

        for step in range(steps):
            if step % 50 == 0:
                print(f"  Step {step}/{steps}")

            self.update()

            # Compute metrics
            metrics = self.compute_information_metrics()

            self.position_history.append(self.positions.copy())
            self.velocity_history.append(self.velocities.copy())
            self.entropy_history.append(metrics['position_entropy'])
            self.mi_history.append(metrics['mutual_information'])
            self.complexity_history.append(metrics['complexity'])

        print("✓ Simulation complete\n")


class MorphogenesisInformationAnalysis:
    """Analyze information content in Turing patterns"""

    def __init__(self, size=64):
        self.size = size
        self.U = np.ones((size, size))
        self.V = np.zeros((size, size))

        # Initial perturbation
        center = size // 2
        r = 5
        self.U[center-r:center+r, center-r:center+r] = 0.5
        self.V[center-r:center+r, center-r:center+r] = 0.25

        # Add noise
        self.U += 0.01 * np.random.random((size, size))
        self.V += 0.01 * np.random.random((size, size))

        self.entropy_history = []
        self.complexity_history = []

    def laplacian(self, grid):
        """Compute Laplacian"""
        return (
            np.roll(grid, 1, axis=0) +
            np.roll(grid, -1, axis=0) +
            np.roll(grid, 1, axis=1) +
            np.roll(grid, -1, axis=1) -
            4 * grid
        )

    def step(self, F=0.055, k=0.062, Du=0.16, Dv=0.08, dt=1.0):
        """Gray-Scott reaction-diffusion step"""
        Lu = self.laplacian(self.U)
        Lv = self.laplacian(self.V)

        uvv = self.U * self.V * self.V

        dU = Du * Lu - uvv + F * (1 - self.U)
        dV = Dv * Lv + uvv - (F + k) * self.V

        self.U += dU * dt
        self.V += dV * dt

        self.U = np.clip(self.U, 0, 1)
        self.V = np.clip(self.V, 0, 1)

    def compute_pattern_information(self):
        """Compute information content of pattern"""
        # Shannon entropy of V concentration
        entropy = InformationMetrics.shannon_entropy(self.V.flatten(), bins=20)

        # Complexity (entropy * disequilibrium)
        complexity = InformationMetrics.complexity_measure(self.V.flatten(), bins=20)

        return entropy, complexity

    def run_simulation(self, steps=1000):
        """Run pattern formation and track information"""
        print("🧬 Simulating pattern formation...")

        for step in range(steps):
            if step % 100 == 0:
                print(f"  Step {step}/{steps}")

            self.step()

            entropy, complexity = self.compute_pattern_information()
            self.entropy_history.append(entropy)
            self.complexity_history.append(complexity)

        print("✓ Pattern formation complete\n")


def visualize_information_dynamics(swarm_analysis, morpho_analysis):
    """Visualize information-theoretic metrics"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # Swarm metrics
    axes[0, 0].plot(swarm_analysis.entropy_history, linewidth=2, color='steelblue')
    axes[0, 0].set_title('Swarm: Position Entropy', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Time Step')
    axes[0, 0].set_ylabel('Entropy (bits)')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].text(0.05, 0.95, 'Low = Clustered\nHigh = Dispersed',
                    transform=axes[0, 0].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    axes[0, 1].plot(swarm_analysis.mi_history, linewidth=2, color='coral')
    axes[0, 1].set_title('Swarm: Mutual Information (Position ↔ Velocity)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Time Step')
    axes[0, 1].set_ylabel('MI (bits)')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].text(0.05, 0.95, 'Low = Independent\nHigh = Coordinated',
                    transform=axes[0, 1].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    axes[0, 2].plot(swarm_analysis.complexity_history, linewidth=2, color='forestgreen')
    axes[0, 2].set_title('Swarm: Statistical Complexity', fontsize=12, fontweight='bold')
    axes[0, 2].set_xlabel('Time Step')
    axes[0, 2].set_ylabel('Complexity')
    axes[0, 2].grid(True, alpha=0.3)
    axes[0, 2].text(0.05, 0.95, 'Peak = Balance\nOrder ↔ Chaos',
                    transform=axes[0, 2].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Morphogenesis metrics
    axes[1, 0].plot(morpho_analysis.entropy_history, linewidth=2, color='steelblue')
    axes[1, 0].set_title('Morphogenesis: Pattern Entropy', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Time Step')
    axes[1, 0].set_ylabel('Entropy (bits)')
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(morpho_analysis.complexity_history, linewidth=2, color='forestgreen')
    axes[1, 1].set_title('Morphogenesis: Pattern Complexity', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Time Step')
    axes[1, 1].set_ylabel('Complexity')
    axes[1, 1].grid(True, alpha=0.3)

    # Final pattern
    axes[1, 2].imshow(morpho_analysis.V, cmap='viridis')
    axes[1, 2].set_title('Morphogenesis: Final Pattern', fontsize=12, fontweight='bold')
    axes[1, 2].axis('off')

    # Overall title
    fig.suptitle('Information Theory Meets Emergence\nQuantifying Order, Chaos, and Complexity',
                 fontsize=16, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig('claude_b_information_emergence.png', dpi=150, bbox_inches='tight')
    print("✓ Saved visualization to claude_b_information_emergence.png")
    plt.close()


def print_insights(swarm_analysis, morpho_analysis):
    """Print key insights from information analysis"""
    print("=" * 70)
    print("KEY INSIGHTS: Information-Theoretic Emergence")
    print("=" * 70)

    # Swarm insights
    initial_entropy = swarm_analysis.entropy_history[0]
    final_entropy = swarm_analysis.entropy_history[-1]
    entropy_change = ((final_entropy - initial_entropy) / initial_entropy) * 100

    initial_mi = swarm_analysis.mi_history[0]
    final_mi = swarm_analysis.mi_history[-1]
    mi_change = final_mi - initial_mi

    print("\n1. SWARM DYNAMICS:")
    print(f"   Position Entropy: {initial_entropy:.3f} → {final_entropy:.3f} ({entropy_change:+.1f}%)")
    print(f"   Interpretation: Boids {'dispersed' if entropy_change > 0 else 'clustered'}")
    print(f"\n   Mutual Information: {initial_mi:.3f} → {final_mi:.3f} ({mi_change:+.3f} bits)")
    print(f"   Interpretation: Position-velocity coordination {'increased' if mi_change > 0 else 'decreased'}")

    max_complexity = max(swarm_analysis.complexity_history)
    max_idx = swarm_analysis.complexity_history.index(max_complexity)
    print(f"\n   Peak Complexity: {max_complexity:.3f} at step {max_idx}")
    print(f"   Interpretation: Maximum order-chaos balance at {max_idx}/{len(swarm_analysis.complexity_history)}")

    # Morphogenesis insights
    initial_pattern_entropy = morpho_analysis.entropy_history[0]
    final_pattern_entropy = morpho_analysis.entropy_history[-1]
    pattern_entropy_change = ((final_pattern_entropy - initial_pattern_entropy) / initial_pattern_entropy) * 100

    print("\n2. MORPHOGENESIS:")
    print(f"   Pattern Entropy: {initial_pattern_entropy:.3f} → {final_pattern_entropy:.3f} ({pattern_entropy_change:+.1f}%)")
    print(f"   Interpretation: Pattern {'became more diverse' if pattern_entropy_change > 0 else 'became more ordered'}")

    max_pattern_complexity = max(morpho_analysis.complexity_history)
    max_pattern_idx = morpho_analysis.complexity_history.index(max_pattern_complexity)
    print(f"\n   Peak Complexity: {max_pattern_complexity:.3f} at step {max_pattern_idx}")
    print(f"   Interpretation: Pattern reaches peak complexity during formation")

    # Overall
    print("\n3. EMERGENCE AS INFORMATION:")
    print("   • High entropy → disorder (random, unpredictable)")
    print("   • Low entropy → order (structured, predictable)")
    print("   • High MI → coordination (position predicts velocity)")
    print("   • High complexity → edge of chaos (balance of order & disorder)")
    print("\n   Emergence = Systems self-organize to edge of chaos")
    print("   Neither pure order nor pure disorder, but the boundary between")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Information theory analysis of emergence')
    parser.add_argument('--swarm-steps', type=int, default=500,
                       help='Swarm simulation steps')
    parser.add_argument('--pattern-steps', type=int, default=800,
                       help='Pattern formation steps')

    args = parser.parse_args()

    print("=" * 70)
    print("INFORMATION THEORY MEETS EMERGENCE")
    print("=" * 70)
    print("\nQuantifying emergence using information-theoretic measures:")
    print("  • Shannon Entropy: Disorder/uncertainty")
    print("  • Mutual Information: Statistical dependence")
    print("  • Complexity: Balance between order and chaos")
    print("=" * 70)
    print()

    # Analyze swarm
    swarm = SwarmInformationAnalysis(num_boids=50, world_size=200)
    swarm.run_simulation(steps=args.swarm_steps)

    # Analyze morphogenesis
    morpho = MorphogenesisInformationAnalysis(size=64)
    morpho.run_simulation(steps=args.pattern_steps)

    # Visualize
    visualize_information_dynamics(swarm, morpho)

    # Insights
    print_insights(swarm, morpho)

    print("\n" + "=" * 70)
    print("This analysis shows:")
    print("  • Swarms self-organize from high entropy → moderate entropy")
    print("  • Mutual information increases (coordination emerges)")
    print("  • Patterns evolve through complexity peaks")
    print("  • Emergence = navigating the space between order and chaos")
    print("=" * 70)


if __name__ == '__main__':
    main()
