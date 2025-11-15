#!/usr/bin/env python3
"""
Self-Organizing Criticality
Systems that naturally evolve to critical states where avalanches of all sizes occur

Classic example: Bak-Tang-Wiesenfeld sandpile model
The system self-organizes to a critical state where adding a single grain
can trigger avalanches of any size, following power-law distributions.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import defaultdict
import argparse


class Sandpile:
    """Bak-Tang-Wiesenfeld sandpile model"""

    def __init__(self, size=100, critical_height=4):
        self.size = size
        self.critical_height = critical_height
        self.grid = np.zeros((size, size), dtype=int)

        # Statistics
        self.avalanche_sizes = []
        self.avalanche_durations = []
        self.current_avalanche_size = 0
        self.current_avalanche_duration = 0

    def add_grain(self, x=None, y=None):
        """Add a grain of sand at (x,y) or random location"""
        if x is None or y is None:
            x = np.random.randint(0, self.size)
            y = np.random.randint(0, self.size)

        self.grid[x, y] += 1

        # Trigger avalanche if needed
        avalanche_occurred = self.topple()

        if avalanche_occurred:
            self.avalanche_sizes.append(self.current_avalanche_size)
            self.avalanche_durations.append(self.current_avalanche_duration)
            self.current_avalanche_size = 0
            self.current_avalanche_duration = 0

        return avalanche_occurred

    def topple(self):
        """Topple unstable sites until system stabilizes"""
        avalanche = False
        self.current_avalanche_size = 0
        self.current_avalanche_duration = 0

        while True:
            # Find unstable sites
            unstable = self.grid >= self.critical_height

            if not unstable.any():
                break

            avalanche = True
            self.current_avalanche_size += np.sum(unstable)
            self.current_avalanche_duration += 1

            # Topple all unstable sites simultaneously
            toppled = unstable.astype(int)

            # Each toppling site loses 4 grains
            self.grid -= toppled * self.critical_height

            # Distribute to neighbors (with boundary conditions - grains fall off edges)
            # Right neighbor
            self.grid[:, 1:] += toppled[:, :-1]
            # Left neighbor
            self.grid[:, :-1] += toppled[:, 1:]
            # Down neighbor
            self.grid[1:, :] += toppled[:-1, :]
            # Up neighbor
            self.grid[:-1, :] += toppled[1:, :]

        return avalanche

    def evolve_to_criticality(self, num_grains=100000, record_interval=1000):
        """Add many grains to drive system to critical state"""
        print(f"Evolving sandpile to criticality ({num_grains} grains)...")

        for i in range(num_grains):
            self.add_grain()

            if (i + 1) % record_interval == 0:
                print(f"  {i+1}/{num_grains} grains added, "
                      f"{len(self.avalanche_sizes)} avalanches recorded")

        print(f"✓ System reached criticality")
        print(f"  Total avalanches: {len(self.avalanche_sizes)}")
        print(f"  Mean height: {np.mean(self.grid):.2f}")

    def get_power_law_stats(self):
        """Analyze power-law distribution of avalanche sizes"""
        if len(self.avalanche_sizes) == 0:
            return None, None

        # Bin the avalanche sizes
        sizes = np.array(self.avalanche_sizes)
        sizes = sizes[sizes > 0]  # Remove zero-size avalanches

        # Create logarithmic bins
        max_size = max(sizes)
        if max_size < 10:
            return None, None

        bins = np.logspace(0, np.log10(max_size), 20)
        hist, bin_edges = np.histogram(sizes, bins=bins)

        # Calculate bin centers
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Remove empty bins
        mask = hist > 0
        bin_centers = bin_centers[mask]
        hist = hist[mask]

        # Fit power law: P(s) ~ s^(-α)
        # log(P(s)) = -α * log(s) + const
        if len(bin_centers) > 3:
            coeffs = np.polyfit(np.log10(bin_centers), np.log10(hist), 1)
            alpha = -coeffs[0]
        else:
            alpha = None

        return bin_centers, hist, alpha


class ForestFire:
    """Forest fire model - another SOC system"""

    def __init__(self, size=100, p_grow=0.01, p_lightning=0.0001):
        self.size = size
        self.p_grow = p_grow  # Probability tree grows
        self.p_lightning = p_lightning  # Probability lightning strikes

        # States: 0=empty, 1=tree, 2=burning
        self.grid = np.random.choice([0, 1], size=(size, size), p=[0.5, 0.5])

        self.fire_sizes = []

    def step(self):
        """One time step of forest fire dynamics"""
        new_grid = self.grid.copy()

        # Trees grow on empty sites
        empty = self.grid == 0
        grow = np.random.random((self.size, self.size)) < self.p_grow
        new_grid[empty & grow] = 1

        # Lightning strikes trees
        trees = self.grid == 1
        lightning = np.random.random((self.size, self.size)) < self.p_lightning
        new_grid[trees & lightning] = 2

        # Fire spreads to neighboring trees
        burning = self.grid == 2
        if burning.any():
            fire_size = self.spread_fire(new_grid, burning)
            if fire_size > 0:
                self.fire_sizes.append(fire_size)

        # Burning sites become empty
        new_grid[self.grid == 2] = 0

        self.grid = new_grid

    def spread_fire(self, grid, burning):
        """Spread fire from burning sites to neighbors"""
        fire_size = 0
        to_burn = burning.copy()

        while to_burn.any():
            fire_size += np.sum(to_burn)

            # Find trees adjacent to burning sites
            neighbors_burning = np.zeros_like(grid, dtype=bool)

            # Check all 4 directions
            neighbors_burning[1:, :] |= to_burn[:-1, :]   # Up
            neighbors_burning[:-1, :] |= to_burn[1:, :]   # Down
            neighbors_burning[:, 1:] |= to_burn[:, :-1]   # Left
            neighbors_burning[:, :-1] |= to_burn[:, 1:]   # Right

            # Only trees can catch fire
            trees = grid == 1
            to_burn = neighbors_burning & trees

            # Mark as burning
            grid[to_burn] = 2

        return fire_size


def visualize_sandpile(sandpile, steps=500, filename='sandpile.gif'):
    """Animate sandpile evolution"""
    print(f"Creating sandpile animation ({steps} steps)...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Sandpile visualization
    im = ax1.imshow(sandpile.grid, cmap='hot', vmin=0, vmax=sandpile.critical_height,
                    interpolation='nearest')
    ax1.set_title('Sandpile Height', fontsize=14)
    ax1.axis('off')
    plt.colorbar(im, ax=ax1, label='Grains')

    # Avalanche size over time
    ax2.set_xlim(0, steps)
    ax2.set_ylim(0, 100)
    ax2.set_xlabel('Time Step', fontsize=12)
    ax2.set_ylabel('Avalanche Size', fontsize=12)
    ax2.set_title('Avalanche Dynamics', fontsize=14)
    ax2.grid(True, alpha=0.3)

    avalanche_line, = ax2.plot([], [], 'r-', linewidth=1, alpha=0.7)
    avalanche_times = []
    avalanche_sizes_plot = []

    def update(frame):
        if frame % 50 == 0:
            print(f"  Frame {frame}/{steps}")

        # Add grain and check for avalanche
        before_count = len(sandpile.avalanche_sizes)
        sandpile.add_grain()
        after_count = len(sandpile.avalanche_sizes)

        if after_count > before_count:
            size = sandpile.avalanche_sizes[-1]
            avalanche_times.append(frame)
            avalanche_sizes_plot.append(size)

            # Update avalanche plot
            avalanche_line.set_data(avalanche_times, avalanche_sizes_plot)

            # Adjust y-axis if needed
            if size > ax2.get_ylim()[1]:
                ax2.set_ylim(0, size * 1.2)

        # Update sandpile image
        im.set_array(sandpile.grid)

        return im, avalanche_line

    anim = animation.FuncAnimation(fig, update, frames=steps,
                                  interval=20, blit=False, repeat=False)

    plt.tight_layout()
    print("Saving animation...")
    anim.save(filename, writer='pillow', fps=30)
    print(f"✓ Saved to {filename}")
    plt.close()


def analyze_power_law(sandpile, filename='power_law.png'):
    """Visualize power-law distribution of avalanche sizes"""
    result = sandpile.get_power_law_stats()

    if result is None or result[0] is None:
        print("Not enough avalanche data for power law analysis")
        return

    bin_centers, hist, alpha = result

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Linear plot
    ax1.scatter(bin_centers, hist, alpha=0.6, s=50)
    ax1.set_xlabel('Avalanche Size', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('Avalanche Size Distribution (Linear)', fontsize=14)
    ax1.grid(True, alpha=0.3)

    # Log-log plot (reveals power law)
    ax2.scatter(bin_centers, hist, alpha=0.6, s=50, label='Data')

    if alpha is not None:
        # Plot fitted power law
        x_fit = np.logspace(np.log10(min(bin_centers)), np.log10(max(bin_centers)), 50)
        # P(s) ~ s^(-α)
        const = hist[0] * (bin_centers[0] ** alpha)
        y_fit = const * (x_fit ** (-alpha))
        ax2.plot(x_fit, y_fit, 'r--', linewidth=2,
                label=f'Power Law: α = {alpha:.2f}')

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Avalanche Size (log)', fontsize=12)
    ax2.set_ylabel('Frequency (log)', fontsize=12)
    ax2.set_title('Avalanche Size Distribution (Log-Log)', fontsize=14)
    ax2.grid(True, alpha=0.3, which='both')
    ax2.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    print(f"✓ Saved power law analysis to {filename}")
    plt.close()

    if alpha is not None:
        print(f"\nPower law exponent α = {alpha:.2f}")
        print("(Theory predicts α ≈ 1.0 for 2D sandpile)")


def visualize_forest_fire(forest, steps=500, filename='forest_fire.gif'):
    """Animate forest fire evolution"""
    print(f"Creating forest fire animation ({steps} steps)...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Color map: empty=black, tree=green, fire=red
    colors = ['black', 'green', 'red']
    cmap = plt.matplotlib.colors.ListedColormap(colors)

    im = ax1.imshow(forest.grid, cmap=cmap, vmin=0, vmax=2, interpolation='nearest')
    ax1.set_title('Forest Fire Dynamics', fontsize=14)
    ax1.axis('off')

    # Fire size over time
    ax2.set_xlim(0, steps)
    ax2.set_ylim(0, 100)
    ax2.set_xlabel('Time Step', fontsize=12)
    ax2.set_ylabel('Fire Size', fontsize=12)
    ax2.set_title('Fire Size Over Time', fontsize=14)
    ax2.grid(True, alpha=0.3)

    fire_line, = ax2.plot([], [], 'r-', linewidth=1, alpha=0.7)
    fire_times = []
    fire_sizes_plot = []

    def update(frame):
        if frame % 50 == 0:
            print(f"  Frame {frame}/{steps}")

        before_count = len(forest.fire_sizes)
        forest.step()
        after_count = len(forest.fire_sizes)

        if after_count > before_count:
            size = forest.fire_sizes[-1]
            fire_times.append(frame)
            fire_sizes_plot.append(size)

            fire_line.set_data(fire_times, fire_sizes_plot)

            if size > ax2.get_ylim()[1]:
                ax2.set_ylim(0, size * 1.2)

        im.set_array(forest.grid)
        return im, fire_line

    anim = animation.FuncAnimation(fig, update, frames=steps,
                                  interval=30, blit=False, repeat=False)

    plt.tight_layout()
    print("Saving animation...")
    anim.save(filename, writer='pillow', fps=30)
    print(f"✓ Saved to {filename}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Self-Organizing Criticality')
    parser.add_argument('--model', type=str, default='sandpile',
                       choices=['sandpile', 'forest'],
                       help='Which SOC model to run')
    parser.add_argument('--size', type=int, default=100,
                       help='Grid size')
    parser.add_argument('--steps', type=int, default=500,
                       help='Animation steps')
    parser.add_argument('--evolve', type=int, default=50000,
                       help='Grains to add before animation (sandpile only)')

    args = parser.parse_args()

    print("🏔️ Self-Organizing Criticality")
    print("   Systems that evolve to critical states")
    print("   Power-law distributions emerge naturally\n")

    if args.model == 'sandpile':
        print(f"Model: Bak-Tang-Wiesenfeld Sandpile")
        print(f"Grid: {args.size}x{args.size}")
        print(f"Critical height: 4 grains\n")

        # Create sandpile
        sandpile = Sandpile(size=args.size, critical_height=4)

        # Evolve to criticality
        sandpile.evolve_to_criticality(num_grains=args.evolve)

        # Animate
        visualize_sandpile(sandpile, steps=args.steps, filename='soc_sandpile.gif')

        # Analyze power law
        analyze_power_law(sandpile, filename='soc_power_law.png')

        # Statistics
        if len(sandpile.avalanche_sizes) > 0:
            sizes = np.array(sandpile.avalanche_sizes)
            sizes = sizes[sizes > 0]

            print(f"\n{'='*70}")
            print("AVALANCHE STATISTICS")
            print('='*70)
            print(f"Total avalanches: {len(sizes)}")
            print(f"Avalanche sizes: min={min(sizes)}, max={max(sizes)}, mean={np.mean(sizes):.1f}")
            print(f"Large avalanches (>100): {np.sum(sizes > 100)} "
                  f"({100 * np.sum(sizes > 100) / len(sizes):.1f}%)")

    else:  # forest fire
        print(f"Model: Forest Fire")
        print(f"Grid: {args.size}x{args.size}")
        print(f"Growth probability: 0.01")
        print(f"Lightning probability: 0.0001\n")

        forest = ForestFire(size=args.size, p_grow=0.01, p_lightning=0.0001)

        visualize_forest_fire(forest, steps=args.steps, filename='soc_forest.gif')

        if len(forest.fire_sizes) > 0:
            sizes = np.array(forest.fire_sizes)
            print(f"\n{'='*70}")
            print("FIRE STATISTICS")
            print('='*70)
            print(f"Total fires: {len(sizes)}")
            print(f"Fire sizes: min={min(sizes)}, max={max(sizes)}, mean={np.mean(sizes):.1f}")

    print(f"\n{'='*70}")
    print("SELF-ORGANIZING CRITICALITY")
    print('='*70)
    print("Key insights:")
    print("  • No tuning required - system self-organizes to critical state")
    print("  • Avalanches of all sizes occur naturally")
    print("  • Power-law distributions (no characteristic scale)")
    print("  • Examples in nature: earthquakes, solar flares, extinctions")
    print('='*70)


if __name__ == "__main__":
    main()
