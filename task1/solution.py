"""
solution.py — Bracket Weighted Counting
======================================
Generating function approach:
  F(x) = 1 + Σ_{k≥0, kw} C[k][kw] · a^{2k+3} · x^{k+2} · F(a^{k+2} b^{kw} x)

where C[k][kw] = Σ_{A:|A|=k, k((A))=kw} a^{alice(A)} · b^{bob((A))}.

Coefficient extraction:
  F[n] = Σ_{m=1}^{n} Σ_{kw} D[m][kw] · (a^m b^{kw})^{n-m} · F[n-m]
  D[m][kw] = C[m-1][kw] · a^{2m-1}

Current limitation: C[k][kw] requires Catalan enumeration for k>14.
Works correctly for N≤14.
"""
import sys

MOD = 998244353


def generate_dyck(n):
    words = []
    def bt(s, op, cl):
        if cl > op or op > n:
            return
        if len(s) == 2*n:
            if op == n and cl == n:
                words.append(s)
            return
        bt(s + '(', op+1, cl)
        bt(s + ')', op, cl+1)
    bt('', 0, 0)
    return words


def alice_of(s):
    n = len(s)//2
    cnt = 0
    for i in range(2*n):
        if s[i] == '(':
            for j in range(i+1, 2*n):
                if s[j] == ')':
                    cnt += 1
    return cnt


def x_seq_and_bob(s):
    n = len(s)//2
    h = [0]*(2*n+1)
    for i in range(2*n):
        h[i+1] = h[i] + (1 if s[i]=='(' else -1)
    cum = 0
    X = []
    while cum < n:
        pos = 2*cum
        t = 1
        best_x = 0
        while pos + t <= 2*n:
            if h[pos + t] == t:
                best_x = t
                t += 1
            elif h[pos + t] > t:
                t += 1
            else:
                break
        if best_x == 0:
            best_x = 1
        X.append(best_x)
        cum += best_x
    bob = 0
    for j in range(len(X)):
        bob += j * X[j]
    return X, bob


def compute_C(max_k, a_val, b_val):
    """C[k][kw] for k=0..max_k via Catalan enumeration."""
    pa = [1] * (max_k * max_k + 10)
    pb = [1] * (max_k * max_k + 10)
    for i in range(1, len(pa)):
        pa[i] = (pa[i-1] * a_val) % MOD
        pb[i] = (pb[i-1] * b_val) % MOD

    C = [{} for _ in range(max_k + 1)]
    for k in range(max_k + 1):
        words = generate_dyck(k)
        for s in words:
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            w = pa[alice_of(s)] * pb[bobw] % MOD
            C[k][kw] = (C[k].get(kw, 0) + w) % MOD
    return C


def solve(N, a, b):
    a_val = a % MOD
    b_val = b % MOD

    MAX_K = min(N - 1, 14)
    C = compute_C(MAX_K, a_val, b_val)

    pa = [1] * (N * N + 10)
    pb = [1] * (N * N + 10)
    for i in range(1, len(pa)):
        pa[i] = (pa[i-1] * a_val) % MOD
        pb[i] = (pb[i-1] * b_val) % MOD

    D = [{} for _ in range(N + 2)]
    for k in range(min(N, MAX_K + 1)):
        m = k + 1
        for kw, val in C[k].items():
            D[m][kw] = val * pa[2*m - 1] % MOD

    F = [0] * (N + 1)
    F[0] = 1

    for n in range(1, N + 1):
        total = 0
        for m in range(1, n + 1):
            if m >= len(D):
                continue
            for kw, d_val in D[m].items():
                r = pa[m] * pb[kw] % MOD
                factor = pow(r, n - m, MOD)
                total = (total + d_val * factor % MOD * F[n - m]) % MOD
        F[n] = total

    return [str(F[i]) for i in range(1, N + 1)]


if __name__ == '__main__':
    if len(sys.argv) >= 4:
        N, a_val, b_val = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        result = solve(N, a_val, b_val)
        print(' '.join(result))
    else:
        for N in [3, 4, 5, 10, 14]:
            r = solve(N, 2, 3)
            print(f"N={N}: {' '.join(r)}")
