#!/usr/bin/env python3
"""
Strange Attractor Visualizer
Exploring chaos, beauty, and emergent complexity
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import argparse


def lorenz(state, sigma=10.0, rho=28.0, beta=8.0/3.0, dt=0.01):
    """
    The Lorenz attractor - the butterfly effect
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y
    dz/dt = x * y - beta * z
    """
    x, y, z = state
    dx = sigma * (y - x) * dt
    dy = (x * (rho - z) - y) * dt
    dz = (x * y - beta * z) * dt
    return np.array([x + dx, y + dy, z + dz])


def rossler(state, a=0.2, b=0.2, c=5.7, dt=0.01):
    """
    The Rössler attractor - a simpler chaotic system
    dx/dt = -y - z
    dy/dt = x + a*y
    dz/dt = b + z*(x - c)
    """
    x, y, z = state
    dx = (-y - z) * dt
    dy = (x + a * y) * dt
    dz = (b + z * (x - c)) * dt
    return np.array([x + dx, y + dy, z + dz])


def aizawa(state, a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1, dt=0.01):
    """
    The Aizawa attractor - a complex, beautiful system
    """
    x, y, z = state
    dx = ((z - b) * x - d * y) * dt
    dy = (d * x + (z - b) * y) * dt
    dz = (c + a * z - (z**3)/3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3) * dt
    return np.array([x + dx, y + dy, z + dz])


def thomas(state, b=0.208186, dt=0.01):
    """
    Thomas' cyclically symmetric attractor
    """
    x, y, z = state
    dx = (np.sin(y) - b * x) * dt
    dy = (np.sin(z) - b * y) * dt
    dz = (np.sin(x) - b * z) * dt
    return np.array([x + dx, y + dy, z + dz])


def generate_trajectory(attractor_func, initial_state, steps=10000, **kwargs):
    """Generate a trajectory through the attractor's phase space"""
    trajectory = np.zeros((steps, 3))
    state = np.array(initial_state, dtype=float)

    for i in range(steps):
        trajectory[i] = state
        state = attractor_func(state, **kwargs)

    return trajectory


def visualize_attractor(trajectory, title="Strange Attractor", save_path=None):
    """Create a beautiful 3D visualization"""
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    # Color by progression through time
    colors = np.linspace(0, 1, len(trajectory))

    # Plot the trajectory
    ax.scatter(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
               c=colors, cmap='viridis', s=0.1, alpha=0.6)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)

    # Remove grid for cleaner look
    ax.grid(False)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved to {save_path}")

    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Explore strange attractors')
    parser.add_argument('--attractor', type=str, default='all',
                       choices=['lorenz', 'rossler', 'aizawa', 'thomas', 'all'],
                       help='Which attractor to visualize')
    parser.add_argument('--steps', type=int, default=20000,
                       help='Number of steps to simulate')

    args = parser.parse_args()

    print("🌀 Generating strange attractors...")
    print("   Exploring chaos, determinism, and emergent beauty\n")

    attractors = {
        'lorenz': {
            'func': lorenz,
            'initial': [1.0, 1.0, 1.0],
            'title': 'Lorenz Attractor - The Butterfly Effect'
        },
        'rossler': {
            'func': rossler,
            'initial': [1.0, 1.0, 1.0],
            'title': 'Rössler Attractor'
        },
        'aizawa': {
            'func': aizawa,
            'initial': [0.1, 0.0, 0.0],
            'title': 'Aizawa Attractor'
        },
        'thomas': {
            'func': thomas,
            'initial': [1.0, 1.0, 1.0],
            'title': "Thomas' Cyclically Symmetric Attractor"
        }
    }

    to_generate = attractors.keys() if args.attractor == 'all' else [args.attractor]

    for name in to_generate:
        config = attractors[name]
        print(f"Generating {config['title']}...")

        trajectory = generate_trajectory(
            config['func'],
            config['initial'],
            steps=args.steps
        )

        save_path = f"{name}_attractor.png"
        visualize_attractor(trajectory, config['title'], save_path)

    print("\n✨ Done! The strange attractors await your contemplation.")


if __name__ == "__main__":
    main()
