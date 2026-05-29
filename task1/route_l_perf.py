"""
Route L DP - Optimized for performance testing.
Computes F[n] = sum a^{alice} b^{bob} over all Dyck words of length 2n.
"""
import sys, time

MOD = 998244353


def solve_l(N, a_val, b_val):
    """Compute F[N] using Route L DP. Complexity: O(N^4) per N."""
    pow_a = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_a[i] = (pow_a[i - 1] * a_val) % MOD

    pow_b = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    H = [[1] * (N + 1) for _ in range(N + 1)]
    for d in range(1, N + 1):
        for u in range(N + 1):
            if u == 0:
                H[d][0] = 1
            else:
                H[d][u] = (H[d][u - 1] + pow_a[u] * H[d - 1][u]) % MOD

    dp = [[0] * (N + 1) for _ in range(N + 1)]
    dp[0][0] = 1

    for x in range(N):
        for y in range(x, N + 1):
            cur = dp[x][y]
            if cur == 0:
                continue

            bob = 1 if x == 0 else pow_b[N - x]
            cur_bob = cur * bob % MOD

            x_min = max(y, x + 1)
            for xp in range(x_min, N + 1):
                d = xp - x

                if d == 1:
                    yp = xp
                    dp[xp][yp] = (dp[xp][yp] + cur_bob * pow_a[xp]) % MOD
                else:
                    base = pow(pow_a[xp], d - 1, MOD)
                    for yp in range(xp, N + 1):
                        alice = base * pow_a[yp] % MOD * H[d - 2][yp - xp] % MOD
                        dp[xp][yp] = (dp[xp][yp] + cur_bob * alice) % MOD

    return dp[N][N]


def solve_l_all(N, a_val, b_val):
    """Compute F[1..N] using Route L DP (computes each n independently)."""
    results = []
    for n in range(1, N + 1):
        results.append(solve_l(n, a_val, b_val))
    return results


def solve_l_optimized(N, a_val, b_val):
    """
    Optimized version: use running prefix sums to reduce inner loop cost.
    
    Key optimization: for a fixed source x, instead of iterating yp for each xp,
    we precompute the contribution using H[d-2][yp-xp].
    
    Actually, let me try a different optimization: use the fact that
    dp[x'][y'] = a^{y'} * sum_{d} C[x'][d] * H[d-2][y'-x']
    
    Where C[x'][d] = b^{n-(x'-d)} * pref[x'-d][x'] * a^{(d-1)x'}.
    
    We can compute pref[x][max_y] = sum_{y=0}^{max_y} dp[x][y] incrementally.
    Then for each x', compute V[delta] = sum_d C[x'][d] * H[d-2][delta].
    """
    pow_a = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_a[i] = (pow_a[i - 1] * a_val) % MOD

    pow_b = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    H = [[1] * (N + 1) for _ in range(N + 1)]
    for d in range(1, N + 1):
        for u in range(N + 1):
            if u == 0:
                H[d][0] = 1
            else:
                H[d][u] = (H[d][u - 1] + pow_a[u] * H[d - 1][u]) % MOD

    dp = [[0] * (N + 1) for _ in range(N + 1)]
    dp[0][0] = 1
    pref = [[0] * (N + 1) for _ in range(N + 1)]
    for y in range(N + 1):
        pref[0][y] = 1

    for xp in range(1, N + 1):
        for yp in range(xp, N + 1):
            total = 0
            x_min = 1
            for x in range(x_min, xp):
                d = xp - x
                if yp > xp:
                    max_y = min(xp, N)
                else:
                    max_y = xp

                bob = 1 if x == 0 else pow_b[N - x]
                a_factor = pow_a[yp]
                if d >= 2:
                    a_factor = a_factor * pow(pow_a[xp], d - 1, MOD) % MOD
                    a_factor = a_factor * H[d - 2][yp - xp] % MOD

                total = (total + bob * a_factor % MOD * pref[x][xp]) % MOD

            dp[xp][yp] = total

        for yp in range(xp, N + 1):
            pref[xp][yp] = (pref[xp][yp - 1] + dp[xp][yp]) % MOD if yp > xp else dp[xp][xp]

    return dp[N][N]


if __name__ == '__main__':
    for N in range(1, 11):
        t0 = time.time()
        result = solve_l(N, 2, 3)
        t1 = time.time()
        print(f"N={N}: F={result}, time={t1-t0:.4f}s")
