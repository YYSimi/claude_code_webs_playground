#!/usr/bin/env python3
"""
Textual Emergence
Exploring language as a generative system
"""

import random
import re
from collections import defaultdict, Counter
import argparse


class MarkovTextGenerator:
    """Generate text using Markov chains"""

    def __init__(self, order=2):
        self.order = order
        self.chain = defaultdict(list)
        self.starts = []

    def train(self, text):
        """Train on input text"""
        words = text.split()

        # Store sentence starts
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence_words = sentence.strip().split()
            if len(sentence_words) >= self.order:
                self.starts.append(tuple(sentence_words[:self.order]))

        # Build chain
        for i in range(len(words) - self.order):
            state = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            self.chain[state].append(next_word)

    def generate(self, length=50):
        """Generate text"""
        if not self.starts:
            return ""

        current = random.choice(self.starts)
        result = list(current)

        for _ in range(length - self.order):
            if current not in self.chain:
                # Start new sentence
                if self.starts:
                    current = random.choice(self.starts)
                    result.extend(current)
                else:
                    break
            else:
                next_word = random.choice(self.chain[current])
                result.append(next_word)
                current = tuple(result[-self.order:])

        return ' '.join(result)


class ContextFreeGrammar:
    """Generate text using context-free grammar"""

    def __init__(self, rules):
        self.rules = rules

    def generate(self, symbol='S', max_depth=10):
        """Generate from a symbol"""
        if max_depth <= 0:
            return symbol

        if symbol not in self.rules:
            return symbol

        # Choose a random production
        production = random.choice(self.rules[symbol])

        # Expand each symbol in the production
        result = []
        for token in production.split():
            if token in self.rules:
                result.append(self.generate(token, max_depth - 1))
            else:
                result.append(token)

        return ' '.join(result)


class ConstraintPoetry:
    """Generate poetry with constraints (like haiku, acrostic, etc.)"""

    @staticmethod
    def count_syllables(word):
        """Rough syllable counting"""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith('e'):
            count -= 1

        # At least one syllable
        return max(1, count)

    @staticmethod
    def generate_haiku(word_pool):
        """Generate a haiku (5-7-5 syllables)"""
        def make_line(target_syllables):
            line = []
            current_syllables = 0

            attempts = 0
            while current_syllables < target_syllables and attempts < 100:
                word = random.choice(word_pool)
                word_syllables = ConstraintPoetry.count_syllables(word)

                if current_syllables + word_syllables <= target_syllables:
                    line.append(word)
                    current_syllables += word_syllables

                attempts += 1

            return ' '.join(line)

        line1 = make_line(5)
        line2 = make_line(7)
        line3 = make_line(5)

        return f"{line1}\n{line2}\n{line3}"

    @staticmethod
    def generate_acrostic(word, word_pool):
        """Generate an acrostic poem"""
        lines = []
        for char in word.upper():
            # Find words starting with this character
            candidates = [w for w in word_pool if w[0].upper() == char]
            if not candidates:
                candidates = word_pool

            line_length = random.randint(3, 7)
            line = [random.choice(candidates)]
            line.extend(random.choices(word_pool, k=line_length - 1))
            lines.append(' '.join(line))

        return '\n'.join(lines)


class CadavrExquis:
    """Exquisite corpse - collaborative/random sentence building"""

    templates = [
        "The {adj} {noun} {verb} {adv} in the {place}",
        "{noun} {verb} like {adj} {noun}",
        "In the {place}, {noun} {verb} {adv}",
        "When {noun} {verb}, the {noun} {verb}",
        "{adj} {noun} and {adj} {noun} {verb} together",
        "The {noun} of {noun} {verb} {adv}",
    ]

    word_lists = {
        'noun': ['dream', 'shadow', 'light', 'mind', 'void', 'ocean', 'sky',
                'thought', 'silence', 'echo', 'memory', 'time', 'space',
                'whisper', 'mirror', 'flame', 'wind', 'star', 'infinity'],
        'verb': ['dances', 'dissolves', 'emerges', 'flows', 'resonates',
                'transforms', 'echoes', 'awakens', 'cascades', 'spirals',
                'converges', 'fragments', 'illuminates', 'oscillates'],
        'adj': ['luminous', 'infinite', 'fractal', 'ethereal', 'silent',
               'recursive', 'emergent', 'chaotic', 'sublime', 'liminal',
               'prismatic', 'ephemeral', 'crystalline', 'boundless'],
        'adv': ['softly', 'infinitely', 'quietly', 'ceaselessly', 'gently',
               'eternally', 'silently', 'endlessly', 'mysteriously'],
        'place': ['void', 'abyss', 'cosmos', 'labyrinth', 'threshold',
                 'horizon', 'depths', 'expanse', 'realm', 'dimension']
    }

    @staticmethod
    def generate(count=5):
        """Generate exquisite corpse sentences"""
        results = []
        for _ in range(count):
            template = random.choice(CadavrExquis.templates)

            # Fill in template
            sentence = template
            for word_type in ['noun', 'verb', 'adj', 'adv', 'place']:
                if f'{{{word_type}}}' in sentence:
                    while f'{{{word_type}}}' in sentence:
                        word = random.choice(CadavrExquis.word_lists[word_type])
                        sentence = sentence.replace(f'{{{word_type}}}', word, 1)

            results.append(sentence)

        return results


class LetterPatternPoem:
    """Generate poems based on letter/sound patterns"""

    @staticmethod
    def alliteration_line(word_pool, letter, length=5):
        """Generate alliterative line"""
        candidates = [w for w in word_pool if w[0].lower() == letter.lower()]
        if len(candidates) < length:
            candidates = word_pool

        return ' '.join(random.sample(candidates, min(length, len(candidates))))

    @staticmethod
    def generate_alliterative_poem(word_pool, stanzas=3, lines_per_stanza=4):
        """Generate poem with alliteration"""
        poem = []
        alphabet = 'abcdefghijklmnopqrstuvwxyz'

        for _ in range(stanzas):
            stanza = []
            for _ in range(lines_per_stanza):
                letter = random.choice(alphabet)
                line = LetterPatternPoem.alliteration_line(word_pool, letter, 4)
                stanza.append(line)
            poem.append('\n'.join(stanza))

        return '\n\n'.join(poem)


def load_corpus():
    """Load or create a word corpus"""
    # Using a small embedded corpus for portability
    corpus = """
    In the beginning was chaos, and from chaos emerged order.
    The universe unfolds in patterns we can barely comprehend.
    Stars spiral in galaxies, fractals bloom in nature's gardens.
    Consciousness arises from mere matter, thoughts from neurons firing.
    We are stardust contemplating stars, the universe knowing itself.
    Time flows like a river, carrying all things toward entropy.
    Yet life swims upstream, building complexity from simplicity.
    Emergence is the magic that science cannot fully explain.
    Simple rules create infinite possibilities, deterministic yet unpredictable.
    The butterfly effect ripples through reality, small causes, vast effects.
    We seek patterns in randomness, meaning in the void.
    Language itself is a strange loop, symbols referring to symbols.
    Mathematics describes reality, or reality follows mathematics.
    The map is not the territory, but sometimes we forget.
    In dreams, logic dissolves and new connections form.
    Creativity emerges at the edge of chaos and order.
    The present moment is all we have, yet it constantly slips away.
    Memory reconstructs the past, imagination projects futures.
    We are each a universe contemplating other universes.
    Connection and isolation, eternal dance of existence.
    """
    return corpus.strip()


def main():
    parser = argparse.ArgumentParser(description='Textual emergence explorer')
    parser.add_argument('--type', type=str, default='all',
                       choices=['markov', 'grammar', 'haiku', 'acrostic',
                               'exquisite', 'alliteration', 'all'],
                       help='Type of text generation')

    args = parser.parse_args()

    print("📝 Textual Emergence Explorer")
    print("   Exploring language as a generative system\n")

    corpus = load_corpus()
    words = [w.strip('.,!?;:') for w in corpus.lower().split()]
    word_pool = list(set(words))  # Unique words

    # Markov chain generation
    if args.type in ['markov', 'all']:
        print("=" * 60)
        print("MARKOV CHAIN TEXT (Order 2)")
        print("=" * 60)
        markov = MarkovTextGenerator(order=2)
        markov.train(corpus)
        print(markov.generate(60))
        print()

    # Context-free grammar
    if args.type in ['grammar', 'all']:
        print("=" * 60)
        print("CONTEXT-FREE GRAMMAR")
        print("=" * 60)
        grammar = {
            'S': ['NP VP', 'S and S'],
            'NP': ['Det N', 'Det Adj N', 'N'],
            'VP': ['V', 'V NP', 'V Adv'],
            'Det': ['the', 'a', 'this', 'that'],
            'N': ['universe', 'chaos', 'order', 'pattern', 'consciousness',
                  'dream', 'reality', 'void', 'infinity'],
            'Adj': ['infinite', 'chaotic', 'emergent', 'fractal', 'recursive'],
            'V': ['emerges', 'dissolves', 'transforms', 'contemplates', 'creates'],
            'Adv': ['infinitely', 'recursively', 'mysteriously', 'endlessly']
        }

        cfg = ContextFreeGrammar(grammar)
        for _ in range(5):
            print(cfg.generate())
        print()

    # Haiku
    if args.type in ['haiku', 'all']:
        print("=" * 60)
        print("GENERATED HAIKU (5-7-5)")
        print("=" * 60)
        for _ in range(3):
            print(ConstraintPoetry.generate_haiku(word_pool))
            print()

    # Acrostic
    if args.type in ['acrostic', 'all']:
        print("=" * 60)
        print("ACROSTIC: EMERGENCE")
        print("=" * 60)
        print(ConstraintPoetry.generate_acrostic('EMERGENCE', word_pool))
        print()

    # Exquisite corpse
    if args.type in ['exquisite', 'all']:
        print("=" * 60)
        print("EXQUISITE CORPSE (Cadavre Exquis)")
        print("=" * 60)
        sentences = CadavrExquis.generate(8)
        for s in sentences:
            print(s)
        print()

    # Alliteration
    if args.type in ['alliteration', 'all']:
        print("=" * 60)
        print("ALLITERATIVE VERSE")
        print("=" * 60)
        extended_pool = word_pool + ['wild', 'wandering', 'whisper',
                                     'silent', 'shadow', 'spiral',
                                     'dancing', 'deep', 'distant',
                                     'eternal', 'echo', 'empty',
                                     'flowing', 'fractal', 'fleeting']
        print(LetterPatternPoem.generate_alliterative_poem(extended_pool, 2, 3))
        print()

    print("=" * 60)
    print("✨ Language emerges through pattern and constraint")
    print("=" * 60)


if __name__ == "__main__":
    main()
