"""
Route D: Lagrange Inversion Implementation
===========================================
Key GF equation (verified):
F(x,y) = 1 + Σ_A [a^{alice(A)+2|A|+1} * b^{bob((A))} * x^{|A|+1} * y^{k((A))}]
              * F(a^{|A|+1} * b^{k((A))} * x, y)

For a fixed n, extracting the coefficient:
F[n](y) = Σ_{m=1..n} Σ_{A:|A|=m-1} a^{alice(A)+2m-1} b^{bob((A))}
           * a^{m(n-m)} b^{k((A))(n-m)} * F[n-m](y) * y^{k((A))}

The answer F_n = F[n](1) (evaluated at y=1).

Strategy: precompute wrapping statistics for all sizes k:
  W[k] = list of (bob_w, k_w, alice_sum_coeff) for size k
  
Then DP: F[0] = 1
  For n in 1..N:
    F[n] = 0
    For m in 1..n:
      For each (bw, kw, coeff_sum) in W[m-1]:
        idx = n - m
        cross_a = m * idx
        cross_b = kw * idx
        F[n] += a^{2m-1+cross_a} * b^{bw+cross_b} * coeff_sum * F[idx]
"""

import sys
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353

def precompute_wrapping_stats(max_k, a_val, b_val):
    """
    For each size k, compute wrapping statistics:
    For each word A of size k, wrapping (A) gives (bob_w, k_w).
    We group by (bob_w, k_w) and sum a^{alice(A)}.
    
    Returns:
        W_stats[k] = {(bw, kw): sum_a_alice}
    """
    max_exp = max_k * max_k + 5
    pa = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i-1] * a_val % MOD

    W_stats = [{} for _ in range(max_k + 1)]
    
    for k in range(max_k + 1):
        words = generate_dyck(k)
        stats = {}
        for s in words:
            alice_v = alice_of(s)
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            key = (bobw, kw)
            val = pa[alice_v]
            stats[key] = (stats.get(key, 0) + val) % MOD
        W_stats[k] = stats
    
    return W_stats

def solve_dp_bruteforce_wrapping(N, a_val, b_val):
    """DP solution using brute-force precomputed wrapping stats (for verification)."""
    a_val %= MOD
    b_val %= MOD
    
    W_stats = precompute_wrapping_stats(N - 1, a_val, b_val)
    
    max_exp = N * N + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i-1] * a_val % MOD
        pb[i] = pb[i-1] * b_val % MOD
    
    F = [0] * (N + 1)
    F[0] = 1
    
    for n in range(1, N + 1):
        total = 0
        for m in range(1, n + 1):
            k = m - 1
            idx = n - m
            for (bw, kw), coeff in W_stats[k].items():
                term = pa[2*m - 1 + m*idx]
                term = term * pb[bw + kw*idx] % MOD
                term = term * coeff % MOD
                term = term * F[idx] % MOD
                total = (total + term) % MOD
        F[n] = total
    
    return [str(F[i]) for i in range(1, N + 1)]

def compute_wrapping_orbits(max_k):
    """
    Analyze the structure of wrapping orbits.
    Returns orbit statistics for each k.
    """
    orbits = {}
    for k in range(1, max_k + 1):
        words = generate_dyck(k)
        dist = {}
        for s in words:
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            key = (bobw, kw)
            dist[key] = dist.get(key, 0) + 1
        
        orbit_sizes = sorted(dist.values(), reverse=True)
        unique_keys = len(dist)
        catalan = len(words)
        orbits[k] = {
            'catalan': catalan,
            'unique_keys': unique_keys,
            'max_orbit_size': orbit_sizes[0] if orbit_sizes else 0,
            'distribution': dist
        }
        
        print(f"k={k}: Catalan={catalan}, unique (bw,kw)={unique_keys}, "
              f"compression={catalan/unique_keys:.1f}:1, "
              f"max_orbit={orbit_sizes[0]}")
    
    return orbits

def cross_validate_with_solution(N, a_val, b_val):
    """Cross-validate the DP solution against the existing solution.py."""
    import solution
    dp_result = solve_dp_bruteforce_wrapping(N, a_val, b_val)
    ref_result = solution.solve(N, a_val, b_val)
    
    match = all(d == r for d, r in zip(dp_result, ref_result))
    print(f"Cross-validation (N={N}, a={a_val}, b={b_val}): {'PASS' if match else 'FAIL'}")
    if not match:
        for i, (d, r) in enumerate(zip(dp_result, ref_result)):
            if d != r:
                print(f"  n={i+1}: dp={d}, ref={r}")
    return match

if __name__ == '__main__':
    print("=== Route D: Lagrange Inversion Prototype ===\n")
    
    print("--- Wrapping orbit analysis ---")
    orbits = compute_wrapping_orbits(10)
    
    print("\n--- Cross-validation ---")
    for N in [4, 5, 6, 7, 8]:
        cross_validate_with_solution(N, 2, 3)
    
    print("\n--- Coefficient analysis (a=2,b=3) ---")
    max_exp = 10 * 10 + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i-1] * 2 % MOD
        pb[i] = pb[i-1] * 3 % MOD
    
    F_coeffs = {}
    for n in range(1, 7):
        words = generate_dyck(n)
        for s in words:
            alice_v = alice_of(s)
            X, bob_v = x_seq_and_bob(s)
            k_val = len(X)
            coeff = pa[alice_v] * pb[bob_v] % MOD
            key = (n, k_val)
            F_coeffs[key] = (F_coeffs.get(key, 0) + coeff) % MOD
    
    print("\nF(x,y) structure:")
    print(f"{'n':>3} {'k':>3} {'coeff':>12} {'log_a(coeff/...)'}")
    for (n, k), v in sorted(F_coeffs.items()):
        print(f"{n:3d} {k:3d} {v:12d}")
