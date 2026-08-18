"""
Lab A, parts one and two: look at the space directly.

Run:  python walk_the_space.py
      python walk_the_space.py --words cat dog truck sorrow

This script is written to be read. It prints far more than it needs to,
because the printing is the lab.
"""

import argparse
import sys

import numpy as np

# --- the words we embed by default -----------------------------------------
# Three obvious clusters, plus four traps. The traps are the interesting part:
# each has more than one meaning, and the model has no context to tell it which
# one you meant, so it has to average them.
DEFAULT_WORDS = [
    # animals
    "cat", "dog", "horse", "sparrow",
    # colors
    "red", "blue", "crimson", "turquoise",
    # emotions
    "joy", "grief", "anger", "contentment",
    # traps: each of these is at least two different words wearing one spelling
    "bank", "light", "charge", "spring",
]

WORD_ARITHMETIC = [
    ("king", "man", "woman"),      # the famous one
    ("paris", "france", "japan"),  # capital-of, usually works
    ("walking", "walk", "swim"),   # verb tense, sometimes works
    ("better", "good", "bad"),     # comparative, often fails
]


def load_model(name):
    """Import late and fail with something a human can act on."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        sys.exit(
            "sentence-transformers is not installed.\n"
            "  pip install -r requirements.txt\n"
            "See ../SETUP.md if that fails."
        )
    print(f"Loading {name} ...")
    print("(First run downloads the model. ~90MB for the default. Once only.)\n")
    return SentenceTransformer(name)


def cosine_matrix(vectors):
    """
    Cosine similarity between every pair.

    This is the whole of Chapter 1, idea one:
      1. divide each vector by its own length, so magnitude stops mattering
      2. take the dot product of every pair

    numpy does step 2 for all pairs at once with a single matrix multiply.
    """
    lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
    unit = vectors / lengths
    return unit @ unit.T


def print_matrix(words, sims):
    """Print the similarity matrix. Ugly, deliberate, readable."""
    width = max(len(w) for w in words) + 1
    header = " " * width + "".join(f"{w[:5]:>6}" for w in words)
    print(header)
    for i, w in enumerate(words):
        row = "".join(f"{sims[i][j]:>6.2f}" for j in range(len(words)))
        print(f"{w:<{width}}{row}")
    print()


def report_neighbours(words, sims, k=3):
    """For each word, its nearest neighbours. This is where the traps show up."""
    print("=" * 68)
    print("NEAREST NEIGHBOURS")
    print("=" * 68)
    print("Look for the words that landed somewhere you didn't expect.\n")
    for i, w in enumerate(words):
        order = np.argsort(-sims[i])
        neighbours = [(words[j], sims[i][j]) for j in order if j != i][:k]
        pretty = ", ".join(f"{n} ({s:.2f})" for n, s in neighbours)
        print(f"  {w:<14} -> {pretty}")
    print()


def report_extremes(words, sims):
    """The single most and least similar pairs in the set."""
    n = len(words)
    pairs = [(sims[i][j], words[i], words[j])
             for i in range(n) for j in range(i + 1, n)]
    pairs.sort()
    print("=" * 68)
    print("EXTREMES")
    print("=" * 68)
    print("  Most similar pair:  "
          f"{pairs[-1][1]} / {pairs[-1][2]}  ({pairs[-1][0]:.3f})")
    print("  Least similar pair: "
          f"{pairs[0][1]} / {pairs[0][2]}  ({pairs[0][0]:.3f})")
    print()
    print("  Note how far the 'least similar' number is from -1.")
    print("  Two unrelated English words are not opposites. They are")
    print("  perpendicular-ish, which is what near-zero means. Genuine")
    print("  negative similarity is rare and usually means something odd.")
    print()


def report_random_baseline(dims, trials=4000, seed=0):
    """
    Chapter 2's claim, checked empirically: in high dimensions, two random
    vectors are almost always near-perpendicular. This is why the whole
    approach works, and it is why a similarity of 0.4 is not 'sort of similar'.
    """
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(trials, dims))
    b = rng.normal(size=(trials, dims))
    a /= np.linalg.norm(a, axis=1, keepdims=True)
    b /= np.linalg.norm(b, axis=1, keepdims=True)
    sims = np.sum(a * b, axis=1)

    print("=" * 68)
    print(f"RANDOM BASELINE  ({dims} dimensions, {trials} random pairs)")
    print("=" * 68)
    print(f"  mean similarity:   {sims.mean():+.4f}   (expect ~0)")
    print(f"  std deviation:     {sims.std():.4f}   "
          f"(expect ~{1 / np.sqrt(dims):.4f}, which is 1/sqrt(dims))")
    print(f"  largest of {trials}:  {sims.max():.4f}")
    print()
    print("  Now recalibrate. Against this baseline, a real-word similarity")
    print(f"  of 0.40 sits about {0.40 / sims.std():.0f} standard deviations off random.")
    print("  It is not 'a bit similar'. It is enormously similar.")
    print()
    print("  This is why picking a retrieval threshold by intuition goes wrong,")
    print("  and why 'how did we choose that number' is a question worth asking.")
    print()


def word_arithmetic(model, triples):
    """
    king - man + woman = ?

    Some of these will work. Some will produce nonsense. The failures are
    more informative than the successes: they tell you which properties the
    model encoded as clean linear directions and which it didn't.
    """
    print("=" * 68)
    print("WORD ARITHMETIC")
    print("=" * 68)
    print("a - b + c = ?   Searching against a small fixed vocabulary.\n")

    vocab = sorted(set(
        DEFAULT_WORDS + [w for t in triples for w in t] + [
            "queen", "king", "man", "woman", "boy", "girl",
            "tokyo", "paris", "france", "japan", "london", "england",
            "swimming", "swim", "walking", "walk", "running", "run",
            "worse", "better", "good", "bad", "best", "worst",
        ]
    ))
    vecs = np.asarray(model.encode(vocab))
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
    index = {w: i for i, w in enumerate(vocab)}

    for a, b, c in triples:
        if not all(w in index for w in (a, b, c)):
            print(f"  {a} - {b} + {c}: skipped (word not in test vocabulary)")
            continue
        target = vecs[index[a]] - vecs[index[b]] + vecs[index[c]]
        target /= np.linalg.norm(target)
        scores = vecs @ target
        # exclude the three inputs; the arithmetic usually lands on them
        for w in (a, b, c):
            scores[index[w]] = -np.inf
        best = np.argsort(-scores)[:3]
        pretty = ", ".join(f"{vocab[i]} ({scores[i]:.2f})" for i in best)
        print(f"  {a} - {b} + {c} = {pretty}")

    print()
    print("  Did some of those fail? Good — that is the finding.")
    print("  Sentence-embedding models are contextual: the vector for a word")
    print("  depends on its surroundings, and here there are no surroundings.")
    print("  The clean king/queen result you have read about came from older")
    print("  word-level models. The underlying claim (directions carry meaning)")
    print("  holds. The party trick is oversold. Both are true.")
    print()


def main():
    p = argparse.ArgumentParser(description="Lab A: walk the embedding space.")
    p.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2",
                   help="any sentence-transformers model; see ../CURRENT.md")
    p.add_argument("--words", nargs="+", default=None,
                   help="your own words instead of the defaults")
    p.add_argument("--skip-arithmetic", action="store_true")
    args = p.parse_args()

    words = args.words or DEFAULT_WORDS
    model = load_model(args.model)

    vectors = np.asarray(model.encode(words))
    print(f"Embedded {len(words)} words.")
    print(f"Each one is now a list of {vectors.shape[1]} numbers.\n")

    print("Here are the first 8 numbers of the vector for '{}':".format(words[0]))
    print("  ", np.round(vectors[0][:8], 4))
    print()
    print("  Nobody chose what those dimensions mean. There is no 'animal'")
    print("  axis. They are whatever coordinate system happened to be useful")
    print("  for the task the model was trained on. The structure you are")
    print("  about to see was never specified by anyone.")
    print()

    sims = cosine_matrix(vectors)
    print("=" * 68)
    print("SIMILARITY MATRIX")
    print("=" * 68)
    print_matrix(words, sims)

    report_neighbours(words, sims)
    report_extremes(words, sims)
    report_random_baseline(vectors.shape[1])

    if not args.skip_arithmetic and args.words is None:
        word_arithmetic(model, WORD_ARITHMETIC)

    print("=" * 68)
    print("NOW DO PART THREE")
    print("=" * 68)
    print("  python cluster_your_data.py --csv your_file.csv --column text")
    print()
    print("  Part three is the one that changes how you think. Use real text")
    print("  from your own work, not the sample file.")
    print()


if __name__ == "__main__":
    main()
