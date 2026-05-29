"""
NTT-accelerated L-sequence DP (Direction 1k-B).

For fixed xp, the inner sum over d is:
  V[u] = a^u * Sum_{m=0}^{xp-2} W[m] * binom(m+u, m)_a   (u=0..N-xp)
  where W[m] = r^{m+2} * (dp[xp-m-2][0..xp] sum)

Using GF: Sum_{u>=0} binom(m+u, m)_a * z^u = 1/Prod_{i=0}^{m} (1 - a^i z)

T(z) = Sum_m W[m] / Prod_{i=0}^{m} (1 - a^i z) = N(z) / Prod_{i=0}^{xp-2} (1 - a^i z)

N(z) computed incrementally: N_0=W[0], N_{m+1}=N_m*(1-a^{m+1}*z)+W[m+1]

Then: V[u] = a^u * (N * H[xp-2])[u]  (standard convolution via NTT)

Overall: O(N^2 log N).
"""
import sys

MOD = 998244353
PRIMITIVE_ROOT = 3


def ntt(a, invert=False):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        wlen = pow(PRIMITIVE_ROOT, (MOD - 1) // length, MOD)
        if invert:
            wlen = pow(wlen, MOD - 2, MOD)
        for i in range(0, n, length):
            w = 1
            half = length // 2
            for j in range(half):
                u = a[i + j]
                v = a[i + j + half] * w % MOD
                a[i + j] = (u + v) % MOD
                a[i + j + half] = (u - v) % MOD
                w = w * wlen % MOD
        length <<= 1
    if invert:
        inv_n = pow(n, MOD - 2, MOD)
        for i in range(n):
            a[i] = a[i] * inv_n % MOD


def multiply_poly(a, b):
    need = len(a) + len(b) - 1
    n = 1
    while n < need:
        n <<= 1
    fa = a + [0] * (n - len(a))
    fb = b + [0] * (n - len(b))
    ntt(fa, False)
    ntt(fb, False)
    for i in range(n):
        fa[i] = fa[i] * fb[i] % MOD
    ntt(fa, True)
    return fa[:need]


def precompute(N, a_val):
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
    return H, pow_a


def compute_N_poly_incremental(W, xp2, pow_a):
    N_poly = [W[0]]
    for m in range(xp2):
        poly_m = [1, (-pow_a[m + 1]) % MOD]
        N_poly = multiply_poly(N_poly, poly_m)
        while len(N_poly) <= m + 1:
            N_poly.append(0)
        N_poly[0] = (N_poly[0] + W[m + 1]) % MOD
    return N_poly


def solve_ntt(N, a_val, b_val):
    H, pow_a = precompute(N, a_val)
    pow_b = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    dp = [[0] * (N + 1) for _ in range(N + 1)]
    dp[0][0] = 1

    pref = [[0] * (N + 2) for _ in range(N + 1)]
    for i in range(N + 1):
        pref[0][i] = 1

    for xp in range(1, N + 1):
        d1_bob = 1 if xp == 1 else pow_b[N - xp + 1]
        d1_S = (pref[xp - 1][xp] - (pref[xp - 1][xp - 2] if xp >= 2 else 0)) % MOD
        dp[xp][xp] = (dp[xp][xp] + d1_S * d1_bob % MOD * pow_a[xp]) % MOD

        xp2 = xp - 2
        if xp2 < 0:
            for i in range(xp, N + 1):
                pref[xp][i] = (pref[xp][i - 1] + dp[xp][i]) % MOD
            continue

        r = b_val * pow_a[xp] % MOD

        if xp2 >= 1:
            K_hi = pow_b[N - xp] * pow_a[xp] % MOD * pow_a[xp] % MOD * b_val % MOD * b_val % MOD
            W = [0] * xp2
            r_pow = 1
            for m in range(xp2):
                d_m = m + 2
                source = xp - d_m
                s_val = pref[source][xp]
                W[m] = K_hi * r_pow % MOD * s_val % MOD
                r_pow = r_pow * r % MOD

            N_poly = compute_N_poly_incremental(W, xp2 - 1, pow_a)
            h_row = H[xp2 - 1][:N - xp + 1]
            conv = multiply_poly(N_poly, h_row)
            for u in range(N - xp + 1):
                if u < len(conv):
                    dp[xp][xp + u] = (dp[xp][xp + u] + pow_a[u] * conv[u]) % MOD

        s0 = pref[0][xp]
        if s0:
            term = pow(pow_a[xp], xp, MOD) * s0 % MOD
            a_pow_u = 1
            for u in range(N - xp + 1):
                dp[xp][xp + u] = (dp[xp][xp + u] + term * a_pow_u % MOD * H[xp2][u]) % MOD
                a_pow_u = a_pow_u * a_val % MOD

        for i in range(xp, N + 1):
            pref[xp][i] = (pref[xp][i - 1] + dp[xp][i]) % MOD

    return dp[N][N]


def verify(N=8):
    from verify_bf import solve_brute
    print(f"=== Verifying NTT DP (N={N}) ===\n")
    for a_val, b_val in [(2, 3), (5, 7), (1, 1), (3, 2)]:
        bf = solve_brute(N, a_val, b_val)
        ntt_r = solve_ntt(N, a_val, b_val)
        ok = bf[N - 1] == ntt_r
        print(f"  a={a_val}, b={b_val}: bf={bf[N-1]} ntt={ntt_r} {'OK' if ok else 'FAIL'}")


def benchmark(n, a_val, b_val):
    import time
    print(f"\n=== Benchmark: N={n}, a={a_val}, b={b_val} ===")
    t0 = time.time()
    result = solve_ntt(n, a_val, b_val)
    t1 = time.time()
    print(f"  Result: {result}")
    print(f"  Time: {t1 - t0:.3f}s")


if __name__ == '__main__':
    verify(6)
    verify(8)
    benchmark(50, 2, 3)
    benchmark(100, 2, 3)
