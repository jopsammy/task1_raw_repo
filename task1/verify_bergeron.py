"""
Verify the Garsia-Haglund-Bergeron recurrence for (q,t)-Catalan:

    H_{n,k}(q,t) = t^{n-k} * q^{binom(k,2)} * sum_{r=1}^{n-k} binom(r+k-1, r)_q * H_{n-k,r}(q,t)
    H_{n,n}(q,t) = q^{binom(n,2)}
    
    C_n(q,t) = t^{-n} * H_{n+1,1}(q,t)
    
    F[n] = a^{n(n+1)/2} * C_n(a,b)
"""
import sys

MOD = 998244353


def generate_dyck(n):
    words = []
    def bt(s, op, cl):
        if cl > op or op > n:
            return
        if len(s) == 2 * n:
            if op == n and cl == n:
                words.append(s)
            return
        bt(s + '(', op + 1, cl)
        bt(s + ')', op, cl + 1)
    bt('', 0, 0)
    return words


def alice_of(s):
    n = len(s) // 2
    cnt = 0
    for i in range(2 * n):
        if s[i] == '(':
            for j in range(i + 1, 2 * n):
                if s[j] == ')':
                    cnt += 1
    return cnt


def x_seq_and_bob(s):
    n = len(s) // 2
    h = [0] * (2 * n + 1)
    for i in range(2 * n):
        h[i + 1] = h[i] + (1 if s[i] == '(' else -1)
    l = 0
    X = []
    while l < n:
        pos = 2 * l
        best_x = 0
        t = 1
        while pos + t <= 2 * n:
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
        l += best_x
    bob = sum(j * X[j] for j in range(len(X)))
    return X, bob


def brute_force_Fn(N, a_val, b_val):
    results = []
    for n in range(1, N + 1):
        words = generate_dyck(n)
        total = 0
        for s in words:
            alice = alice_of(s)
            X, bob = x_seq_and_bob(s)
            total = (total + pow(a_val, alice, MOD) * pow(b_val, bob, MOD)) % MOD
        results.append(total)
    return results


def precompute_qbinom(N, q):
    """Precompute q-binomial binom(n,k)_q for n,k<=N.
    Using recurrence: binom(n,k)_q = binom(n-1,k-1)_q + q^k * binom(n-1,k)_q
    """
    qb = [[0] * (N + 1) for _ in range(N + 1)]
    for i in range(N + 1):
        qb[i][0] = qb[i][i] = 1
    for n in range(2, N + 1):
        for k in range(1, n):
            qb[n][k] = (qb[n-1][k-1] + pow(q, k, MOD) * qb[n-1][k]) % MOD
    return qb


def compute_Cn_bergeron(N, a_val, b_val):
    """
    Compute C_n(a,b) using Bergeron formula.
    H_{n,k} for n=1..N+1, k=1..n.
    """
    qb = precompute_qbinom(N + 1, a_val)

    # Precompute q^{binom(k,2)}
    powbinom = [1] * (N + 3)
    for k in range(1, N + 3):
        powbinom[k] = pow(a_val, k * (k - 1) // 2, MOD)

    # Precompute b^d
    powb = [1] * (N + 3)
    for d in range(1, N + 3):
        powb[d] = powb[d - 1] * b_val % MOD

    H = [[0] * (N + 3) for _ in range(N + 4)]

    for n in range(1, N + 2):
        H[n][n] = powbinom[n]
        for k in range(1, n):
            d = n - k
            total = 0
            for r in range(1, d + 1):
                term = qb[r + k - 1][r] * H[d][r] % MOD
                total = (total + term) % MOD
            H[n][k] = powb[d] * powbinom[k] % MOD * total % MOD

    # C_n(q,t) = t^{-n} * H_{n+1,1}(q,t)
    import math
    inv_b = pow(b_val, MOD - 2, MOD)
    
    Cn = [0] * (N + 1)
    for n in range(1, N + 1):
        inv_bn = pow(inv_b, n, MOD)
        Cn[n] = inv_bn * H[n + 1][1] % MOD

    return Cn[1:]


def compute_Fn_from_bergeron(N, a_val, b_val):
    """F[n] = a^{n(n+1)/2} * C_n(a,b)"""
    Cn = compute_Cn_bergeron(N, a_val, b_val)
    Fn = []
    for n, c in enumerate(Cn, 1):
        baseline = pow(a_val, n * (n + 1) // 2, MOD)
        Fn.append(baseline * c % MOD)
    return Fn


def verify(max_n=8):
    print(f"=== Verifying Bergeron recurrence for n <= {max_n} ===\n")

    for a_val, b_val in [(2, 3), (5, 7), (1, 1), (3, 2)]:
        bf = brute_force_Fn(max_n, a_val, b_val)
        berg = compute_Fn_from_bergeron(max_n, a_val, b_val)

        ok = True
        for n in range(max_n):
            if bf[n] != berg[n]:
                print(f"  a={a_val}, b={b_val}, n={n+1}: FAIL (bf={bf[n]}, bergeron={berg[n]})")
                ok = False
        if ok:
            print(f"  a={a_val}, b={b_val}: ALL OK (n=1..{max_n})")


def benchmark(N, a_val, b_val):
    import time
    print(f"\n=== Benchmark N={N}, a={a_val}, b={b_val} ===")
    t0 = time.time()
    Cn = compute_Cn_bergeron(N, a_val, b_val)
    t1 = time.time()
    print(f"  Time: {t1 - t0:.3f}s")
    print(f"  C_{N} = {Cn[N-1]}")


if __name__ == '__main__':
    verify(8)
    benchmark(100, 2, 3)
    benchmark(200, 2, 3)
    benchmark(500, 2, 3)
    print("\n=== Comparison with route_l_dp_v3 at N=500 ===")
    print("route_l_dp_v3 N=500: 3.49s")