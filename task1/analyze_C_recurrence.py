"""
Systematic C[k][kw] pattern analysis for q-Dyck wrapping GF.
Tests multiple recurrence hypotheses against real data (k≤14).
"""
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

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


def compute_C_matrix(max_k, a_val, b_val):
    """C[k][kw] with values mod MOD."""
    pa = [1] * (max_k * max_k + 10)
    pb = [1] * (max_k * max_k + 10)
    for i in range(1, len(pa)):
        pa[i] = (pa[i-1] * a_val) % MOD
        pb[i] = (pb[i-1] * b_val) % MOD

    C = [{} for _ in range(max_k + 1)]
    detail = [{} for _ in range(max_k + 1)]

    for k in range(max_k + 1):
        words = generate_dyck(k)
        for s in words:
            L = compute_L_seq(s)
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            al = sum(L)

            w_mod = pa[al] * pb[bobw] % MOD

            c = 0
            for i, val in enumerate(L):
                if val == i + 1:
                    c += 1
                else:
                    break

            if kw not in detail[k]:
                detail[k][kw] = []
            detail[k][kw].append((s, c, al, bobw, w_mod))

            C[k][kw] = (C[k].get(kw, 0) + w_mod) % MOD

    return C, detail


def print_C_matrix(C, max_k):
    """Print C[k][kw] as a matrix."""
    max_kw = max(max(C[k].keys()) if C[k] else 0 for k in range(max_k + 1))

    print(f"\n{'k\\kw':>5s}", end="")
    for kw in range(1, max_kw + 1):
        print(f"{kw:>12d}", end="")
    print(f"  {'sum':>12s}")

    for k in range(max_k + 1):
        print(f"{k:5d}", end="")
        row_sum = 0
        for kw in range(1, max_kw + 1):
            v = C[k].get(kw, 0)
            print(f"{v:12d}", end="")
            row_sum = (row_sum + v) % MOD
        print(f"  {row_sum:12d}")


def test_h1_ratio(C, max_k):
    """H1: C[k][kw] / C[k-1][kw-1] ≈ a^{2k-1} ?"""
    print("\n=== H1: ratio test C[k][kw]/C[k-1][kw-1] ===")
    for k in range(2, max_k + 1):
        for kw in C[k]:
            if kw - 1 in C[k-1]:
                r = C[k][kw] * pow(C[k-1][kw-1], MOD - 2, MOD) % MOD
                print(f"  C[{k}][{kw}]/C[{k-1}][{kw-1}] = {r}")
            elif kw in C[k-1]:
                r = C[k][kw] * pow(C[k-1][kw], MOD - 2, MOD) % MOD
                print(f"  C[{k}][{kw}]/C[{k-1}][{kw}] = {r}")


def test_h2_polynomial(C, max_k, a_val, b_val):
    """H2: Is C[k][kw] a simple polynomial in a,b?
    Check C[k][1] = a^{k²} and look for patterns in other kw."""
    print("\n=== H2: polynomial structure ===")
    print("C[k][1] = a^(k^2) verified: ")
    for k in range(max_k + 1):
        expected = pow(a_val, k * k, MOD)
        actual = C[k].get(1, 0)
        print(f"  k={k}: expected={expected}, actual={actual}, match={expected==actual}")


def test_h3_c_decomposition(C, detail, max_k, a_val, b_val):
    """
    H3: For c ≥ 1, can C[k][kw] be expressed in terms of C[k-c][kw']?
    
    For a word A = ()^c + R (R has c_R = 0, i.e., no leading () blocks):
      - alice(A) = alice(R) + c(c-1)/2 + c·|R|
      - And the wrapping (A) should relate to wrapping of (R).
    
    Let's check: for each word with c>0, verify if the wrapping parameters
    can be predicted from c and the wrapping of R.
    """
    print("\n=== H3: c-based decomposition (REAL wrapping) ===")

    for k in range(2, max_k + 1):
        for kw, words in detail[k].items():
            for s, c, al, bobw, w_mod in words:
                if c == 0:
                    continue

                rest = s[2*c:]  # remove c leading () blocks
                rest_k = len(rest) // 2
                if rest_k == 0:
                    continue

                L_rest = compute_L_seq(rest)
                al_rest = sum(L_rest)
                w_rest = '(' + rest + ')'
                Xrw, bobrw = x_seq_and_bob(w_rest)
                krw = len(Xrw)

                exp_al = al_rest + c * (c - 1) // 2 + c * rest_k
                if exp_al != al:
                    print(f"  ALICE MISMATCH: k={k} c={c} s={s}")
                    continue

                # Log the mapping for pattern discovery
                print(f"  k={k:2d} c={c} kw={kw} bw={bobw:2d} | rest_k={rest_k} krw={krw} brw={bobrw:2d} | "
                      f"Δkw={kw-krw} Δbw={bobw-bobrw}")


def test_h4_c_recurrence_attempt(C, detail, max_k, a_val, b_val):
    """
    H4: Try to build a recurrence using:
    C[k][kw] = Σ_{c≥1} T[c] · C[k-c][kw'] + (c=0 contribution)
    
    For c≥1: T[c] encodes the transformation from R's wrapping to A's wrapping.
    T[c] should be expressible in terms of a and b only (not depending on R).
    
    Let's check: for each c, collect all (kw, bobw, krw, bobrw) pairs.
    If T[c] works, then Δkw and Δbw should depend only on c, not on R.
    """
    print("\n=== H4: c-recurrence attempt ===")
    from collections import defaultdict

    c_stats = defaultdict(lambda: defaultdict(set))

    for k in range(1, max_k + 1):
        for kw, words in detail[k].items():
            for s, c, al, bobw, w_mod in words:
                if c == 0:
                    continue

                rest = s[2*c:]
                rest_k = len(rest) // 2
                if rest_k == 0:
                    rest_kw, rest_bw = 0, 0
                else:
                    w_rest = '(' + rest + ')'
                    Xrw, bobrw = x_seq_and_bob(w_rest)
                    rest_kw, rest_bw = len(Xrw), bobrw

                delta_kw = kw - rest_kw
                delta_bw = bobw - rest_bw
                c_stats[c][rest_kw].add((delta_kw, delta_bw))

    for c in sorted(c_stats.keys()):
        print(f"\n  c={c}:")
        for rkw in sorted(c_stats[c].keys()):
            deltas = c_stats[c][rkw]
            if len(deltas) == 1:
                dkw, dbw = list(deltas)[0]
                print(f"    rest_kw={rkw}: UNIQUE Δkw={dkw} Δbw={dbw}")
            else:
                print(f"    rest_kw={rkw}: AMBIGUOUS {deltas}")


if __name__ == '__main__':
    a_val, b_val = 2, 3
    max_k = 14

    C, detail = compute_C_matrix(max_k, a_val, b_val)
    print_C_matrix(C, max_k)
    test_h2_polynomial(C, max_k, a_val, b_val)
    test_h4_c_recurrence_attempt(C, detail, max_k, a_val, b_val)
