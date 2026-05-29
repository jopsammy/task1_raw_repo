"""
Route L DP - O(N^3) with y-dimension eliminated via prefix sum.

Key insight: for fixed source x and target xp, all valid y in [x, xp]
have the same per-y contribution. So we sum over y first using prefix sums.

Transition (original):
  dp[xp][yp] += dp[x][y] * b^{n-x} * a^{(d-1)xp+yp} * H[d-2][yp-xp]

After y-elimination:
  Let S[x][xp] = sum_{y=x}^{xp} dp[x][y]
  dp[xp][xp]   += S[x][xp] * b^{n-x} * a^{xp}                                    (d=1)
  dp[xp][yp]   += S[x][xp] * b^{n-x} * a^{d·xp+u} * H[d-2][u]                     (d>=2)
  where u = yp - xp, d = xp - x

Complexity:
  - Outer: x from 0 to N-1
  - Inner: xp from x+1 to N
  - Deepest: yp from xp to N (for d>=2)
  - Total: O(N^3/2) ≈ 20.8B for N=5000
  
  With PyPy3 JIT, each iteration is ~5-8 CPU cycles, estimated ~100-150s
  for N=5000, which is ~5-8x over the 20s limit.
  
  Further optimization: precompute G_tables[d][u] = a^{u} * H[d-2][u].
"""
import sys
from verify_bf import solve_brute, generate_dyck

MOD = 998244353


def precompute_all(N, a_val):
    """Precompute pow_a, H[d][u], and G[d][u] = a^u * H[d-2][u]."""
    pow_a = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_a[i] = (pow_a[i - 1] * a_val) % MOD

    H = [[1] * (N + 1) for _ in range(N + 1)]
    for d in range(1, N + 1):
        for u in range(N + 1):
            if u == 0:
                H[d][0] = 1
            else:
                H[d][u] = (H[d][u - 1] + pow_a[u] * H[d - 1][u]) % MOD

    G = [[0] * (N + 1) for _ in range(N + 3)]
    for d in range(2, N + 3):
        for u in range(N + 1):
            G[d][u] = pow_a[u] * H[d - 2][u] % MOD

    return H, G, pow_a


def solve_y_eliminated(N, a_val, b_val):
    """
    O(N^3) DP with y-dimension eliminated.
    """
    H, G, pow_a = precompute_all(N, a_val)

    pow_b = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    pow_a_pow = [[1] * (N + 1) for _ in range(N + 1)]
    for d in range(1, N + 1):
        for xp in range(N + 1):
            pow_a_pow[d][xp] = pow(pow_a[xp], d, MOD)

    dp = [[0] * (N + 1) for _ in range(N + 1)]
    dp[0][0] = 1

    for x in range(N):
        pref = [0] * (N + 2)
        for i in range(x, N + 1):
            pref[i] = (pref[i - 1] + dp[x][i]) % MOD

        bob_factor_base = 1 if x == 0 else pow_b[N - x]

        for xp in range(x + 1, N + 1):
            d = xp - x
            S = (pref[xp] - (pref[x - 1] if x > 0 else 0)) % MOD
            if S == 0:
                continue

            const = S * bob_factor_base % MOD

            if d == 1:
                dp[xp][xp] = (dp[xp][xp] + const * pow_a[xp]) % MOD
            else:
                base_alice = pow_a_pow[d][xp]
                factor = const * base_alice % MOD

                row = dp[xp]
                g_row = G[d]
                for yp in range(xp, N + 1):
                    u = yp - xp
                    val = factor * g_row[u] % MOD
                    row[yp] = (row[yp] + val) % MOD

    return dp[N][N]


def solve_all_y_eliminated(N, a_val, b_val):
    H, G, pow_a = precompute_all(N, a_val)

    pow_b = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    pow_a_pow = [[1] * (N + 1) for _ in range(N + 1)]
    for d in range(1, N + 1):
        for xp in range(N + 1):
            pow_a_pow[d][xp] = pow(pow_a[xp], d, MOD)

    results = [0] * (N + 1)

    for n in range(1, N + 1):
        dp = [[0] * (n + 1) for _ in range(n + 1)]
        dp[0][0] = 1

        for x in range(n):
            pref = [0] * (n + 2)
            for i in range(x, n + 1):
                pref[i] = (pref[i - 1] + dp[x][i]) % MOD

            bob_factor_base = 1 if x == 0 else pow_b[n - x]

            for xp in range(x + 1, n + 1):
                d = xp - x
                S = (pref[xp] - (pref[x - 1] if x > 0 else 0)) % MOD
                if S == 0:
                    continue

                const = S * bob_factor_base % MOD

                if d == 1:
                    dp[xp][xp] = (dp[xp][xp] + const * pow_a[xp]) % MOD
                else:
                    base_alice = pow_a_pow[d][xp]
                    factor = const * base_alice % MOD

                    row = dp[xp]
                    g_row = G[d]
                    for yp in range(xp, n + 1):
                        u = yp - xp
                        row[yp] = (row[yp] + factor * g_row[u]) % MOD

        results[n] = dp[n][n] % MOD

    return results


def verify(N=8):
    print(f"=== Verifying y-eliminated DP vs brute force (N={N}) ===\n")

    for a_val, b_val in [(2, 3), (5, 7), (1, 1), (3, 2)]:
        bf = solve_brute(N, a_val, b_val)
        dp = solve_all_y_eliminated(N, a_val, b_val)

        ok = True
        for n in range(1, N + 1):
            if bf[n - 1] != dp[n]:
                print(f"  a={a_val}, b={b_val}, n={n}: FAIL (bf={bf[n-1]}, dp={dp[n]})")
                ok = False
        if ok:
            print(f"  a={a_val}, b={b_val}: ALL OK (n=1..{N})")

    return True


def benchmark(n, a_val, b_val):
    import time
    print(f"\n=== Benchmark: N={n}, a={a_val}, b={b_val} ===")
    t0 = time.time()
    result = solve_y_eliminated(n, a_val, b_val)
    t1 = time.time()
    print(f"  Result: {result}")
    print(f"  Time: {t1 - t0:.3f}s")


if __name__ == '__main__':
    verify(8)
    benchmark(100, 2, 3)
    benchmark(200, 2, 3)
    benchmark(500, 2, 3)
