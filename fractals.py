#!/usr/bin/env python3
"""
Fractal Explorer
Infinite complexity, infinite beauty
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import argparse


def mandelbrot(height, width, max_iter=256, zoom=1, center=(-0.5, 0)):
    """Generate the Mandelbrot set"""
    # Create coordinate arrays
    x_min, x_max = center[0] - 2/zoom, center[0] + 2/zoom
    y_min, y_max = center[1] - 1.5/zoom, center[1] + 1.5/zoom

    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)

    # Complex plane
    C = X + 1j*Y
    Z = np.zeros_like(C)
    M = np.zeros(C.shape)

    for i in range(max_iter):
        # Points that haven't diverged
        mask = np.abs(Z) <= 2

        # Iterate: z = z^2 + c
        Z[mask] = Z[mask]**2 + C[mask]

        # Track iteration count
        M[mask] = i

    return M


def julia(height, width, c=-0.7+0.27015j, max_iter=256, zoom=1):
    """Generate a Julia set"""
    # Create coordinate arrays
    x_min, x_max = -2/zoom, 2/zoom
    y_min, y_max = -1.5/zoom, 1.5/zoom

    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)

    # Complex plane
    Z = X + 1j*Y
    M = np.zeros(Z.shape)

    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask]**2 + c
        M[mask] = i

    return M


def burning_ship(height, width, max_iter=256, zoom=1, center=(-0.5, -0.5)):
    """Generate the Burning Ship fractal"""
    x_min, x_max = center[0] - 2/zoom, center[0] + 2/zoom
    y_min, y_max = center[1] - 1.5/zoom, center[1] + 1.5/zoom

    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)

    C = X + 1j*Y
    Z = np.zeros_like(C)
    M = np.zeros(C.shape)

    for i in range(max_iter):
        mask = np.abs(Z) <= 2

        # Key difference: take absolute value before squaring
        Z[mask] = (np.abs(Z[mask].real) + 1j*np.abs(Z[mask].imag))**2 + C[mask]

        M[mask] = i

    return M


def newton_fractal(height, width, max_iter=50, zoom=1):
    """Newton fractal for z^3 - 1 = 0"""
    x = np.linspace(-2/zoom, 2/zoom, width)
    y = np.linspace(-1.5/zoom, 1.5/zoom, height)
    X, Y = np.meshgrid(x, y)

    Z = X + 1j*Y
    M = np.zeros(Z.shape)

    # Three roots of z^3 - 1 = 0
    roots = [1, np.exp(2j*np.pi/3), np.exp(4j*np.pi/3)]
    colors = np.zeros(Z.shape)

    for i in range(max_iter):
        # Newton's method: z = z - f(z)/f'(z)
        # For f(z) = z^3 - 1: z = z - (z^3 - 1)/(3z^2) = (2z^3 + 1)/(3z^2)
        mask = np.abs(Z) > 0.01  # Avoid division by zero

        Z[mask] = Z[mask] - (Z[mask]**3 - 1) / (3 * Z[mask]**2)

    # Determine which root each point converged to
    for idx, root in enumerate(roots):
        dist = np.abs(Z - root)
        colors[dist < 0.1] = idx

    return colors


def sierpinski_triangle(iterations=7):
    """Generate Sierpinski triangle using chaos game"""
    # Three vertices of equilateral triangle
    vertices = np.array([
        [0, 0],
        [1, 0],
        [0.5, np.sqrt(3)/2]
    ])

    # Start at random point
    point = np.random.random(2)
    points = []

    # Chaos game
    for _ in range(50000):  # First points ignored as warmup
        vertex = vertices[np.random.randint(0, 3)]
        point = (point + vertex) / 2
        points.append(point.copy())

    return np.array(points)


def barnsley_fern(iterations=100000):
    """Generate Barnsley fern using IFS"""
    points = []
    x, y = 0, 0

    for _ in range(iterations):
        r = np.random.random()

        if r < 0.01:  # Stem
            x_new = 0
            y_new = 0.16 * y
        elif r < 0.86:  # Successively smaller leaflets
            x_new = 0.85 * x + 0.04 * y
            y_new = -0.04 * x + 0.85 * y + 1.6
        elif r < 0.93:  # Largest left-hand leaflet
            x_new = 0.2 * x - 0.26 * y
            y_new = 0.23 * x + 0.22 * y + 1.6
        else:  # Largest right-hand leaflet
            x_new = -0.15 * x + 0.28 * y
            y_new = 0.26 * x + 0.24 * y + 0.44

        x, y = x_new, y_new
        points.append([x, y])

    return np.array(points)


def dragon_curve(iterations=15):
    """Generate dragon curve using L-system"""
    # L-system rules:
    # X -> X+YF+
    # Y -> -FX-Y

    axiom = "FX"
    rules = {'X': 'X+YF+', 'Y': '-FX-Y'}

    # Generate string
    sequence = axiom
    for _ in range(iterations):
        sequence = ''.join(rules.get(c, c) for c in sequence)

    # Interpret as turtle graphics
    x, y = 0, 0
    angle = 0
    points = [(x, y)]

    for cmd in sequence:
        if cmd == 'F':
            x += np.cos(np.radians(angle))
            y += np.sin(np.radians(angle))
            points.append((x, y))
        elif cmd == '+':
            angle += 90
        elif cmd == '-':
            angle -= 90

    return np.array(points)


def visualize_fractal(data, title, filename, cmap='hot', point_based=False):
    """Visualize a fractal"""
    fig, ax = plt.subplots(figsize=(12, 10))

    if point_based:
        # For point-based fractals (IFS, chaos game)
        ax.scatter(data[:, 0], data[:, 1], s=0.1, c='green', alpha=0.5)
        ax.set_aspect('equal')
        ax.axis('off')
    else:
        # For grid-based fractals
        im = ax.imshow(data, cmap=cmap, interpolation='bilinear')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set_title(title, fontsize=16, pad=20)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='black')
    print(f"✓ {title} saved to {filename}")
    plt.close()


def create_custom_colormap():
    """Create a beautiful custom colormap"""
    colors = ['#000033', '#000055', '#0E4C92', '#2E8BC0', '#19D3F3',
              '#FFF700', '#FF6C00', '#C70039', '#900C3F', '#581845']
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
    return cmap


def main():
    parser = argparse.ArgumentParser(description='Explore fractals')
    parser.add_argument('--type', type=str, default='all',
                       choices=['mandelbrot', 'julia', 'burning_ship', 'newton',
                               'sierpinski', 'fern', 'dragon', 'all'],
                       help='Type of fractal to generate')
    parser.add_argument('--resolution', type=int, default=2000,
                       help='Resolution (width in pixels)')

    args = parser.parse_args()

    print("🌀 Fractal Explorer")
    print("   Generating infinite complexity...\n")

    custom_cmap = create_custom_colormap()

    # Grid-based fractals
    if args.type in ['mandelbrot', 'all']:
        print("Generating Mandelbrot set...")
        M = mandelbrot(args.resolution, args.resolution, max_iter=256)
        visualize_fractal(M, "The Mandelbrot Set", "fractal_mandelbrot.png",
                         cmap=custom_cmap)

    if args.type in ['julia', 'all']:
        print("Generating Julia set...")
        J = julia(args.resolution, args.resolution, c=-0.7+0.27015j, max_iter=256)
        visualize_fractal(J, "Julia Set (c = -0.7 + 0.27015i)",
                         "fractal_julia.png", cmap='twilight')

    if args.type in ['burning_ship', 'all']:
        print("Generating Burning Ship fractal...")
        B = burning_ship(args.resolution, args.resolution, max_iter=256,
                        zoom=1, center=(-0.5, -0.6))
        visualize_fractal(B, "The Burning Ship Fractal",
                         "fractal_burning_ship.png", cmap='inferno')

    if args.type in ['newton', 'all']:
        print("Generating Newton fractal...")
        N = newton_fractal(args.resolution, args.resolution, max_iter=50)
        visualize_fractal(N, "Newton Fractal (z³ - 1 = 0)",
                         "fractal_newton.png", cmap='viridis')

    # Point-based fractals
    if args.type in ['sierpinski', 'all']:
        print("Generating Sierpinski triangle...")
        S = sierpinski_triangle()
        visualize_fractal(S, "Sierpinski Triangle (Chaos Game)",
                         "fractal_sierpinski.png", point_based=True)

    if args.type in ['fern', 'all']:
        print("Generating Barnsley fern...")
        F = barnsley_fern(iterations=150000)
        visualize_fractal(F, "Barnsley Fern (Iterated Function System)",
                         "fractal_fern.png", point_based=True)

    if args.type in ['dragon', 'all']:
        print("Generating dragon curve...")
        D = dragon_curve(iterations=15)
        visualize_fractal(D, "Dragon Curve (L-System)",
                         "fractal_dragon.png", point_based=True)

    print("\n✨ Fractal generation complete!")
    print("   Infinite detail awaits your contemplation.")


if __name__ == "__main__":
    main()
