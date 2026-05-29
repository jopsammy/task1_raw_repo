"""Debug the verified y-eliminated DP for N=2."""
from route_l_dp_v3 import solve_all_y_eliminated, precompute_all

MOD = 998244353
N = 2
a_val = 2
b_val = 3

ref = solve_all_y_eliminated(N, a_val, b_val)
print(f"Verified F: {ref}")

H, G, pow_a = precompute_all(N, a_val)
pow_b = [1]
for i in range(1, N + 1):
    pow_b.append(pow_b[-1] * b_val % MOD)

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
    print(f"\n  x={x}: pref={pref[0:N+2]}, bob_base={bob_factor_base}")

    for xp in range(x + 1, N + 1):
        d = xp - x
        S = (pref[xp] - (pref[x - 1] if x > 0 else 0)) % MOD
        if S == 0:
            continue

        const = S * bob_factor_base % MOD
        print(f"    xp={xp}, d={d}, S={S}, const={const}")

        if d == 1:
            contrib = const * pow_a[xp] % MOD
            dp[xp][xp] = (dp[xp][xp] + contrib) % MOD
            print(f"    d=1: contrib={contrib}, dp[{xp}][{xp}]={dp[xp][xp]}")
        else:
            base_alice = pow_a_pow[d][xp]
            factor = const * base_alice % MOD
            g_row = G[d]
            for yp in range(xp, N + 1):
                u = yp - xp
                val = factor * g_row[u] % MOD
                dp[xp][yp] = (dp[xp][yp] + val) % MOD
                print(f"    d=2 yp={yp}: val={val}, dp[{xp}][{yp}]={dp[xp][yp]}")

print(f"\nFinal dp[{N}][{N}] = {dp[N][N]}")
