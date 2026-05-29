"""
H5: Orbit-level c-based transition test.
For a fixed c and rest orbit (bw_rest, kw_rest), is the WEIGHTED distribution
of wrapped (bw, kw) predictable? I.e., does word-level ambiguity cancel out
at the orbit level?
"""
from verify_bf import generate_dyck, alice_of, x_seq_and_bob
from collections import defaultdict

MOD = 998244353


def compute_L_seq(s):
    n = len(s) // 2
    L = [0] * n
    rc = 0
    for i, ch in enumerate(s):
        if ch == ')':
            L[rc] = (i + 1) - (rc + 1)
            rc += 1
    return L


def analyze_orbit_transition(max_k=10, a_val=2):
    """For each c and rest orbit, compute the transition distribution."""
    pa = [1] * (max_k * max_k + 10)
    for i in range(1, len(pa)):
        pa[i] = (pa[i-1] * a_val) % MOD

    data_by_c = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for k in range(1, max_k + 1):
        words = generate_dyck(k)
        for s in words:
            L = compute_L_seq(s)
            c = 0
            for i, val in enumerate(L):
                if val == i + 1:
                    c += 1
                else:
                    break
            if c == 0:
                continue

            rest = s[2*c:]
            rest_k = len(rest) // 2

            if rest_k == 0:
                continue

            L_rest = compute_L_seq(rest)
            al_rest = sum(L_rest)
            wr = '(' + rest + ')'
            Xrw, bobrw = x_seq_and_bob(wr)
            krw = len(Xrw)
            rest_orbit = (bobrw, krw)
            rest_alpha = pa[al_rest]

            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            al = sum(L)
            alpha = pa[al]

            target_orbit = (bobw, kw)

            data_by_c[c][rest_orbit][target_orbit] += alpha / rest_alpha

    return data_by_c


def check_transition_regularity(data_by_c):
    """Check if the transition distribution has a pattern."""
    print("=== H5: Orbit-level c-transition analysis ===\n")

    for c in sorted(data_by_c.keys()):
        print(f"\n--- c={c} ---")
        for rest_orbit, targets in sorted(data_by_c[c].items()):
            bwr, kwr = rest_orbit
            nontrivial = [(bw, kw, w) for (bw, kw), w in targets.items() if bw != bwr or kw != kwr]
            print(f"  rest=({bwr},{kwr}): {len(targets)} target orbits")

            if len(nontrivial) >= 1 and len(nontrivial) <= 5:
                for bw, kw, w in nontrivial:
                    print(f"    -> ({bw},{kw}): weight={w:.2f}")


if __name__ == '__main__':
    data = analyze_orbit_transition(10)
    check_transition_regularity(data)
