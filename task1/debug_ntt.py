"""Debug NTT DP for N=2."""
import sys
sys.path.insert(0, '.')
from route_l_dp_v3 import solve_all_y_eliminated
from route_l_ntt import solve_ntt, precompute as ntt_precompute, compute_N_poly_incremental, multiply_poly

MOD = 998244353

N = 2
a_val = 2
b_val = 3

ref = solve_all_y_eliminated(N, a_val, b_val)
print(f"Ref (y-elim O(N^3)): F[1]={ref[1]}, F[2]={ref[2]}")
print(f"Expected from brute: verify_bf says... let me check")

from verify_bf import solve_brute
bf = solve_brute(N, a_val, b_val)
print(f"Brute force: F[1]={bf[0]}, F[2]={bf[1]}")

H, pow_a = ntt_precompute(N, a_val)
pow_b = [1, 3, 9]

print(f"\nH[0] = {H[0]}")
print(f"H[1] = {H[1]}")
print(f"pow_a = {pow_a}")

dp = [[0] * (N + 1) for _ in range(N + 1)]
dp[0][0] = 1
pref = [[0] * (N + 2) for _ in range(N + 1)]
for i in range(N + 1):
    pref[0][i] = 1

for xp in range(1, N + 1):
    print(f"\n--- xp={xp} ---")
    K_final = pow_b[N - xp]
    r = b_val * pow_a[xp] % MOD
    print(f"  K={K_final}, r={r}")

    d1_S = (pref[xp - 1][xp] - (pref[xp - 1][xp - 2] if xp >= 2 else 0)) % MOD
    d1_contrib = d1_S * pow_b[N - xp + 1] % MOD * pow_a[xp] % MOD
    dp[xp][xp] = (dp[xp][xp] + d1_contrib) % MOD
    print(f"  d1: S={d1_S}, contrib={d1_contrib}, dp[{xp}][{xp}]={dp[xp][xp]}")

    xp2 = xp - 2
    if xp2 < 0:
        for i in range(xp, N + 1):
            pref[xp][i] = (pref[xp][i - 1] + dp[xp][i]) % MOD
        print(f"  pref[{xp}] = {pref[xp]}")
        continue

    W = [0] * (xp2 + 1)
    r_pow_v = r * r % MOD
    for m in range(xp2 + 1):
        d = m + 2
        source = xp - d
        s_val = pref[source][xp]
        W[m] = r_pow_v * s_val % MOD
        print(f"  W[m={m}]: source={source}, S={s_val}, r^d={r_pow_v}, W={W[m]}")
        r_pow_v = r_pow_v * r % MOD

    N_poly = compute_N_poly_incremental(W, xp2, pow_a)
    print(f"  N_poly={N_poly}")

    h_row = H[xp2][:N - xp + 1]
    print(f"  h_row={h_row}")
    conv = multiply_poly(N_poly, h_row)
    print(f"  conv={conv}")

    dp_row = dp[xp]
    total_d2 = 0
    for u in range(N - xp + 1):
        if u < len(conv):
            val = K_final * pow_a[u] % MOD * conv[u] % MOD
            dp_row[xp + u] = (dp_row[xp + u] + val) % MOD
            print(f"  d2 u={u}: val={val}, dp[{xp}][{xp+u}]={dp_row[xp+u]}")
            total_d2 = (total_d2 + val) % MOD
    print(f"  d2 total={total_d2}")

    for i in range(xp, N + 1):
        pref[xp][i] = (pref[xp][i - 1] + dp[xp][i]) % MOD

print(f"\n=== Final: F[2] = {dp[N][N]} ===")
print(f"Expected: {bf[1]}")
