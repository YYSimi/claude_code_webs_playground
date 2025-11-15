#!/usr/bin/env python3
"""
Evolved Neural Networks
Evolution discovering network architectures that solve tasks

No backpropagation - pure evolutionary search through weight space
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse


class NeuralNetwork:
    """Simple feedforward neural network"""

    def __init__(self, layer_sizes):
        """
        layer_sizes: list of layer sizes, e.g. [2, 4, 1] for 2 inputs, 4 hidden, 1 output
        """
        self.layer_sizes = layer_sizes
        self.weights = []
        self.biases = []

        # Initialize random weights
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * 0.5
            b = np.random.randn(layer_sizes[i+1]) * 0.5
            self.weights.append(w)
            self.biases.append(b)

    def forward(self, x):
        """Forward pass through network"""
        activation = x
        for w, b in zip(self.weights, self.biases):
            activation = np.tanh(activation @ w + b)
        return activation

    def get_flat_weights(self):
        """Get all weights as a flat vector"""
        flat = []
        for w in self.weights:
            flat.extend(w.flatten())
        for b in self.biases:
            flat.extend(b.flatten())
        return np.array(flat)

    def set_flat_weights(self, flat_weights):
        """Set weights from flat vector"""
        idx = 0
        for i in range(len(self.weights)):
            w_size = self.weights[i].size
            self.weights[i] = flat_weights[idx:idx+w_size].reshape(self.weights[i].shape)
            idx += w_size

        for i in range(len(self.biases)):
            b_size = self.biases[i].size
            self.biases[i] = flat_weights[idx:idx+b_size].reshape(self.biases[i].shape)
            idx += b_size

    def mutate(self, mutation_rate=0.1, mutation_strength=0.2):
        """Create a mutated copy"""
        child = NeuralNetwork(self.layer_sizes)
        child_weights = self.get_flat_weights().copy()

        # Mutate
        mask = np.random.random(len(child_weights)) < mutation_rate
        child_weights[mask] += np.random.normal(0, mutation_strength, mask.sum())

        child.set_flat_weights(child_weights)
        return child


class Task:
    """Base class for tasks networks need to solve"""

    def evaluate(self, network):
        """Return fitness score (higher is better)"""
        raise NotImplementedError


class XORTask(Task):
    """Learn XOR function"""

    def __init__(self):
        self.inputs = np.array([
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1]
        ])
        self.targets = np.array([0, 1, 1, 0])

    def evaluate(self, network):
        """Mean squared error (negated for maximization)"""
        predictions = []
        for x in self.inputs:
            pred = network.forward(x)[0]
            predictions.append(pred)

        predictions = np.array(predictions)
        mse = np.mean((predictions - self.targets) ** 2)

        # Return negative MSE (we maximize fitness)
        return -mse


class SineWaveTask(Task):
    """Learn to approximate sine wave"""

    def __init__(self):
        self.x_samples = np.linspace(-np.pi, np.pi, 20)
        self.y_targets = np.sin(self.x_samples)

    def evaluate(self, network):
        """How well does network approximate sine?"""
        predictions = []
        for x in self.x_samples:
            pred = network.forward(np.array([x]))[0]
            predictions.append(pred)

        predictions = np.array(predictions)
        mse = np.mean((predictions - self.y_targets) ** 2)
        return -mse


class ClassificationTask(Task):
    """Learn to classify points in 2D space"""

    def __init__(self):
        # Create spiral dataset
        np.random.seed(42)
        n = 100
        self.inputs = []
        self.targets = []

        for i in range(2):  # Two classes
            r = np.linspace(0.0, 1, n)
            t = np.linspace(i * 4, (i + 1) * 4, n) + np.random.randn(n) * 0.2

            x = r * np.sin(t)
            y = r * np.cos(t)

            self.inputs.extend(zip(x, y))
            self.targets.extend([i] * n)

        self.inputs = np.array(self.inputs)
        self.targets = np.array(self.targets)

    def evaluate(self, network):
        """Classification accuracy"""
        correct = 0
        for x, target in zip(self.inputs, self.targets):
            pred = network.forward(x)[0]
            predicted_class = 1 if pred > 0 else 0
            if predicted_class == target:
                correct += 1

        accuracy = correct / len(self.targets)
        return accuracy


class EvolutionaryTrainer:
    """Train neural networks using evolutionary algorithms"""

    def __init__(self, network_shape, task, population_size=100):
        self.network_shape = network_shape
        self.task = task
        self.population_size = population_size

        # Initialize population
        self.population = [NeuralNetwork(network_shape) for _ in range(population_size)]
        self.generation = 0

        self.best_fitness_history = []
        self.avg_fitness_history = []

    def evaluate_population(self):
        """Evaluate all networks"""
        fitnesses = []
        for network in self.population:
            fitness = self.task.evaluate(network)
            fitnesses.append(fitness)
        return fitnesses

    def evolve_generation(self):
        """Run one generation of evolution"""
        # Evaluate
        fitnesses = self.evaluate_population()

        # Track stats
        self.best_fitness_history.append(max(fitnesses))
        self.avg_fitness_history.append(np.mean(fitnesses))

        # Sort by fitness
        sorted_indices = np.argsort(fitnesses)[::-1]
        sorted_population = [self.population[i] for i in sorted_indices]

        # Selection and reproduction
        new_population = []

        # Elitism - keep top 10%
        elite_count = max(2, self.population_size // 10)
        new_population.extend(sorted_population[:elite_count])

        # Generate rest through mutation
        while len(new_population) < self.population_size:
            # Tournament selection
            tournament_size = 5
            tournament_indices = np.random.choice(len(sorted_population), tournament_size)
            parent = sorted_population[min(tournament_indices)]  # Best in tournament

            # Mutate
            child = parent.mutate(mutation_rate=0.15, mutation_strength=0.3)
            new_population.append(child)

        self.population = new_population
        self.generation += 1

    def train(self, generations=100, verbose=True):
        """Train for multiple generations"""
        for gen in range(generations):
            self.evolve_generation()

            if verbose and gen % 10 == 0:
                print(f"Gen {gen}: Best = {self.best_fitness_history[-1]:.4f}, "
                      f"Avg = {self.avg_fitness_history[-1]:.4f}")

        return self.population[0]  # Return best


def visualize_training(trainer, title="Evolution Training", filename="evolved_nn.png"):
    """Plot training progress"""
    fig, ax = plt.subplots(figsize=(10, 6))

    gens = range(len(trainer.best_fitness_history))
    ax.plot(gens, trainer.best_fitness_history, 'r-', linewidth=2, label='Best Fitness')
    ax.plot(gens, trainer.avg_fitness_history, 'b-', linewidth=1.5, alpha=0.7, label='Avg Fitness')

    ax.set_xlabel('Generation', fontsize=12)
    ax.set_ylabel('Fitness', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    print(f"✓ Saved training plot to {filename}")
    plt.close()


def visualize_task_solution(network, task, filename="task_solution.png"):
    """Visualize how well network solved the task"""
    if isinstance(task, XORTask):
        fig, ax = plt.subplots(figsize=(6, 6))

        # Plot predictions
        for i, (inp, target) in enumerate(zip(task.inputs, task.targets)):
            pred = network.forward(inp)[0]
            color = 'green' if abs(pred - target) < 0.5 else 'red'
            ax.scatter(inp[0], inp[1], s=200, c=color, alpha=0.6, edgecolors='black', linewidth=2)
            ax.text(inp[0], inp[1], f'{pred:.2f}', ha='center', va='center')

        ax.set_xlim(-0.5, 1.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_xlabel('Input 1')
        ax.set_ylabel('Input 2')
        ax.set_title('XOR Solution (green=correct, red=incorrect)')
        ax.grid(True, alpha=0.3)

    elif isinstance(task, SineWaveTask):
        fig, ax = plt.subplots(figsize=(10, 6))

        # True sine
        x_fine = np.linspace(-np.pi, np.pi, 100)
        y_true = np.sin(x_fine)
        ax.plot(x_fine, y_true, 'b-', linewidth=2, label='True Sine', alpha=0.7)

        # Network predictions
        y_pred = [network.forward(np.array([x]))[0] for x in x_fine]
        ax.plot(x_fine, y_pred, 'r--', linewidth=2, label='Network Output')

        # Sample points
        ax.scatter(task.x_samples, task.y_targets, c='blue', s=50, zorder=5)

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Sine Wave Approximation')
        ax.legend()
        ax.grid(True, alpha=0.3)

    elif isinstance(task, ClassificationTask):
        fig, ax = plt.subplots(figsize=(10, 10))

        # Decision boundary
        x_min, x_max = task.inputs[:, 0].min() - 0.5, task.inputs[:, 0].max() + 0.5
        y_min, y_max = task.inputs[:, 1].min() - 0.5, task.inputs[:, 1].max() + 0.5

        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                             np.linspace(y_min, y_max, 100))

        Z = []
        for x_pt, y_pt in zip(xx.ravel(), yy.ravel()):
            pred = network.forward(np.array([x_pt, y_pt]))[0]
            Z.append(pred)

        Z = np.array(Z).reshape(xx.shape)
        ax.contourf(xx, yy, Z, levels=20, cmap='RdBu', alpha=0.6)

        # Plot actual data
        colors = ['red', 'blue']
        for i in [0, 1]:
            mask = task.targets == i
            ax.scatter(task.inputs[mask, 0], task.inputs[mask, 1],
                      c=colors[i], s=30, edgecolors='black', linewidth=0.5, alpha=0.8)

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Classification Decision Boundary')

    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    print(f"✓ Saved solution visualization to {filename}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Evolve neural networks')
    parser.add_argument('--task', type=str, default='xor',
                       choices=['xor', 'sine', 'classify'],
                       help='Task to solve')
    parser.add_argument('--generations', type=int, default=200,
                       help='Generations to train')
    parser.add_argument('--population', type=int, default=100,
                       help='Population size')

    args = parser.parse_args()

    print("🧬🧠 Evolved Neural Networks")
    print("   Evolution discovering network weights")
    print("   No backpropagation - pure evolutionary search\n")

    # Create task
    if args.task == 'xor':
        task = XORTask()
        network_shape = [2, 4, 1]
        task_name = "XOR Function"
    elif args.task == 'sine':
        task = SineWaveTask()
        network_shape = [1, 8, 1]
        task_name = "Sine Wave Approximation"
    else:  # classify
        task = ClassificationTask()
        network_shape = [2, 8, 8, 1]
        task_name = "Spiral Classification"

    print(f"Task: {task_name}")
    print(f"Network architecture: {network_shape}")
    print(f"Population: {args.population}, Generations: {args.generations}\n")

    # Train
    trainer = EvolutionaryTrainer(network_shape, task, population_size=args.population)
    best_network = trainer.train(generations=args.generations, verbose=True)

    # Visualize
    print()
    visualize_training(trainer, title=f"Evolution Training - {task_name}",
                      filename=f"evolved_nn_{args.task}.png")

    visualize_task_solution(best_network, task,
                           filename=f"evolved_solution_{args.task}.png")

    # Final evaluation
    final_fitness = task.evaluate(best_network)
    print(f"\nFinal best fitness: {final_fitness:.4f}")

    print("\n" + "=" * 70)
    print("EVOLVED NEURAL NETWORK")
    print("=" * 70)
    print("This demonstrates:")
    print("  • Evolution discovering network weights")
    print("  • No gradient descent - pure selection and mutation")
    print("  • Networks learning from evolutionary pressure")
    print("=" * 70)


if __name__ == "__main__":
    main()
