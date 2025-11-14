#!/usr/bin/env python3
"""
Optimization Through Evolution
Genetic algorithms and simulated annealing solving various problems
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, List, Tuple
import argparse
from dataclasses import dataclass


@dataclass
class Individual:
    """An individual solution in the population"""
    genes: np.ndarray
    fitness: float = None


class GeneticAlgorithm:
    """Genetic algorithm framework for optimization"""

    def __init__(self,
                 fitness_function: Callable,
                 gene_length: int,
                 population_size: int = 100,
                 mutation_rate: float = 0.01,
                 crossover_rate: float = 0.7,
                 elitism: int = 2,
                 gene_bounds: Tuple[float, float] = (0, 1)):

        self.fitness_func = fitness_function
        self.gene_length = gene_length
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism = elitism
        self.gene_bounds = gene_bounds

        # Initialize population
        self.population = self._initialize_population()
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []

    def _initialize_population(self) -> List[Individual]:
        """Create initial random population"""
        population = []
        for _ in range(self.population_size):
            genes = np.random.uniform(
                self.gene_bounds[0],
                self.gene_bounds[1],
                self.gene_length
            )
            population.append(Individual(genes))
        return population

    def _evaluate_fitness(self):
        """Evaluate fitness for all individuals"""
        for individual in self.population:
            if individual.fitness is None:
                individual.fitness = self.fitness_func(individual.genes)

    def _selection(self) -> Individual:
        """Tournament selection"""
        tournament_size = 3
        tournament = np.random.choice(self.population, tournament_size)
        return max(tournament, key=lambda ind: ind.fitness)

    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Single-point crossover"""
        if np.random.random() > self.crossover_rate:
            return Individual(parent1.genes.copy()), Individual(parent2.genes.copy())

        point = np.random.randint(1, self.gene_length)

        child1_genes = np.concatenate([parent1.genes[:point], parent2.genes[point:]])
        child2_genes = np.concatenate([parent2.genes[:point], parent1.genes[point:]])

        return Individual(child1_genes), Individual(child2_genes)

    def _mutate(self, individual: Individual):
        """Gaussian mutation"""
        for i in range(len(individual.genes)):
            if np.random.random() < self.mutation_rate:
                individual.genes[i] += np.random.normal(0, 0.1)
                individual.genes[i] = np.clip(
                    individual.genes[i],
                    self.gene_bounds[0],
                    self.gene_bounds[1]
                )

    def evolve(self):
        """Run one generation of evolution"""
        self._evaluate_fitness()

        # Track statistics
        fitnesses = [ind.fitness for ind in self.population]
        self.best_fitness_history.append(max(fitnesses))
        self.avg_fitness_history.append(np.mean(fitnesses))

        # Sort by fitness
        self.population.sort(key=lambda ind: ind.fitness, reverse=True)

        # Create new population
        new_population = []

        # Elitism - keep best individuals
        new_population.extend([
            Individual(ind.genes.copy(), ind.fitness)
            for ind in self.population[:self.elitism]
        ])

        # Generate rest through selection, crossover, mutation
        while len(new_population) < self.population_size:
            parent1 = self._selection()
            parent2 = self._selection()

            child1, child2 = self._crossover(parent1, parent2)

            self._mutate(child1)
            self._mutate(child2)

            new_population.extend([child1, child2])

        self.population = new_population[:self.population_size]
        self.generation += 1

    def run(self, generations: int, verbose: bool = True):
        """Run the genetic algorithm"""
        for gen in range(generations):
            self.evolve()

            if verbose and gen % 50 == 0:
                best = self.population[0]
                print(f"Gen {gen}: Best fitness = {best.fitness:.6f}")

        return self.population[0]


class SimulatedAnnealing:
    """Simulated annealing optimization"""

    def __init__(self,
                 fitness_function: Callable,
                 initial_solution: np.ndarray,
                 initial_temp: float = 100.0,
                 cooling_rate: float = 0.95,
                 min_temp: float = 0.01,
                 step_size: float = 0.1):

        self.fitness_func = fitness_function
        self.current = initial_solution.copy()
        self.current_fitness = fitness_function(self.current)
        self.best = self.current.copy()
        self.best_fitness = self.current_fitness

        self.temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.step_size = step_size

        self.fitness_history = [self.current_fitness]
        self.temp_history = [self.temp]

    def _neighbor(self, solution: np.ndarray) -> np.ndarray:
        """Generate a neighboring solution"""
        neighbor = solution + np.random.normal(0, self.step_size, len(solution))
        return neighbor

    def _accept_probability(self, old_fitness: float, new_fitness: float) -> float:
        """Calculate probability of accepting worse solution"""
        if new_fitness > old_fitness:
            return 1.0
        return np.exp((new_fitness - old_fitness) / self.temp)

    def step(self):
        """Take one step of simulated annealing"""
        # Generate neighbor
        neighbor = self._neighbor(self.current)
        neighbor_fitness = self.fitness_func(neighbor)

        # Accept or reject
        if np.random.random() < self._accept_probability(self.current_fitness, neighbor_fitness):
            self.current = neighbor
            self.current_fitness = neighbor_fitness

            # Update best
            if self.current_fitness > self.best_fitness:
                self.best = self.current.copy()
                self.best_fitness = self.current_fitness

        # Cool down
        self.temp *= self.cooling_rate

        # Track history
        self.fitness_history.append(self.current_fitness)
        self.temp_history.append(self.temp)

    def run(self, max_iterations: int = 10000, verbose: bool = True):
        """Run simulated annealing"""
        iteration = 0
        while self.temp > self.min_temp and iteration < max_iterations:
            self.step()

            if verbose and iteration % 1000 == 0:
                print(f"Iteration {iteration}: Best = {self.best_fitness:.6f}, Temp = {self.temp:.4f}")

            iteration += 1

        return self.best


# ============================================================================
# Problem Domains
# ============================================================================

def rastrigin_function(x: np.ndarray) -> float:
    """
    Rastrigin function - highly multimodal, difficult to optimize
    Global minimum at origin with value 0
    We return negative because GA maximizes
    """
    n = len(x)
    A = 10
    return -(A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x)))


def sphere_function(x: np.ndarray) -> float:
    """Simple sphere function - single global minimum at origin"""
    return -np.sum(x**2)


def rosenbrock_function(x: np.ndarray) -> float:
    """Rosenbrock function - narrow valley, global minimum at (1,1,...)"""
    return -np.sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)


def traveling_salesman_fitness(route: np.ndarray, cities: np.ndarray) -> float:
    """
    Fitness for TSP - negative total distance
    route: permutation of city indices
    cities: array of (x, y) coordinates
    """
    route = route.astype(int) % len(cities)  # Ensure valid indices
    total_distance = 0

    for i in range(len(route)):
        city1 = cities[route[i]]
        city2 = cities[route[(i + 1) % len(route)]]
        total_distance += np.linalg.norm(city1 - city2)

    return -total_distance


def knapsack_fitness(x: np.ndarray, weights: np.ndarray, values: np.ndarray, capacity: float) -> float:
    """
    Knapsack problem - maximize value while staying under weight capacity
    x: binary array indicating which items to take
    """
    # Threshold to binary
    selection = (x > 0.5).astype(int)

    total_weight = np.sum(selection * weights)
    total_value = np.sum(selection * values)

    # Penalty for exceeding capacity
    if total_weight > capacity:
        return 0

    return total_value


# ============================================================================
# Visualization
# ============================================================================

def plot_optimization_history(ga_history, sa_history, problem_name, filename):
    """Plot optimization progress for both algorithms"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # GA plot
    ax1.plot(ga_history['best'], label='Best Fitness', linewidth=2, color='red')
    ax1.plot(ga_history['avg'], label='Average Fitness', linewidth=1.5, color='blue', alpha=0.7)
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Fitness')
    ax1.set_title(f'Genetic Algorithm - {problem_name}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # SA plot
    ax2.plot(sa_history['fitness'], linewidth=1.5, color='green')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Fitness')
    ax2.set_title(f'Simulated Annealing - {problem_name}')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved plot to {filename}")
    plt.close()


# ============================================================================
# Main Experiments
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Optimization algorithm comparison')
    parser.add_argument('--problem', type=str, default='rastrigin',
                       choices=['rastrigin', 'sphere', 'rosenbrock', 'all'],
                       help='Optimization problem to solve')
    parser.add_argument('--generations', type=int, default=200,
                       help='Generations for GA')
    parser.add_argument('--sa-iterations', type=int, default=5000,
                       help='Iterations for SA')

    args = parser.parse_args()

    print("🧬 Evolutionary Optimization")
    print("   Comparing Genetic Algorithms vs Simulated Annealing\n")

    problems = {
        'rastrigin': (rastrigin_function, 10, (-5.12, 5.12), "Rastrigin (multimodal)"),
        'sphere': (sphere_function, 10, (-10, 10), "Sphere (convex)"),
        'rosenbrock': (rosenbrock_function, 10, (-5, 5), "Rosenbrock (narrow valley)"),
    }

    to_run = problems.keys() if args.problem == 'all' else [args.problem]

    for problem_name in to_run:
        func, dimensions, bounds, description = problems[problem_name]

        print("=" * 70)
        print(f"Problem: {description}")
        print(f"Dimensions: {dimensions}, Bounds: {bounds}")
        print("=" * 70)

        # Genetic Algorithm
        print("\n🧬 Running Genetic Algorithm...")
        ga = GeneticAlgorithm(
            fitness_function=func,
            gene_length=dimensions,
            population_size=100,
            mutation_rate=0.05,
            crossover_rate=0.7,
            gene_bounds=bounds
        )

        best_ga = ga.run(generations=args.generations, verbose=True)
        print(f"\nGA Result: {best_ga.genes}")
        print(f"GA Fitness: {best_ga.fitness:.6f}")

        # Simulated Annealing
        print("\n🌡️  Running Simulated Annealing...")
        initial = np.random.uniform(bounds[0], bounds[1], dimensions)
        sa = SimulatedAnnealing(
            fitness_function=func,
            initial_solution=initial,
            initial_temp=100.0,
            cooling_rate=0.95,
            step_size=0.5
        )

        best_sa = sa.run(max_iterations=args.sa_iterations, verbose=True)
        print(f"\nSA Result: {best_sa}")
        print(f"SA Fitness: {sa.best_fitness:.6f}")

        # Compare
        print("\n" + "=" * 70)
        print("COMPARISON")
        print("=" * 70)
        print(f"GA Final Fitness: {best_ga.fitness:.6f}")
        print(f"SA Final Fitness: {sa.best_fitness:.6f}")
        winner = "Genetic Algorithm" if best_ga.fitness > sa.best_fitness else "Simulated Annealing"
        print(f"Winner: {winner}")

        # Plot
        plot_optimization_history(
            {'best': ga.best_fitness_history, 'avg': ga.avg_fitness_history},
            {'fitness': sa.fitness_history},
            description,
            f'optimization_{problem_name}.png'
        )

        print()

    print("✨ Optimization complete - evolution finds solutions!")


if __name__ == "__main__":
    main()
