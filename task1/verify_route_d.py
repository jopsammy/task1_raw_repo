"""
Verify Route D recurrence: F[n] = Σ_{m=1..n} a^{2m-1+m(n-m)} * H[m-1][n-m] * F[n-m]
where H[k][L] = Σ_{A:|A|=k} a^{alice(A)} * b^{bob((A)) + k((A))*L}

Strategy:
1. Compute H[k][L] by enumerating all Dyck words of size k for small k.
2. Verify the recurrence against brute-force.
3. Analyze orbit counts.
"""
from verify_bf import generate_dyck, alice_of, x_seq_and_bob
from route_l_dp_v2 import solve_route_l_all as route_l_all

MOD = 998244353


def compute_H_by_enumeration(max_k, a_val, b_val):
    """
    Compute H[k][L] for k=0..max_k, L=0..some_max by full enumeration.
    H[k][L] = Σ_{A:|A|=k} a^{alice(A)} * b^{bob((A)) + k((A))*L}
    """
    max_L = max_k
    pow_a = [1] * (max_k * max_k + 5)
    pow_b = [1] * (max_k * max_k + 10)
    for i in range(1, len(pow_a)):
        pow_a[i] = (pow_a[i - 1] * a_val) % MOD
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD
    
    H = [[0] * (max_L + 1) for _ in range(max_k + 1)]
    H[0][0] = 1
    for L in range(1, max_L + 1):
        H[0][L] = H[0][L - 1] * b_val % MOD
    
    for k in range(1, max_k + 1):
        words = generate_dyck(k)
        for L in range(max_L - k + 1):
            total = 0
            for s in words:
                alice = alice_of(s)
                ws = '(' + s + ')'
                Xw, bobw = x_seq_and_bob(ws)
                kw = len(Xw)
                weight = pow_a[alice] * pow_b[bobw + kw * L] % MOD
                total = (total + weight) % MOD
            H[k][L] = total
    
    return H


def compute_H_orbit_stats(max_k, a_val, b_val):
    """
    Compute orbit statistics: for each k, return {(bw, kw): sum a^{alice}}
    """
    pow_a = [1] * (max_k * max_k + 5)
    for i in range(1, len(pow_a)):
        pow_a[i] = (pow_a[i - 1] * a_val) % MOD
    
    orbit_stats = [{} for _ in range(max_k + 1)]
    for k in range(max_k + 1):
        words = generate_dyck(k)
        for s in words:
            alice = alice_of(s)
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            key = (bobw, kw)
            orbit_stats[k][key] = (orbit_stats[k].get(key, 0) + pow_a[alice]) % MOD
    
    return orbit_stats


def solve_via_orbit_recurrence(N, a_val, b_val, H):
    """Solve F[1..N] using the orbit recurrence."""
    pow_a = [1] * (N * N + 5)
    pow_b = [1] * (N * N + 5)
    for i in range(1, len(pow_a)):
        pow_a[i] = (pow_a[i - 1] * a_val) % MOD
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD
    
    F = [0] * (N + 1)
    F[0] = 1
    
    for n in range(1, N + 1):
        total = 0
        for m in range(1, n + 1):
            k = m - 1
            idx = n - m
            H_val = H[k][idx] if k <= len(H) - 1 and idx <= len(H[k]) - 1 else 0
            exp_a = 2 * m - 1 + m * idx
            term = pow_a[exp_a] * H_val % MOD * F[idx] % MOD
            total = (total + term) % MOD
        F[n] = total
    
    return [str(F[i]) for i in range(1, N + 1)]


if __name__ == '__main__':
    max_k = 8
    a_val, b_val = 2, 3
    
    print("=== Computing H by enumeration ===")
    H = compute_H_by_enumeration(max_k, a_val, b_val)
    
    print(f"H[0] = {H[0][:5]}")
    for k in range(1, min(5, max_k + 1)):
        print(f"H[{k}] = {H[k][:5]}")
    
    print("\n=== Orbit statistics ===")
    stats = compute_H_orbit_stats(max_k, a_val, b_val)
    for k in range(max_k + 1):
        print(f"k={k}: {len(stats[k])} orbits: {sorted(stats[k].items())[:5]}")
    
    print("\n=== Verifying Route D recurrence ===")
    N = min(max_k + 1, 8)
    
    print(f"Route L DP:")
    rl = route_l_all(N, a_val, b_val)
    print(f"  {rl}")
    
    print(f"Route D (orbit recurrence):")
    rd = solve_via_orbit_recurrence(N, a_val, b_val, H)
    print(f"  {rd}")
    
    match = all(int(rl[i]) == int(rd[i]) for i in range(N))
    print(f"Match: {match}")
