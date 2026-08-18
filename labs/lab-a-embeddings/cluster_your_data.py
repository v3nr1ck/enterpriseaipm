"""
Lab A, part three: cluster your own text, with no labels and no training.

Run:  python cluster_your_data.py                          # uses sample_tickets.csv
      python cluster_your_data.py --csv mine.csv --column body
      python cluster_your_data.py --csv mine.csv --column body --clusters 6

Then compare what comes out against however your company currently
categorizes that same data. That comparison IS the lab.
"""

import argparse
import csv
import sys
from collections import Counter

import numpy as np

STOPWORDS = set("""
a an the and or but if then than that this these those there here it its it's
i me my we our you your he she they them his her their is are was were be been
being am do does did doing have has had having will would can could should may
might must of in on at to for with from by as about into over after before
not no nor so very just also too own same s t don now
""".split())


def load_rows(path, column):
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                sys.exit(f"{path} appears to be empty.")
            if column not in reader.fieldnames:
                sys.exit(
                    f"No column named '{column}' in {path}.\n"
                    f"Columns found: {', '.join(reader.fieldnames)}\n"
                    f"Re-run with --column <one of those>"
                )
            rows = [r[column].strip() for r in reader if r.get(column, "").strip()]
    except FileNotFoundError:
        sys.exit(f"Can't find {path}. Check the path, or omit --csv to use the sample.")
    except UnicodeDecodeError:
        sys.exit(
            f"{path} isn't UTF-8. Re-save it as UTF-8 CSV and try again.\n"
            "(Excel: Save As -> CSV UTF-8.)"
        )
    if len(rows) < 10:
        sys.exit(f"Only found {len(rows)} rows of text. Use at least 30 for this to mean anything.")
    return rows


def label_cluster(texts, k=4):
    """
    Crude keyword labelling: the most distinctive frequent words.
    Deliberately dumb. The point is to see the grouping, not to name it well.
    """
    counts = Counter()
    for t in texts:
        words = [w.strip(".,!?;:'\"()[]").lower() for w in t.split()]
        counts.update(w for w in words if len(w) > 3 and w not in STOPWORDS)
    return ", ".join(w for w, _ in counts.most_common(k)) or "(no clear keywords)"


def main():
    p = argparse.ArgumentParser(description="Lab A part three: cluster your own text.")
    p.add_argument("--csv", default="sample_tickets.csv")
    p.add_argument("--column", default="text")
    p.add_argument("--clusters", type=int, default=0,
                   help="0 = try several and show you the options")
    p.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    p.add_argument("--examples", type=int, default=3,
                   help="how many rows to print per cluster")
    args = p.parse_args()

    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
    except ImportError:
        sys.exit("Missing dependencies. Run: pip install -r requirements.txt")

    rows = load_rows(args.csv, args.column)
    print(f"Loaded {len(rows)} rows from {args.csv} (column '{args.column}').\n")

    print(f"Loading {args.model} ...")
    model = SentenceTransformer(args.model)
    print("Embedding ...\n")
    vectors = np.asarray(model.encode(rows, show_progress_bar=True))
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    # --- how many clusters? -------------------------------------------------
    if args.clusters:
        chosen = args.clusters
    else:
        print("\n" + "=" * 68)
        print("HOW MANY CLUSTERS?")
        print("=" * 68)
        print("Silhouette score: roughly, how cleanly separated the groups are.")
        print("Higher is tighter. This is a hint, not an answer.\n")
        best, chosen = -1, 4
        upper = min(9, max(3, len(rows) // 4))
        for k in range(2, upper + 1):
            km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(vectors)
            score = silhouette_score(vectors, km.labels_)
            marker = ""
            if score > best:
                best, chosen, marker = score, k, "   <-- tightest so far"
            print(f"  k={k}:  {score:.3f}{marker}")
        print(f"\nGoing with k={chosen}. Override with --clusters N.\n")

    km = KMeans(n_clusters=chosen, n_init=10, random_state=0).fit(vectors)
    labels = km.labels_

    # --- report -------------------------------------------------------------
    print("=" * 68)
    print(f"{chosen} CLUSTERS, FOUND WITHOUT ANY LABELS")
    print("=" * 68)
    print()

    for c in range(chosen):
        members = [rows[i] for i in range(len(rows)) if labels[i] == c]
        centre = km.cluster_centers_[c]
        centre = centre / np.linalg.norm(centre)
        idx = [i for i in range(len(rows)) if labels[i] == c]
        closeness = [(float(vectors[i] @ centre), rows[i]) for i in idx]
        closeness.sort(reverse=True)

        plural = "row" if len(members) == 1 else "rows"
        print(f"CLUSTER {c}  ({len(members)} {plural})")
        print(f"  keywords: {label_cluster(members)}")
        print("  most central examples:")
        for score, text in closeness[:args.examples]:
            snippet = text if len(text) <= 90 else text[:87] + "..."
            print(f"    [{score:.2f}] {snippet}")
        if len(closeness) > 1:
            score, text = closeness[-1]
            snippet = text if len(text) <= 90 else text[:87] + "..."
            print(f"  least central (the awkward one):")
            print(f"    [{score:.2f}] {snippet}")
        print()

    print("=" * 68)
    print("WHAT JUST HAPPENED")
    print("=" * 68)
    print("  You did not define categories.")
    print("  You did not label a single row.")
    print("  You did not train anything.")
    print()
    print("  The groups were already there, in the geometry, because the")
    print("  embedding model put semantically similar text near itself.")
    print("  All k-means did was notice.")
    print()
    print("  Now the actual lab: pull up however your company currently")
    print("  categorizes this same data. Compare. Where the machine split")
    print("  something your taxonomy merges, or merged something your")
    print("  taxonomy splits, ask which one is wrong. Sometimes it's the")
    print("  machine. Often it isn't.")
    print()
    print("  Look especially at the 'least central' rows above. Those are")
    print("  the items that don't really belong to any group — which is")
    print("  usually where your real edge cases live.")
    print()


if __name__ == "__main__":
    main()
