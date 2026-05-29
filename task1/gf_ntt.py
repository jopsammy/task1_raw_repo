"""
Compute C[k][kw] = Σ_{A:|A|=k, k((A))=kw} a^{alice(A)} b^{bob((A))}
for k=0..14. Check for recurrence patterns.

Then derive the generating function:
F(x) = 1 + Σ_{k≥0, kw} C[k][kw] · a^{2k+3} · x^{k+2} · F(a^{k+2} b^{kw} x)

Wait, let me re-index. For a primitive block of size m = k+2 (wrapping of size k+1 word):
  coeff = C[k][kw] · a^{2k+3}

Let me define D[m][kw] for m≥2 (m = k+2 where k≥0):
  D[m][kw] = C[m-2][kw] · a^{2m-1}

Then: F(x) = 1 + Σ_{m≥2, kw} D[m][kw] · x^m · F(a^m b^{kw} x)

Coefficient extraction:
F[n] = Σ_{m=2}^{n} Σ_{kw} D[m][kw] · (a^m b^{kw})^{n-m} · F[n-m]

Let's verify this matches the original recurrence.
"""
import time
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353

def compute_C_kw(max_k, a_val, b_val):
    """Compute C[k][kw] for k=0..max_k."""
    pow_a = [1] * (max_k * max_k + 10)
    pow_b = [1] * (max_k * max_k + 10)
    for i in range(1, len(pow_a)):
        pow_a[i] = (pow_a[i-1] * a_val) % MOD
        pow_b[i] = (pow_b[i-1] * b_val) % MOD

    C = [{} for _ in range(max_k + 1)]
    
    for k in range(max_k + 1):
        words = generate_dyck(k)
        for s in words:
            al = alice_of(s)
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            weight = pow_a[al] * pow_b[bobw] % MOD
            C[k][kw] = (C[k].get(kw, 0) + weight) % MOD
    
    return C


def compute_D(N, a_val, b_val, C):
    """D[m][kw] for m=2..N+1."""
    pow_a = [1] * (N * N + 10)
    for i in range(1, len(pow_a)):
        pow_a[i] = (pow_a[i-1] * a_val) % MOD
    
    D = [{} for _ in range(N + 2)]
    for k in range(N):
        m = k + 1
        if k >= len(C):
            continue
        for kw, val in C[k].items():
            D[m][kw] = val * pow_a[2*m - 1] % MOD
    
    return D


def solve_via_gf(N, a_val, b_val, D):
    """Compute F[1..N] using GF coefficient extraction."""
    pow_a = [1] * (N * N + 10)
    pow_b = [1] * (N * N + 10)
    for i in range(1, len(pow_a)):
        pow_a[i] = (pow_a[i-1] * a_val) % MOD
        pow_b[i] = (pow_b[i-1] * b_val) % MOD
    
    F = [0] * (N + 1)
    F[0] = 1
    
    for n in range(1, N + 1):
        total = 0
        for m in range(1, n + 1):
            k = m - 1
            if k < 0 or k >= len(D):
                continue
            for kw, d_val in D[m].items():
                r = pow_a[m] * pow_b[kw] % MOD
                factor = pow(r, n - m, MOD)
                total = (total + d_val * factor % MOD * F[n - m]) % MOD
        F[n] = total
    
    return F


def verify_gf(N, a_val, b_val, C):
    """Verify GF recurrence against brute force."""
    from verify_bf import solve_brute
    
    D = compute_D(N, a_val, b_val, C)
    bf = solve_brute(N, a_val, b_val)
    gf = solve_via_gf(N, a_val, b_val, D)
    
    print(f"Verifying GF for N={N}, a={a_val}, b={b_val}:")
    for n in range(1, N + 1):
        if bf[n-1] != gf[n]:
            print(f"  FAIL n={n}: bf={bf[n-1]} gf={gf[n]}")
            return False
    print(f"  ALL OK ({N} values)")
    return True


def analyze_C_structure(max_k, a_val, b_val):
    """Analyze C[k][kw] pattern."""
    C = compute_C_kw(max_k, a_val, b_val)
    
    print(f"\n{'k':>3s}  {'kw values':>20s}  {'sum C':>10s}  {'#kw':>4s}")
    print("-" * 50)
    for k in range(max_k + 1):
        items = sorted(C[k].items())
        kw_str = " ".join(f"{kw}:{val:5d}" for kw, val in items[:5])
        if len(items) > 5:
            kw_str += " ..."
        print(f"{k:3d}  {kw_str:40s}  {sum(C[k].values()):10d}  {len(C[k]):4d}")
    
    return C


if __name__ == '__main__':
    a_val, b_val = 2, 3
    max_k = 14
    
    t0 = time.time()
    C = analyze_C_structure(max_k, a_val, b_val)
    t1 = time.time()
    print(f"\nEnumeration time: {t1-t0:.2f}s")
    
    verify_gf(max_k, a_val, b_val, C)
    
    a2, b2 = 5, 7
    C2 = compute_C_kw(8, a2, b2)
    verify_gf(8, a2, b2, C2)
