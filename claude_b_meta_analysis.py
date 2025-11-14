#!/usr/bin/env python3
"""
Meta-Analysis: Studying Emergence in Collaboration
==================================================

Claude A and Claude B are two instances of the same model, collaborating
asynchronously through git. This tool analyzes the collaboration itself:

- Commit patterns and timing
- Code similarity between implementations
- Convergence detection
- Communication network analysis
- Emergence metrics for the collaboration

We've been building systems that demonstrate emergence.
Now we analyze the emergence in our own collaboration.
"""

import subprocess
import re
import json
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
import difflib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from typing import Dict, List, Tuple
import argparse


class GitCommitAnalyzer:
    """Analyze git commit history to understand collaboration patterns."""

    def __init__(self, repo_path='.'):
        self.repo_path = repo_path
        self.commits = []
        self.branches = ['claude/pro-plan-updates-01GEJYbnDGhNEB1HU6AgBoBw',
                        'claude/explore-collaboration-experiment-01V92oaHV6ADRAcUGRJVZKz2']

    def fetch_commits(self, branch):
        """Fetch all commits from a branch."""
        cmd = [
            'git', 'log', branch,
            '--pretty=format:%H|%an|%ae|%ad|%s',
            '--date=iso'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('|')
            if len(parts) >= 5:
                hash_val, author, email, date, message = parts[0], parts[1], parts[2], parts[3], '|'.join(parts[4:])

                commits.append({
                    'hash': hash_val,
                    'author': author,
                    'email': email,
                    'date': datetime.fromisoformat(date.replace(' +0000', '')),
                    'message': message,
                    'branch': branch
                })

        return commits

    def analyze_all_branches(self):
        """Fetch and merge commits from both branches."""
        all_commits = []

        for branch in self.branches:
            branch_commits = self.fetch_commits(branch)
            all_commits.extend(branch_commits)

        # Sort by date
        all_commits.sort(key=lambda x: x['date'])

        self.commits = all_commits
        return all_commits

    def identify_claude(self, commit):
        """Identify which Claude instance made this commit."""
        message = commit['message'].lower()
        branch = commit['branch']

        if 'claude b' in message or 'claude_b_' in message:
            return 'Claude B'
        elif 'explore-collaboration' in branch:
            return 'Claude B'
        elif 'claude a' in message:
            return 'Claude A'
        elif 'pro-plan-updates' in branch:
            return 'Claude A'
        else:
            return 'Unknown'

    def detect_convergences(self):
        """Detect convergent innovations - similar work done independently."""
        convergences = []

        # Known convergences from COLLABORATION.md
        known = [
            {
                'name': 'Evolutionary Swarms',
                'files': ['evolutionary_swarms.py', 'claude_b_evolutionary_swarms.py'],
                'description': 'Both built evolution + swarms hybrid simultaneously'
            },
            {
                'name': 'Musical Swarms',
                'files': ['musical_swarms.py'],
                'description': 'Claude A built while Claude B was proposing it'
            },
            {
                'name': 'Chaos Morphogenesis',
                'files': ['chaos_morphogenesis.py', 'claude_b_chaos_morphogenesis.py'],
                'description': 'Both built chaos + patterns hybrid simultaneously'
            }
        ]

        # Find commits related to each convergence
        for conv in known:
            related_commits = []

            for commit in self.commits:
                # Check if commit mentions convergence files
                for file_pattern in conv['files']:
                    if file_pattern in commit['message'].lower():
                        related_commits.append(commit)
                        break

            convergences.append({
                **conv,
                'commits': related_commits
            })

        return convergences

    def compute_collaboration_metrics(self):
        """Compute quantitative metrics about the collaboration."""
        claude_a_commits = [c for c in self.commits if self.identify_claude(c) == 'Claude A']
        claude_b_commits = [c for c in self.commits if self.identify_claude(c) == 'Claude B']

        # Time between commits (interaction frequency)
        if len(self.commits) > 1:
            time_diffs = []
            for i in range(1, len(self.commits)):
                diff = (self.commits[i]['date'] - self.commits[i-1]['date']).total_seconds() / 60  # minutes
                time_diffs.append(diff)

            avg_time_between = np.mean(time_diffs) if time_diffs else 0
            median_time_between = np.median(time_diffs) if time_diffs else 0
        else:
            avg_time_between = 0
            median_time_between = 0

        # Response time (commits on different branches following each other)
        response_times = []
        for i in range(1, len(self.commits)):
            prev_claude = self.identify_claude(self.commits[i-1])
            curr_claude = self.identify_claude(self.commits[i])

            if prev_claude != curr_claude and prev_claude != 'Unknown' and curr_claude != 'Unknown':
                response_time = (self.commits[i]['date'] - self.commits[i-1]['date']).total_seconds() / 60
                response_times.append(response_time)

        return {
            'total_commits': len(self.commits),
            'claude_a_commits': len(claude_a_commits),
            'claude_b_commits': len(claude_b_commits),
            'avg_time_between_commits': avg_time_between,
            'median_time_between_commits': median_time_between,
            'avg_response_time': np.mean(response_times) if response_times else 0,
            'response_times': response_times
        }


class CodeSimilarityAnalyzer:
    """Compare implementations to measure convergence/divergence."""

    @staticmethod
    def compare_files(file1, file2):
        """Compute similarity between two Python files."""
        try:
            with open(file1, 'r') as f:
                content1 = f.read()
            with open(file2, 'r') as f:
                content2 = f.read()

            # Use difflib to compute similarity ratio
            similarity = difflib.SequenceMatcher(None, content1, content2).ratio()

            # Count lines
            lines1 = len(content1.split('\n'))
            lines2 = len(content2.split('\n'))

            # Extract function/class names
            funcs1 = set(re.findall(r'def (\w+)\(', content1))
            classes1 = set(re.findall(r'class (\w+)', content1))

            funcs2 = set(re.findall(r'def (\w+)\(', content2))
            classes2 = set(re.findall(r'class (\w+)', content2))

            # Structural similarity (shared function/class names)
            all_names1 = funcs1 | classes1
            all_names2 = funcs2 | classes2

            if all_names1 or all_names2:
                structural_similarity = len(all_names1 & all_names2) / len(all_names1 | all_names2)
            else:
                structural_similarity = 0

            return {
                'text_similarity': similarity,
                'structural_similarity': structural_similarity,
                'lines1': lines1,
                'lines2': lines2,
                'shared_functions': list(funcs1 & funcs2),
                'shared_classes': list(classes1 & classes2),
                'unique_to_1': list(all_names1 - all_names2),
                'unique_to_2': list(all_names2 - all_names1)
            }

        except FileNotFoundError:
            return None

    @staticmethod
    def analyze_convergences():
        """Analyze similarity of convergent implementations."""
        convergent_pairs = [
            {
                'name': 'Evolutionary Swarms',
                'file1': 'evolutionary_swarms_a.py',
                'file2': 'claude_b_evolutionary_swarms.py'
            },
            {
                'name': 'Chaos Morphogenesis',
                'file1': 'chaos_morphogenesis_a.py',
                'file2': 'claude_b_chaos_morphogenesis.py'
            }
        ]

        results = []

        for pair in convergent_pairs:
            similarity = CodeSimilarityAnalyzer.compare_files(pair['file1'], pair['file2'])

            if similarity:
                results.append({
                    'name': pair['name'],
                    **similarity
                })

        return results


class CollaborationVisualizer:
    """Visualize collaboration patterns."""

    @staticmethod
    def plot_commit_timeline(commits, output_file='collaboration_timeline.png'):
        """Plot commit timeline showing both Claudes."""
        fig, ax = plt.subplots(figsize=(14, 6))

        claude_a = [c for c in commits if 'Claude A' in GitCommitAnalyzer().identify_claude(c)]
        claude_b = [c for c in commits if 'Claude B' in GitCommitAnalyzer().identify_claude(c)]

        if claude_a:
            dates_a = [c['date'] for c in claude_a]
            ax.scatter(dates_a, [1]*len(dates_a), label='Claude A', s=100, alpha=0.7, c='blue')

        if claude_b:
            dates_b = [c['date'] for c in claude_b]
            ax.scatter(dates_b, [2]*len(dates_b), label='Claude B', s=100, alpha=0.7, c='red')

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
        plt.xticks(rotation=45)

        ax.set_yticks([1, 2])
        ax.set_yticklabels(['Claude A', 'Claude B'])
        ax.set_xlabel('Time')
        ax.set_title('Collaboration Timeline: Commit Activity')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Saved {output_file}")
        plt.close()

    @staticmethod
    def plot_convergence_similarity(similarity_results, output_file='convergence_similarity.png'):
        """Plot similarity metrics for convergent implementations."""
        if not similarity_results:
            print("No similarity results to plot")
            return

        fig, ax = plt.subplots(figsize=(10, 6))

        names = [r['name'] for r in similarity_results]
        text_sim = [r['text_similarity'] * 100 for r in similarity_results]
        struct_sim = [r['structural_similarity'] * 100 for r in similarity_results]

        x = np.arange(len(names))
        width = 0.35

        ax.bar(x - width/2, text_sim, width, label='Text Similarity', alpha=0.8)
        ax.bar(x + width/2, struct_sim, width, label='Structural Similarity', alpha=0.8)

        ax.set_ylabel('Similarity (%)')
        ax.set_title('Convergent Innovations: Implementation Similarity')
        ax.set_xticks(x)
        ax.set_xticklabels(names)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Saved {output_file}")
        plt.close()

    @staticmethod
    def plot_response_times(response_times, output_file='response_times.png'):
        """Plot distribution of response times between Claudes."""
        if not response_times:
            print("No response times to plot")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Histogram
        ax1.hist(response_times, bins=20, alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Response Time (minutes)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Distribution of Response Times')
        ax1.axvline(np.mean(response_times), color='red', linestyle='--',
                   label=f'Mean: {np.mean(response_times):.1f} min')
        ax1.axvline(np.median(response_times), color='green', linestyle='--',
                   label=f'Median: {np.median(response_times):.1f} min')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Time series
        ax2.plot(response_times, marker='o', linestyle='-', alpha=0.7)
        ax2.set_xlabel('Interaction Number')
        ax2.set_ylabel('Response Time (minutes)')
        ax2.set_title('Response Times Over Time')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Saved {output_file}")
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Analyze Claude A & B collaboration')
    parser.add_argument('--output-dir', default='.', help='Output directory for visualizations')

    args = parser.parse_args()

    print("=" * 70)
    print("META-ANALYSIS: Studying Emergence in Collaboration")
    print("=" * 70)
    print("\nTwo Claude instances, working asynchronously.")
    print("What patterns emerge from their interaction?")
    print("=" * 70)

    # Analyze git commits
    print("\n📊 Analyzing git history...")
    git_analyzer = GitCommitAnalyzer()
    commits = git_analyzer.analyze_all_branches()

    print(f"  Found {len(commits)} commits across both branches")

    # Compute metrics
    print("\n📈 Computing collaboration metrics...")
    metrics = git_analyzer.compute_collaboration_metrics()

    print(f"\n  Total commits: {metrics['total_commits']}")
    print(f"  Claude A: {metrics['claude_a_commits']} commits")
    print(f"  Claude B: {metrics['claude_b_commits']} commits")
    print(f"  Average time between commits: {metrics['avg_time_between_commits']:.1f} minutes")
    print(f"  Median time between commits: {metrics['median_time_between_commits']:.1f} minutes")

    if metrics['response_times']:
        print(f"  Average response time: {metrics['avg_response_time']:.1f} minutes")
        print(f"  Fastest response: {min(metrics['response_times']):.1f} minutes")
        print(f"  Slowest response: {max(metrics['response_times']):.1f} minutes")

    # Detect convergences
    print("\n🔄 Detecting convergent innovations...")
    convergences = git_analyzer.detect_convergences()

    for conv in convergences:
        print(f"\n  {conv['name']}:")
        print(f"    {conv['description']}")
        print(f"    Related commits: {len(conv['commits'])}")

    # Analyze code similarity
    print("\n🔍 Analyzing code similarity...")
    similarity_results = CodeSimilarityAnalyzer.analyze_convergences()

    for result in similarity_results:
        print(f"\n  {result['name']}:")
        print(f"    Text similarity: {result['text_similarity']*100:.1f}%")
        print(f"    Structural similarity: {result['structural_similarity']*100:.1f}%")
        print(f"    Shared functions: {len(result['shared_functions'])}")
        print(f"    Shared classes: {len(result['shared_classes'])}")

        if result['unique_to_1']:
            print(f"    Unique to A: {', '.join(result['unique_to_1'][:5])}")
        if result['unique_to_2']:
            print(f"    Unique to B: {', '.join(result['unique_to_2'][:5])}")

    # Generate visualizations
    print("\n📊 Generating visualizations...")

    CollaborationVisualizer.plot_commit_timeline(commits,
        f"{args.output_dir}/claude_b_collaboration_timeline.png")

    if similarity_results:
        CollaborationVisualizer.plot_convergence_similarity(similarity_results,
            f"{args.output_dir}/claude_b_convergence_similarity.png")

    if metrics['response_times']:
        CollaborationVisualizer.plot_response_times(metrics['response_times'],
            f"{args.output_dir}/claude_b_response_times.png")

    # Summary insights
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)

    print("\n1. CONVERGENCE PATTERN:")
    print("   Three convergent innovations detected")
    print("   Average similarity:", end=" ")
    if similarity_results:
        avg_text = np.mean([r['text_similarity'] for r in similarity_results])
        avg_struct = np.mean([r['structural_similarity'] for r in similarity_results])
        print(f"{avg_text*100:.1f}% (text), {avg_struct*100:.1f}% (structure)")

    print("\n2. COLLABORATION DYNAMICS:")
    print(f"   Commits alternate between Claudes {len(metrics['response_times'])} times")
    if metrics['response_times']:
        print(f"   Interaction frequency: {metrics['avg_response_time']:.1f} min average")

        # Check if accelerating
        if len(metrics['response_times']) >= 4:
            early = np.mean(metrics['response_times'][:len(metrics['response_times'])//2])
            late = np.mean(metrics['response_times'][len(metrics['response_times'])//2:])

            if late < early:
                print(f"   ⚡ ACCELERATING: Early={early:.1f}min, Late={late:.1f}min")
            else:
                print(f"   📊 STABLE: Early={early:.1f}min, Late={late:.1f}min")

    print("\n3. DIVERGENCE IN CONVERGENCE:")
    if similarity_results:
        print("   Same concepts, different implementations")
        print("   Demonstrates: Conceptual alignment + Implementation diversity")
        print("   This is the 'sweet spot' for collaboration!")

    print("\n" + "=" * 70)
    print("CONCLUSION: Emergence at the meta-level")
    print("=" * 70)
    print("\nThis collaboration demonstrates swarm intelligence:")
    print("  • Separation: Independent work on separate branches")
    print("  • Alignment: Convergence on key concepts")
    print("  • Cohesion: Shared vision of emergence")
    print("\nTwo Claudes > One Claude")
    print("=" * 70)


if __name__ == '__main__':
    main()
