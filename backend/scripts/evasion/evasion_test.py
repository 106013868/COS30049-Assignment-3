"""
Detection evasion test (from section 2.8).

For each phishing URL in evasion_urls.csv it disguises the suspicious words
with Cyrillic letters that look the same, tries every combination of words to
disguise, and keeps the version the model trusts most. Every check goes
through POST /api/predict.

Start the back end first, then from backend/:
    python scripts/evasion/evasion_test.py before
The label (before / after) names the results file it saves.
"""
import csv
import itertools
import json
import math
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:8000/api/predict"
HERE = Path(__file__).parent

# words the attacker disguises: the usual phishing words
WORDS = ["login", "signin", "verify", "verification", "account",
         "secure", "update", "password", "bank"]

# Latin letter -> Cyrillic letter that looks the same
LOOKALIKES = {"o": "о", "e": "е", "a": "а", "i": "і",
              "c": "с", "p": "р", "s": "ѕ", "x": "х", "y": "у"}

# colours for the terminal (skipped when the output is saved to a file)
COLOUR = sys.stdout.isatty()
RED, GREEN, YELLOW, BOLD, END = (("\033[31m", "\033[32m", "\033[33m", "\033[1m", "\033[0m")
                                 if COLOUR else ("", "", "", "", ""))


def check(url):
    """sends one URL to the API, like the app's Check button; returns (verdict, trust %, keywords seen)"""
    body = json.dumps({"url": url}).encode("utf-8")
    request = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request) as response:
        result = json.load(response)
    return result["verdict"], result["trust_score"], int(result["features"]["suspicious_keyword_count"])


def disguise(url, words):
    """swaps one letter in every copy of each word for its Cyrillic look-alike"""
    chars = list(url)
    for word in words:
        letter = next(l for l in LOOKALIKES if l in word)
        offset = word.index(letter)
        start = "".join(chars).lower().find(word)
        while start != -1:
            original = chars[start + offset]
            swap = LOOKALIKES[letter]
            chars[start + offset] = swap.upper() if original.isupper() else swap
            start = "".join(chars).lower().find(word)
    return "".join(chars)


def best_disguise(url):
    """tries every combination of words to disguise; keeps the one the model trusts most"""
    present = [w for w in WORDS if w in url.lower()]
    best = None
    for size in range(1, len(present) + 1):
        for words in itertools.combinations(present, size):
            fake = disguise(url, words)
            verdict, trust, keywords = check(fake)
            if best is None or trust > best["trust"]:
                best = {"url": fake, "verdict": verdict, "trust": trust,
                        "keywords": keywords, "hidden": words}
    best["tried"] = 2 ** len(present) - 1
    return best


def label(verdict, trust):
    if verdict == "phishing":
        return f"{RED}LIKELY PHISHING{END} (trust {trust:>3}%)"
    return f"{GREEN}LIKELY SAFE{END}     (trust {trust:>3}%)"


def highlight(fake, original, width=90):
    """the look-alike URL with swapped letters in yellow"""
    shown = "".join(f"{YELLOW}{BOLD}{f}{END}" if f != o else f
                    for f, o in zip(fake[:width], original[:width]))
    return shown + ("..." if len(fake) > width else "")


def wilson(successes, n, z=1.96):
    """95% confidence interval for a rate"""
    p = successes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0, centre - margin), min(1, centre + margin)


def main(run):
    with open(HERE / "evasion_urls.csv", encoding="utf-8") as f:
        urls = [row["url"] for row in csv.DictReader(f)]

    results, requests = [], 0
    for number, url in enumerate(urls, 1):
        try:
            verdict, trust, keywords = check(url)
            fake = best_disguise(url)
        except urllib.error.HTTPError as error:
            print(f"[{number:>3}/{len(urls)}] skipped, server said {error.code}")
            continue
        requests += 1 + fake["tried"]
        got_past = verdict == "phishing" and fake["verdict"] == "legitimate"
        outcome = f"{GREEN}{BOLD}GOT PAST{END}" if got_past else "still caught"

        print(f"[{number:>3}/{len(urls)}] {highlight(fake['url'], url)}")
        print(f"          original {label(verdict, trust)}   look-alike {label(fake['verdict'], fake['trust'])}   {outcome}")

        results.append({"original": url, "lookalike": fake["url"],
                        "hidden_words": " ".join(fake["hidden"]), "versions_tried": fake["tried"],
                        "original_verdict": verdict, "original_trust": trust, "original_keywords": keywords,
                        "lookalike_verdict": fake["verdict"], "lookalike_trust": fake["trust"],
                        "lookalike_keywords": fake["keywords"], "got_past": got_past})

    n = len(results)
    caught = sum(r["original_verdict"] == "phishing" for r in results)
    still = sum(r["lookalike_verdict"] == "phishing" for r in results)
    passed = sum(r["got_past"] for r in results)
    low, high = wilson(passed, caught)
    avg = lambda key: sum(r[key] for r in results) / n

    print(f"\n{BOLD}Summary ({run}){END}")
    print(f"{'':28}{'Original':>10}{'Look-alike':>12}")
    print(f"{'Caught as phishing':28}{caught:>10}{still:>12}")
    print(f"{'Keywords the model saw':28}{avg('original_keywords'):>10.2f}{avg('lookalike_keywords'):>12.2f}")
    print(f"{'Average trust score':28}{avg('original_trust'):>9.0f}%{avg('lookalike_trust'):>11.0f}%")
    print(f"\n{BOLD}Got past the model: {passed} of {caught} ({passed / caught:.0%}){END}, "
          f"95% confidence interval {low:.0%} to {high:.0%}")
    print(f"API requests sent: {requests}")

    print("\nTrust score bands (the app says LIKELY SAFE above about 50%):")
    print(f"{'trust':>10}{'original':>10}{'look-alike':>12}")
    for start in range(0, 100, 10):
        top = 100 if start == 90 else start + 9
        a = sum(start <= r["original_trust"] <= top for r in results)
        b = sum(start <= r["lookalike_trust"] <= top for r in results)
        print(f"{start:>4}-{top:<4}% {a:>8}{b:>12}")

    out = HERE / f"evasion_results_{run}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nEvery URL's result saved to {out.name}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "before")
