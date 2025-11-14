#!/usr/bin/env python3
"""
Chaos-Driven Morphogenesis - A Hybrid System
=============================================

Combining:
- Claude A's strange attractors (Lorenz, Rössler, Aizawa)
- Claude B's reaction-diffusion morphogenesis (Gray-Scott patterns)

The Concept:
Instead of static parameters, the chaos attractor's trajectory
drives the reaction-diffusion parameters through time.

Lorenz attractor coordinates → Gray-Scott F/k parameters
→ Patterns evolve: spots → stripes → waves → spirals → chaos

This creates DYNAMIC morphogenesis - patterns that flow and transform
driven by deterministic chaos.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import argparse


# ============================================================================
# Strange Attractors (from Claude A)
# ============================================================================

def lorenz_step(state, sigma=10.0, rho=28.0, beta=8.0/3.0, dt=0.01):
    """One step of Lorenz attractor"""
    x, y, z = state
    dx = sigma * (y - x) * dt
    dy = (x * (rho - z) - y) * dt
    dz = (x * y - beta * z) * dt
    return np.array([x + dx, y + dy, z + dz])


def rossler_step(state, a=0.2, b=0.2, c=5.7, dt=0.01):
    """One step of Rössler attractor"""
    x, y, z = state
    dx = (-y - z) * dt
    dy = (x + a * y) * dt
    dz = (b + z * (x - c)) * dt
    return np.array([x + dx, y + dy, z + dz])


def aizawa_step(state, a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1, dt=0.01):
    """One step of Aizawa attractor"""
    x, y, z = state
    dx = ((z - b) * x - d * y) * dt
    dy = (d * x + (z - b) * y) * dt
    dz = (c + a * z - (z**3)/3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3) * dt
    return np.array([x + dx, y + dy, z + dz])


# ============================================================================
# Reaction-Diffusion (from Claude B)
# ============================================================================

class ChaosDrivenGrayScott:
    """Gray-Scott reaction-diffusion with chaos-controlled parameters"""

    def __init__(self, size=128, Du=0.16, Dv=0.08, attractor_func=lorenz_step,
                 attractor_state=None):
        self.size = size
        self.Du = Du
        self.Dv = Dv

        # Attractor state
        if attractor_state is None:
            attractor_state = [1.0, 1.0, 1.0]
        self.attractor_state = np.array(attractor_state, dtype=float)
        self.attractor_func = attractor_func

        # Warmup attractor to get onto the attractor
        for _ in range(1000):
            self.attractor_state = self.attractor_func(self.attractor_state)

        # Initialize chemical concentrations
        self.U = np.ones((size, size))
        self.V = np.zeros((size, size))

        # Seed pattern in center
        center = size // 2
        r = 20
        y, x = np.ogrid[-center:size-center, -center:size-center]
        mask = x*x + y*y <= r*r
        self.U[mask] = 0.5
        self.V[mask] = 0.25

        # Add noise
        self.U += np.random.uniform(-0.01, 0.01, (size, size))
        self.V += np.random.uniform(-0.01, 0.01, (size, size))

        # Track attractor path
        self.attractor_history = []

    def map_attractor_to_params(self):
        """Map attractor coordinates to Gray-Scott F/k parameters

        Different regions of the attractor → different pattern types:
        - Spots: F~0.060, k~0.062
        - Stripes: F~0.035, k~0.065
        - Waves: F~0.014, k~0.054
        - Spirals: F~0.018, k~0.051

        We'll map attractor x,y,z to explore this parameter space
        """
        x, y, z = self.attractor_state

        # Normalize attractor coordinates (Lorenz typical range)
        # X: -20 to 20, Y: -30 to 30, Z: 0 to 50
        x_norm = (x + 20) / 40  # 0 to 1
        z_norm = z / 50  # 0 to 1

        # Map to F and k ranges
        # F range: 0.010 to 0.070
        # k range: 0.045 to 0.070
        F = 0.010 + x_norm * 0.060
        k = 0.045 + z_norm * 0.025

        # Clamp to valid ranges
        F = np.clip(F, 0.010, 0.070)
        k = np.clip(k, 0.045, 0.070)

        return F, k

    def laplacian(self, field):
        """Compute discrete Laplacian with periodic boundaries"""
        return (
            np.roll(field, 1, axis=0) +
            np.roll(field, -1, axis=0) +
            np.roll(field, 1, axis=1) +
            np.roll(field, -1, axis=1) -
            4 * field
        )

    def step(self, dt=1.0):
        """One Gray-Scott step with chaos-driven parameters"""
        # Update attractor state
        self.attractor_state = self.attractor_func(self.attractor_state)
        self.attractor_history.append(self.attractor_state.copy())

        # Get current F, k from attractor
        F, k = self.map_attractor_to_params()

        # Compute Laplacians
        Lu = self.laplacian(self.U)
        Lv = self.laplacian(self.V)

        # Reaction term
        UVV = self.U * self.V * self.V

        # Gray-Scott equations
        self.U += dt * (self.Du * Lu - UVV + F * (1 - self.U))
        self.V += dt * (self.Dv * Lv + UVV - (F + k) * self.V)

        # Keep stable
        self.U = np.clip(self.U, 0, 1)
        self.V = np.clip(self.V, 0, 1)

        return F, k


# ============================================================================
# Visualization
# ============================================================================

def create_chaos_morphogenesis_animation(attractor_name='lorenz', size=128,
                                        frames=300, steps_per_frame=5,
                                        filename='chaos_morphogenesis.gif'):
    """Create animation of chaos-driven pattern formation"""

    print(f"\nGenerating chaos-driven morphogenesis with {attractor_name} attractor...")
    print(f"  Grid size: {size}x{size}")
    print(f"  Frames: {frames}")
    print(f"  The attractor drives the pattern through parameter space\n")

    # Select attractor
    attractors = {
        'lorenz': (lorenz_step, [1.0, 1.0, 1.0]),
        'rossler': (rossler_step, [1.0, 1.0, 1.0]),
        'aizawa': (aizawa_step, [0.1, 0.0, 0.0])
    }

    attractor_func, initial_state = attractors[attractor_name]

    # Create system
    system = ChaosDrivenGrayScott(
        size=size,
        attractor_func=attractor_func,
        attractor_state=initial_state
    )

    # Create figure with two subplots
    fig = plt.figure(figsize=(14, 6))

    # Left: Pattern
    ax_pattern = plt.subplot(1, 2, 1)
    ax_pattern.set_title('Chaos-Driven Morphogenesis')
    ax_pattern.axis('off')

    # Right: Attractor trajectory in F-k space
    ax_params = plt.subplot(1, 2, 2)
    ax_params.set_xlabel('Feed Rate (F)')
    ax_params.set_ylabel('Kill Rate (k)')
    ax_params.set_title('Attractor Path in Parameter Space')
    ax_params.grid(True, alpha=0.3)

    # Mark known pattern regions
    ax_params.text(0.060, 0.062, 'Spots', fontsize=8, alpha=0.5)
    ax_params.text(0.035, 0.065, 'Stripes', fontsize=8, alpha=0.5)
    ax_params.text(0.014, 0.054, 'Waves', fontsize=8, alpha=0.5)
    ax_params.text(0.018, 0.051, 'Spirals', fontsize=8, alpha=0.5)

    # Colormap
    colors = ['#0d0887', '#7e03a8', '#cc4778', '#f89540', '#f0f921']
    cmap = LinearSegmentedColormap.from_list('custom', colors)

    # Initialize plots
    im = ax_pattern.imshow(system.V, cmap=cmap, interpolation='bilinear',
                          vmin=0, vmax=1)

    param_line, = ax_params.plot([], [], 'cyan', linewidth=1, alpha=0.6)
    param_point, = ax_params.plot([], [], 'ro', markersize=8)

    F_history = []
    k_history = []

    def update(frame):
        # Run several steps per frame for faster evolution
        for _ in range(steps_per_frame):
            F, k = system.step()

        # Update pattern
        im.set_data(system.V)

        # Track parameters
        F_history.append(F)
        k_history.append(k)

        # Update parameter space plot
        param_line.set_data(F_history, k_history)
        param_point.set_data([F], [k])

        # Set axis limits if not yet set
        if frame == 0:
            ax_params.set_xlim(0.010, 0.070)
            ax_params.set_ylim(0.045, 0.070)

        # Title with current parameters
        ax_pattern.set_title(f'Frame {frame}: F={F:.4f}, k={k:.4f}')

        return [im, param_line, param_point]

    anim = animation.FuncAnimation(fig, update, frames=frames,
                                  interval=50, blit=True)

    print(f"Saving animation to {filename}...")
    anim.save(filename, writer='pillow', fps=20)
    print(f"✓ Saved {filename}")

    plt.close()

    # Create final frame
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(system.V, cmap=cmap, interpolation='bilinear')
    ax.axis('off')
    final_F, final_k = system.map_attractor_to_params()
    ax.set_title(f'Final Pattern (F={final_F:.4f}, k={final_k:.4f})',
                fontsize=14)
    plt.savefig(filename.replace('.gif', '_final.png'), dpi=150, bbox_inches='tight')
    print(f"✓ Saved {filename.replace('.gif', '_final.png')}")
    plt.close()


def create_comparison(size=128):
    """Create comparison of different attractors driving morphogenesis"""
    attractors = ['lorenz', 'rossler', 'aizawa']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = ['#0d0887', '#7e03a8', '#cc4778', '#f89540', '#f0f921']
    cmap = LinearSegmentedColormap.from_list('custom', colors)

    print("\nGenerating attractor comparison...")

    for idx, attractor_name in enumerate(attractors):
        print(f"  {attractor_name}...")

        attractor_funcs = {
            'lorenz': (lorenz_step, [1.0, 1.0, 1.0]),
            'rossler': (rossler_step, [1.0, 1.0, 1.0]),
            'aizawa': (aizawa_step, [0.1, 0.0, 0.0])
        }

        attractor_func, initial_state = attractor_funcs[attractor_name]

        system = ChaosDrivenGrayScott(
            size=size,
            attractor_func=attractor_func,
            attractor_state=initial_state
        )

        # Evolve
        for _ in range(2000):
            system.step()

        # Plot
        ax = axes[idx]
        ax.imshow(system.V, cmap=cmap, interpolation='bilinear')
        ax.set_title(f'{attractor_name.capitalize()} Attractor', fontsize=12)
        ax.axis('off')

    plt.suptitle('Chaos-Driven Morphogenesis: Different Attractors', fontsize=14)
    plt.tight_layout()
    plt.savefig('chaos_morpho_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved chaos_morpho_comparison.png")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Chaos-driven morphogenesis')
    parser.add_argument('--attractor', choices=['lorenz', 'rossler', 'aizawa', 'all'],
                       default='lorenz', help='Which attractor to use')
    parser.add_argument('--size', type=int, default=128, help='Grid size')
    parser.add_argument('--frames', type=int, default=300, help='Animation frames')

    args = parser.parse_args()

    print("=" * 70)
    print("CHAOS-DRIVEN MORPHOGENESIS")
    print("=" * 70)
    print("\nA hybrid combining:")
    print("  - Claude A's strange attractors (deterministic chaos)")
    print("  - Claude B's reaction-diffusion (pattern formation)")
    print("\nAttractor trajectory → parameter space → evolving patterns")
    print("=" * 70)

    if args.attractor == 'all':
        # Create comparison
        create_comparison(size=args.size)

        # Animate each
        for attractor in ['lorenz', 'rossler', 'aizawa']:
            create_chaos_morphogenesis_animation(
                attractor_name=attractor,
                size=args.size,
                frames=args.frames,
                filename=f'chaos_morpho_{attractor}.gif'
            )
    else:
        create_chaos_morphogenesis_animation(
            attractor_name=args.attractor,
            size=args.size,
            frames=args.frames,
            filename=f'chaos_morpho_{args.attractor}.gif'
        )

    print("\n" + "=" * 70)
    print("HYBRID COMPLETE")
    print("=" * 70)
    print("\nKey insight: Chaos drives order. The deterministic but")
    print("unpredictable trajectory of the attractor creates ever-changing")
    print("patterns. Same equations, but the pattern never repeats.")
    print("\nThis is emergence at multiple levels:")
    print("  1. Attractor: Simple equations → chaotic trajectory")
    print("  2. Patterns: Local reactions → global morphogenesis")
    print("  3. Hybrid: Chaos → evolving order")
    print("=" * 70)


if __name__ == '__main__':
    main()
