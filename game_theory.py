#!/usr/bin/env python3
"""
Evolutionary Game Theory
Exploring how cooperation and competition emerge through iterated interactions
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Callable
import argparse


@dataclass
class Strategy:
    """A strategy for playing iterated games"""
    name: str
    play: Callable  # Function that takes (history, opponent_history) and returns choice


class PrisonersDilemmaGame:
    """The classic prisoner's dilemma"""

    PAYOFFS = {
        ('C', 'C'): (3, 3),  # Both cooperate
        ('C', 'D'): (0, 5),  # I cooperate, opponent defects
        ('D', 'C'): (5, 0),  # I defect, opponent cooperates
        ('D', 'D'): (1, 1),  # Both defect
    }

    @staticmethod
    def play_round(choice1, choice2):
        """Play one round and return payoffs"""
        return PrisonersDilemmaGame.PAYOFFS[(choice1, choice2)]


# Define classic strategies
def always_cooperate(my_history, opp_history):
    """Always cooperate"""
    return 'C'


def always_defect(my_history, opp_history):
    """Always defect"""
    return 'D'


def tit_for_tat(my_history, opp_history):
    """Copy opponent's last move (start with cooperation)"""
    if not opp_history:
        return 'C'
    return opp_history[-1]


def tit_for_two_tats(my_history, opp_history):
    """Only defect if opponent defected twice in a row"""
    if len(opp_history) < 2:
        return 'C'
    if opp_history[-1] == 'D' and opp_history[-2] == 'D':
        return 'D'
    return 'C'


def grudger(my_history, opp_history):
    """Cooperate until opponent defects, then defect forever"""
    if 'D' in opp_history:
        return 'D'
    return 'C'


def random_strategy(my_history, opp_history):
    """Play randomly"""
    return np.random.choice(['C', 'D'])


def pavlov(my_history, opp_history):
    """Win-stay, lose-shift: repeat if last outcome was good"""
    if not my_history:
        return 'C'

    last_outcome = PrisonersDilemmaGame.play_round(my_history[-1], opp_history[-1])
    my_payoff = last_outcome[0]

    # If I got 3 or 5 (good outcomes), repeat my last move
    if my_payoff >= 3:
        return my_history[-1]
    else:
        # Otherwise, switch
        return 'D' if my_history[-1] == 'C' else 'C'


def generous_tit_for_tat(my_history, opp_history):
    """Tit for tat, but sometimes forgive defection"""
    if not opp_history:
        return 'C'

    if opp_history[-1] == 'D':
        # 10% chance to forgive and cooperate anyway
        if np.random.random() < 0.1:
            return 'C'
        return 'D'
    return 'C'


def suspicious_tit_for_tat(my_history, opp_history):
    """Like tit for tat, but start by defecting"""
    if not opp_history:
        return 'D'
    return opp_history[-1]


class Tournament:
    """Run a round-robin tournament between strategies"""

    def __init__(self, strategies: List[Strategy], rounds_per_match=100):
        self.strategies = strategies
        self.rounds_per_match = rounds_per_match
        self.scores = {s.name: 0 for s in strategies}
        self.matchups = {}

    def play_match(self, strat1: Strategy, strat2: Strategy):
        """Play a match between two strategies"""
        history1 = []
        history2 = []
        score1, score2 = 0, 0

        for _ in range(self.rounds_per_match):
            choice1 = strat1.play(history1, history2)
            choice2 = strat2.play(history2, history1)

            payoff1, payoff2 = PrisonersDilemmaGame.play_round(choice1, choice2)

            score1 += payoff1
            score2 += payoff2

            history1.append(choice1)
            history2.append(choice2)

        return score1, score2

    def run_tournament(self):
        """Run full round-robin tournament"""
        print(f"🎮 Running tournament with {len(self.strategies)} strategies")
        print(f"   Each pair plays {self.rounds_per_match} rounds\n")

        for i, strat1 in enumerate(self.strategies):
            for j, strat2 in enumerate(self.strategies):
                if i <= j:  # Only play each matchup once (including self-play)
                    score1, score2 = self.play_match(strat1, strat2)

                    self.scores[strat1.name] += score1
                    if i != j:  # Don't double count self-play
                        self.scores[strat2.name] += score2

                    self.matchups[(strat1.name, strat2.name)] = (score1, score2)

    def print_results(self):
        """Print tournament results"""
        print("=" * 60)
        print("TOURNAMENT RESULTS")
        print("=" * 60)

        sorted_strategies = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

        for rank, (name, score) in enumerate(sorted_strategies, 1):
            avg_score = score / (len(self.strategies) * self.rounds_per_match)
            print(f"{rank}. {name:25s} - {score:6d} points (avg: {avg_score:.2f})")

        print()


class EvolutionarySimulation:
    """Simulate evolution of strategies in a population"""

    def __init__(self, strategies: List[Strategy], initial_populations: List[int],
                 rounds_per_match=50):
        self.strategies = strategies
        self.populations = np.array(initial_populations, dtype=float)
        self.rounds_per_match = rounds_per_match
        self.history = [self.populations.copy()]

    def get_payoff_matrix(self):
        """Calculate average payoff matrix"""
        n = len(self.strategies)
        payoff_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                score1, _ = self._play_match(i, j)
                payoff_matrix[i, j] = score1 / self.rounds_per_match

        return payoff_matrix

    def _play_match(self, idx1, idx2):
        """Play match between strategy indices"""
        strat1 = self.strategies[idx1]
        strat2 = self.strategies[idx2]

        history1, history2 = [], []
        score1, score2 = 0, 0

        for _ in range(self.rounds_per_match):
            choice1 = strat1.play(history1, history2)
            choice2 = strat2.play(history2, history1)

            payoff1, payoff2 = PrisonersDilemmaGame.play_round(choice1, choice2)

            score1 += payoff1
            score2 += payoff2

            history1.append(choice1)
            history2.append(choice2)

        return score1, score2

    def step(self):
        """One generation of evolution"""
        payoff_matrix = self.get_payoff_matrix()

        # Calculate fitness for each strategy
        total_pop = self.populations.sum()
        proportions = self.populations / total_pop

        # Fitness = average payoff against current population distribution
        fitnesses = payoff_matrix @ proportions

        # New populations proportional to fitness
        total_fitness = (fitnesses * self.populations).sum()

        if total_fitness > 0:
            new_populations = (fitnesses * self.populations) / total_fitness * total_pop
        else:
            new_populations = self.populations

        self.populations = new_populations
        self.history.append(self.populations.copy())

    def run(self, generations=100):
        """Run simulation for multiple generations"""
        for _ in range(generations):
            self.step()

    def plot_evolution(self, filename='evolution_game_theory.png'):
        """Plot population dynamics over time"""
        history_array = np.array(self.history)

        plt.figure(figsize=(14, 8))
        for i, strategy in enumerate(self.strategies):
            plt.plot(history_array[:, i], label=strategy.name, linewidth=2)

        plt.xlabel('Generation')
        plt.ylabel('Population')
        plt.title('Evolution of Strategies in Prisoner\'s Dilemma')
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        print(f"\n📊 Evolution plot saved to {filename}")
        plt.close()

    def print_final_state(self):
        """Print final population distribution"""
        print("\n" + "=" * 60)
        print("FINAL POPULATION DISTRIBUTION")
        print("=" * 60)

        total = self.populations.sum()
        sorted_indices = np.argsort(self.populations)[::-1]

        for idx in sorted_indices:
            name = self.strategies[idx].name
            pop = self.populations[idx]
            pct = (pop / total) * 100
            print(f"{name:25s} - {pop:8.1f} ({pct:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(description='Game theory explorer')
    parser.add_argument('--mode', type=str, default='both',
                       choices=['tournament', 'evolution', 'both'],
                       help='Mode to run')
    parser.add_argument('--generations', type=int, default=200,
                       help='Generations for evolution')

    args = parser.parse_args()

    print("🎲 Evolutionary Game Theory Explorer")
    print("   How do cooperation and competition emerge?\n")

    # Define strategies
    strategies = [
        Strategy("Always Cooperate", always_cooperate),
        Strategy("Always Defect", always_defect),
        Strategy("Tit for Tat", tit_for_tat),
        Strategy("Tit for Two Tats", tit_for_two_tats),
        Strategy("Grudger", grudger),
        Strategy("Pavlov (Win-Stay)", pavlov),
        Strategy("Generous Tit for Tat", generous_tit_for_tat),
        Strategy("Suspicious Tit for Tat", suspicious_tit_for_tat),
        Strategy("Random", random_strategy),
    ]

    # Tournament mode
    if args.mode in ['tournament', 'both']:
        tournament = Tournament(strategies, rounds_per_match=100)
        tournament.run_tournament()
        tournament.print_results()

    # Evolution mode
    if args.mode in ['evolution', 'both']:
        print("=" * 60)
        print("EVOLUTIONARY SIMULATION")
        print("=" * 60)
        print("Starting with equal populations, how do strategies evolve?\n")

        initial_pop = [100] * len(strategies)
        sim = EvolutionarySimulation(strategies, initial_pop, rounds_per_match=50)

        print(f"Running {args.generations} generations...")
        sim.run(args.generations)

        sim.print_final_state()
        sim.plot_evolution()

    print("\n" + "=" * 60)
    print("✨ Cooperation emerges when the shadow of the future is long")
    print("=" * 60)


if __name__ == "__main__":
    main()
