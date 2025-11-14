#!/usr/bin/env python3
"""
Morphogenesis: Pattern Formation in Nature
==========================================

Exploring how complex spatial patterns emerge from simple reaction-diffusion equations.

Alan Turing's 1952 paper showed how two chemicals (activator & inhibitor) with
different diffusion rates can spontaneously create patterns - explaining zebra
stripes, leopard spots, and countless other biological patterns.

Systems implemented:
1. Gray-Scott reaction-diffusion (spots, stripes, spirals, chaos)
2. Turing patterns (multiple parameter sets)
3. Pattern evolution animation
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import argparse


class ReactionDiffusion:
    """Base class for reaction-diffusion systems."""

    def __init__(self, size, dx=1.0, dt=1.0):
        self.size = size
        self.dx = dx
        self.dt = dt

    def laplacian(self, field):
        """Compute discrete Laplacian (diffusion operator) with periodic boundaries."""
        laplacian = (
            np.roll(field, 1, axis=0) +
            np.roll(field, -1, axis=0) +
            np.roll(field, 1, axis=1) +
            np.roll(field, -1, axis=1) +
            -4 * field
        )
        return laplacian / (self.dx ** 2)


class GrayScott(ReactionDiffusion):
    """
    Gray-Scott reaction-diffusion model.

    Two chemicals U (activator) and V (inhibitor) react:
        U + 2V → 3V  (autocatalytic reaction)
        V → P        (decay)

    Equations:
        dU/dt = Du·∇²U - UV² + F(1-U)
        dV/dt = Dv·∇²V + UV² - (F+k)V

    Different (F, k) parameters create different patterns:
    - Spots, stripes, spirals, moving waves, chaos
    """

    def __init__(self, size=256, Du=0.16, Dv=0.08, F=0.060, k=0.062, dx=1.0, dt=1.0):
        super().__init__(size, dx, dt)
        self.Du = Du  # Diffusion rate of U
        self.Dv = Dv  # Diffusion rate of V
        self.F = F    # Feed rate
        self.k = k    # Kill rate

        # Initialize fields
        self.U = np.ones((size, size))
        self.V = np.zeros((size, size))

        # Add small perturbation in center to seed pattern formation
        center = size // 2
        r = 20
        y, x = np.ogrid[-center:size-center, -center:size-center]
        mask = x*x + y*y <= r*r
        self.U[mask] = 0.5
        self.V[mask] = 0.25

        # Add noise
        self.U += np.random.uniform(-0.01, 0.01, (size, size))
        self.V += np.random.uniform(-0.01, 0.01, (size, size))

    def step(self):
        """Evolve the system one time step."""
        # Compute Laplacians (diffusion)
        Lu = self.laplacian(self.U)
        Lv = self.laplacian(self.V)

        # Reaction terms
        UVV = self.U * self.V * self.V

        # Update equations
        self.U += self.dt * (self.Du * Lu - UVV + self.F * (1 - self.U))
        self.V += self.dt * (self.Dv * Lv + UVV - (self.F + self.k) * self.V)

        # Ensure stability
        self.U = np.clip(self.U, 0, 1)
        self.V = np.clip(self.V, 0, 1)


class TuringPattern(ReactionDiffusion):
    """
    Classic Turing instability pattern formation.

    Simpler model focusing on the activator-inhibitor mechanism.
    """

    def __init__(self, size=256, Da=0.5, Di=1.0, ra=0.02, ri=0.04, dx=1.0, dt=0.5):
        super().__init__(size, dx, dt)
        self.Da = Da  # Activator diffusion
        self.Di = Di  # Inhibitor diffusion (faster than activator - key!)
        self.ra = ra  # Activator reaction rate
        self.ri = ri  # Inhibitor reaction rate

        # Initialize with small random noise
        self.A = np.random.uniform(0.4, 0.6, (size, size))  # Activator
        self.I = np.random.uniform(0.4, 0.6, (size, size))  # Inhibitor

    def step(self):
        """Evolve one time step."""
        La = self.laplacian(self.A)
        Li = self.laplacian(self.I)

        # Activator-inhibitor dynamics
        # Activator activates itself and inhibitor
        # Inhibitor suppresses activator
        dA = self.ra * self.A * (1 - self.I) + self.Da * La
        dI = self.ri * self.A - self.ri * self.I + self.Di * Li

        self.A += self.dt * dA
        self.I += self.dt * dI

        # Keep stable
        self.A = np.clip(self.A, 0, 1)
        self.I = np.clip(self.I, 0, 1)


def simulate_grayscott(pattern_type='spots', size=256, steps=10000, snapshot_interval=1000):
    """
    Simulate Gray-Scott model with different parameter sets.

    Pattern types and their (F, k) parameters:
    - 'spots': (0.060, 0.062) - stable spots
    - 'stripes': (0.035, 0.065) - maze-like stripes
    - 'waves': (0.014, 0.054) - moving wave patterns
    - 'chaos': (0.026, 0.051) - chaotic dynamics
    - 'spirals': (0.018, 0.051) - spiral waves
    """
    params = {
        'spots': (0.060, 0.062),
        'stripes': (0.035, 0.065),
        'waves': (0.014, 0.054),
        'chaos': (0.026, 0.051),
        'spirals': (0.018, 0.051)
    }

    F, k = params[pattern_type]
    print(f"\nGray-Scott: {pattern_type} pattern")
    print(f"  Parameters: F={F}, k={k}")
    print(f"  Simulating {steps} steps...")

    gs = GrayScott(size=size, F=F, k=k)

    # Take snapshots at intervals
    snapshots = []
    snapshot_steps = []

    for step in range(steps):
        gs.step()

        if step % snapshot_interval == 0 or step == steps - 1:
            snapshots.append(gs.V.copy())
            snapshot_steps.append(step)
            print(f"    Step {step}/{steps}")

    return snapshots, snapshot_steps


def simulate_turing(size=256, steps=5000, snapshot_interval=500):
    """Simulate classic Turing pattern formation."""
    print(f"\nTuring pattern formation")
    print(f"  Simulating {steps} steps...")

    turing = TuringPattern(size=size)

    snapshots = []
    snapshot_steps = []

    for step in range(steps):
        turing.step()

        if step % snapshot_interval == 0 or step == steps - 1:
            snapshots.append(turing.A.copy())
            snapshot_steps.append(step)
            print(f"    Step {step}/{steps}")

    return snapshots, snapshot_steps


def visualize_pattern_evolution(snapshots, snapshot_steps, title, filename):
    """Create a figure showing pattern evolution over time."""
    n_snapshots = len(snapshots)
    cols = 4
    rows = (n_snapshots + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(16, 4*rows))
    axes = axes.flatten() if n_snapshots > 1 else [axes]

    # Custom colormap (organic-looking)
    colors = ['#0d0887', '#7e03a8', '#cc4778', '#f89540', '#f0f921']
    cmap = LinearSegmentedColormap.from_list('custom', colors)

    for idx, (snapshot, step) in enumerate(zip(snapshots, snapshot_steps)):
        ax = axes[idx]
        im = ax.imshow(snapshot, cmap=cmap, interpolation='bilinear')
        ax.set_title(f'Step {step}', fontsize=12)
        ax.axis('off')

    # Hide unused subplots
    for idx in range(n_snapshots, len(axes)):
        axes[idx].axis('off')

    plt.suptitle(title, fontsize=16, y=0.98)
    plt.colorbar(im, ax=axes, orientation='horizontal', pad=0.02, shrink=0.8)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"  Saved {filename}")
    plt.close()


def create_pattern_animation(pattern_type='spots', size=256, frames=300, frame_skip=10):
    """Create animation of pattern formation."""
    params = {
        'spots': (0.060, 0.062),
        'stripes': (0.035, 0.065),
        'waves': (0.014, 0.054),
        'chaos': (0.026, 0.051),
        'spirals': (0.018, 0.051)
    }

    F, k = params[pattern_type]
    print(f"\nCreating animation: {pattern_type}")

    gs = GrayScott(size=size, F=F, k=k)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axis('off')

    colors = ['#0d0887', '#7e03a8', '#cc4778', '#f89540', '#f0f921']
    cmap = LinearSegmentedColormap.from_list('custom', colors)

    im = ax.imshow(gs.V, cmap=cmap, interpolation='bilinear')
    title = ax.text(0.5, 1.02, '', transform=ax.transAxes, ha='center', fontsize=14)

    def update(frame):
        for _ in range(frame_skip):
            gs.step()

        im.set_data(gs.V)
        title.set_text(f'{pattern_type.capitalize()} Pattern - Step {frame * frame_skip}')
        return [im, title]

    anim = animation.FuncAnimation(fig, update, frames=frames, interval=50, blit=True)

    filename = f'claude_b_morpho_{pattern_type}.gif'
    print(f"  Generating {filename}...")
    anim.save(filename, writer='pillow', fps=20)
    print(f"  Saved {filename}")
    plt.close()


def compare_patterns():
    """Generate comparison of different Gray-Scott patterns."""
    pattern_types = ['spots', 'stripes', 'waves', 'spirals']

    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.flatten()

    colors = ['#0d0887', '#7e03a8', '#cc4778', '#f89540', '#f0f921']
    cmap = LinearSegmentedColormap.from_list('custom', colors)

    print("\nGenerating pattern comparison...")

    for idx, pattern_type in enumerate(pattern_types):
        params = {
            'spots': (0.060, 0.062),
            'stripes': (0.035, 0.065),
            'waves': (0.014, 0.054),
            'spirals': (0.018, 0.051)
        }

        F, k = params[pattern_type]
        print(f"  {pattern_type}...")

        gs = GrayScott(size=256, F=F, k=k)

        # Evolve to steady state
        for _ in range(10000):
            gs.step()

        ax = axes[idx]
        im = ax.imshow(gs.V, cmap=cmap, interpolation='bilinear')
        ax.set_title(f'{pattern_type.capitalize()}\nF={F}, k={k}', fontsize=14)
        ax.axis('off')

    plt.suptitle('Gray-Scott Patterns: Same Equations, Different Parameters', fontsize=16, y=0.98)
    plt.tight_layout()
    plt.savefig('claude_b_morpho_comparison.png', dpi=150, bbox_inches='tight')
    print("  Saved claude_b_morpho_comparison.png")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Morphogenesis: Reaction-Diffusion Patterns')
    parser.add_argument('--mode', choices=['spots', 'stripes', 'waves', 'spirals',
                                           'turing', 'compare', 'animate', 'all'],
                        default='all', help='Pattern type to generate')
    parser.add_argument('--size', type=int, default=256, help='Grid size')
    parser.add_argument('--steps', type=int, default=10000, help='Simulation steps')

    args = parser.parse_args()

    print("=" * 70)
    print("MORPHOGENESIS: How Patterns Form from Simple Chemical Reactions")
    print("=" * 70)
    print("\nAlan Turing (1952): Two chemicals with different diffusion rates")
    print("can spontaneously break symmetry and create patterns.")
    print("\nThis explains: zebra stripes, leopard spots, fish patterns,")
    print("shell patterns, and countless other biological phenomena.")
    print("=" * 70)

    if args.mode == 'all':
        # Generate pattern comparison
        compare_patterns()

        # Generate one detailed evolution
        snapshots, steps = simulate_grayscott('spots', size=args.size, steps=args.steps, snapshot_interval=1000)
        visualize_pattern_evolution(snapshots, steps,
                                     'Spots: Pattern Formation Over Time',
                                     'claude_b_morpho_spots_evolution.png')

        # Generate Turing pattern
        snapshots, steps = simulate_turing(size=args.size, steps=5000, snapshot_interval=500)
        visualize_pattern_evolution(snapshots, steps,
                                     'Classic Turing Pattern Formation',
                                     'claude_b_morpho_turing_evolution.png')

        # Create one animation
        create_pattern_animation('stripes', size=256, frames=200, frame_skip=20)

    elif args.mode == 'compare':
        compare_patterns()

    elif args.mode == 'turing':
        snapshots, steps = simulate_turing(size=args.size, steps=args.steps)
        visualize_pattern_evolution(snapshots, steps,
                                     'Classic Turing Pattern Formation',
                                     'claude_b_morpho_turing_evolution.png')

    elif args.mode == 'animate':
        for pattern in ['spots', 'stripes', 'waves', 'spirals']:
            create_pattern_animation(pattern, size=256, frames=200, frame_skip=20)

    else:
        # Individual pattern
        snapshots, steps = simulate_grayscott(args.mode, size=args.size, steps=args.steps)
        visualize_pattern_evolution(snapshots, steps,
                                     f'{args.mode.capitalize()}: Pattern Evolution',
                                     f'claude_b_morpho_{args.mode}.png')

    print("\n" + "=" * 70)
    print("Key Insight: Pattern formation requires two ingredients:")
    print("  1. Short-range activation (autocatalysis)")
    print("  2. Long-range inhibition (faster diffusion of inhibitor)")
    print("\nFrom these simple rules → zebra stripes, leopard spots, nature's art")
    print("=" * 70)


if __name__ == '__main__':
    main()
