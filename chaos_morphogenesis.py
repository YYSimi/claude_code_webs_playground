#!/usr/bin/env python3
"""
Chaos-Driven Morphogenesis
Combining Claude A's strange attractors with Claude B's pattern formation

Lorenz attractor trajectory → Gray-Scott F/k parameters → evolving patterns
Watching chaos drive biological pattern formation
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import argparse


def lorenz(state, sigma=10.0, rho=28.0, beta=8.0/3.0, dt=0.01):
    """Lorenz attractor"""
    x, y, z = state
    dx = sigma * (y - x) * dt
    dy = (x * (rho - z) - y) * dt
    dz = (x * y - beta * z) * dt
    return np.array([x + dx, y + dy, z + dz])


class GrayScott:
    """Gray-Scott reaction-diffusion system with time-varying parameters"""

    def __init__(self, size=128, F=0.055, k=0.062, Du=0.16, Dv=0.08):
        self.size = size
        self.F = F  # Feed rate
        self.k = k  # Kill rate
        self.Du = Du  # Diffusion rate of U
        self.Dv = Dv  # Diffusion rate of V

        # Initialize concentrations
        self.U = np.ones((size, size))
        self.V = np.zeros((size, size))

        # Add initial perturbation in center
        center = size // 2
        r = 10
        self.U[center-r:center+r, center-r:center+r] = 0.50
        self.V[center-r:center+r, center-r:center+r] = 0.25

        # Add random noise
        self.U += 0.01 * np.random.random((size, size))
        self.V += 0.01 * np.random.random((size, size))

    def laplacian(self, grid):
        """Compute Laplacian (diffusion operator)"""
        laplacian = (
            np.roll(grid, 1, axis=0) +
            np.roll(grid, -1, axis=0) +
            np.roll(grid, 1, axis=1) +
            np.roll(grid, -1, axis=1) +
            0.5 * (
                np.roll(np.roll(grid, 1, axis=0), 1, axis=1) +
                np.roll(np.roll(grid, 1, axis=0), -1, axis=1) +
                np.roll(np.roll(grid, -1, axis=0), 1, axis=1) +
                np.roll(np.roll(grid, -1, axis=0), -1, axis=1)
            ) - 6 * grid
        )
        return laplacian

    def step(self, dt=1.0):
        """Update one time step"""
        Lu = self.laplacian(self.U)
        Lv = self.laplacian(self.V)

        uvv = self.U * self.V * self.V

        dU = self.Du * Lu - uvv + self.F * (1 - self.U)
        dV = self.Dv * Lv + uvv - (self.F + self.k) * self.V

        self.U += dU * dt
        self.V += dV * dt

        # Clamp values
        self.U = np.clip(self.U, 0, 1)
        self.V = np.clip(self.V, 0, 1)

    def update_parameters(self, F, k):
        """Update F and k parameters"""
        self.F = F
        self.k = k


class ChaosMorphogenesis:
    """Drive morphogenesis with chaotic dynamics"""

    def __init__(self, size=128):
        self.gs = GrayScott(size=size)

        # Lorenz attractor state
        self.attractor_state = np.array([1.0, 1.0, 1.0])

        # Parameter mapping ranges
        # We'll map Lorenz x to F, y to k
        # Lorenz x typically ranges roughly -20 to 20
        # Lorenz y typically ranges roughly -30 to 30
        self.F_range = (0.01, 0.09)  # Feed rate range
        self.k_range = (0.045, 0.07)  # Kill rate range

        self.history = {
            'F': [],
            'k': [],
            'x': [],
            'y': [],
            'z': []
        }

    def map_to_F(self, x):
        """Map Lorenz x to F parameter"""
        # Normalize x from roughly [-20, 20] to [0, 1]
        x_norm = (x + 20) / 40
        x_norm = np.clip(x_norm, 0, 1)
        # Map to F range
        return self.F_range[0] + x_norm * (self.F_range[1] - self.F_range[0])

    def map_to_k(self, y):
        """Map Lorenz y to k parameter"""
        # Normalize y from roughly [-30, 30] to [0, 1]
        y_norm = (y + 30) / 60
        y_norm = np.clip(y_norm, 0, 1)
        # Map to k range
        return self.k_range[0] + y_norm * (self.k_range[1] - self.k_range[0])

    def step(self):
        """Step both attractor and morphogenesis"""
        # Update Lorenz attractor
        self.attractor_state = lorenz(self.attractor_state)

        x, y, z = self.attractor_state

        # Map to parameters
        F = self.map_to_F(x)
        k = self.map_to_k(y)

        # Update Gray-Scott parameters
        self.gs.update_parameters(F, k)

        # Step morphogenesis
        self.gs.step()

        # Record history
        self.history['F'].append(F)
        self.history['k'].append(k)
        self.history['x'].append(x)
        self.history['y'].append(y)
        self.history['z'].append(z)

    def get_pattern(self):
        """Get current V concentration (the visible pattern)"""
        return self.gs.V


def create_animation(duration_steps=2000, size=128, filename='chaos_morpho.gif'):
    """Create animation of chaos-driven morphogenesis"""
    print("🌀🧬 Chaos-Driven Morphogenesis")
    print("   Lorenz attractor controlling Gray-Scott parameters")
    print(f"   Simulating {duration_steps} steps...\n")

    cm = ChaosMorphogenesis(size=size)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Pattern visualization
    ax1.set_title('Morphogenetic Pattern', fontsize=14)
    ax1.axis('off')
    im = ax1.imshow(cm.get_pattern(), cmap='viridis', vmin=0, vmax=1)

    # Parameter trajectory
    ax2.set_xlabel('Feed Rate (F)')
    ax2.set_ylabel('Kill Rate (k)')
    ax2.set_title('Parameter Space Trajectory (driven by Lorenz)', fontsize=14)
    ax2.set_xlim(cm.F_range[0], cm.F_range[1])
    ax2.set_ylim(cm.k_range[0], cm.k_range[1])
    ax2.grid(True, alpha=0.3)

    line, = ax2.plot([], [], 'b-', alpha=0.6, linewidth=1)
    point, = ax2.plot([], [], 'ro', markersize=8)

    # Text showing current parameters
    param_text = ax2.text(0.02, 0.98, '', transform=ax2.transAxes,
                         verticalalignment='top', fontfamily='monospace',
                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    def update(frame):
        if frame % 100 == 0:
            print(f"  Step {frame}/{duration_steps}")

        # Step simulation
        cm.step()

        # Update pattern
        im.set_array(cm.get_pattern())

        # Update trajectory
        if len(cm.history['F']) > 1:
            line.set_data(cm.history['F'], cm.history['k'])
            point.set_data([cm.history['F'][-1]], [cm.history['k'][-1]])

            # Update parameter text
            param_text.set_text(
                f"F = {cm.history['F'][-1]:.4f}\n"
                f"k = {cm.history['k'][-1]:.4f}\n"
                f"Lorenz:\n"
                f"  x = {cm.history['x'][-1]:.2f}\n"
                f"  y = {cm.history['y'][-1]:.2f}\n"
                f"  z = {cm.history['z'][-1]:.2f}"
            )

        return im, line, point, param_text

    anim = animation.FuncAnimation(fig, update, frames=duration_steps,
                                  interval=20, blit=False, repeat=False)

    plt.tight_layout()
    print(f"\nSaving animation to {filename}...")
    anim.save(filename, writer='pillow', fps=30)
    print("✓ Animation saved!")
    plt.close()

    return cm


def plot_parameter_trajectory(cm, filename='chaos_morpho_trajectory.png'):
    """Plot the full parameter trajectory"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Lorenz trajectory in 3D
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    ax.plot(cm.history['x'], cm.history['y'], cm.history['z'],
            'b-', alpha=0.6, linewidth=0.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Lorenz Attractor Trajectory')

    # Parameter space trajectory
    axes[0, 1].plot(cm.history['F'], cm.history['k'], 'b-', alpha=0.6, linewidth=1)
    axes[0, 1].scatter(cm.history['F'][0], cm.history['k'][0],
                      c='green', s=100, label='Start', zorder=5)
    axes[0, 1].scatter(cm.history['F'][-1], cm.history['k'][-1],
                      c='red', s=100, label='End', zorder=5)
    axes[0, 1].set_xlabel('Feed Rate (F)')
    axes[0, 1].set_ylabel('Kill Rate (k)')
    axes[0, 1].set_title('Gray-Scott Parameter Trajectory')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # F over time
    axes[1, 0].plot(cm.history['F'], 'b-', linewidth=1)
    axes[1, 0].set_xlabel('Time Step')
    axes[1, 0].set_ylabel('Feed Rate (F)')
    axes[1, 0].set_title('F Parameter Evolution')
    axes[1, 0].grid(True, alpha=0.3)

    # k over time
    axes[1, 1].plot(cm.history['k'], 'r-', linewidth=1)
    axes[1, 1].set_xlabel('Time Step')
    axes[1, 1].set_ylabel('Kill Rate (k)')
    axes[1, 1].set_title('k Parameter Evolution')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"✓ Trajectory plot saved to {filename}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Chaos-driven morphogenesis')
    parser.add_argument('--steps', type=int, default=1500,
                       help='Number of simulation steps')
    parser.add_argument('--size', type=int, default=128,
                       help='Grid size')

    args = parser.parse_args()

    # Create animation
    cm = create_animation(duration_steps=args.steps, size=args.size)

    # Plot trajectory
    plot_parameter_trajectory(cm)

    # Save final pattern
    plt.figure(figsize=(10, 10))
    plt.imshow(cm.get_pattern(), cmap='viridis')
    plt.title('Final Pattern (Chaos-Driven Morphogenesis)')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('chaos_morpho_final.png', dpi=300, bbox_inches='tight')
    print("✓ Final pattern saved to chaos_morpho_final.png")
    plt.close()

    print("\n" + "=" * 70)
    print("HYBRID COMPLETE")
    print("=" * 70)
    print("This system combines:")
    print("  • Claude A's Lorenz attractor (chaos theory)")
    print("  • Claude B's Gray-Scott reaction-diffusion (pattern formation)")
    print("\nChaos drives the parameters → patterns evolve over time")
    print("The Lorenz butterfly creates morphogenetic butterflies!")
    print("=" * 70)


if __name__ == "__main__":
    main()
