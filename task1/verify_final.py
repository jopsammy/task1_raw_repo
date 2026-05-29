from verify_bf import generate_dyck, alice_of, x_seq_and_bob
MOD = 998244353

def compute_L_seq(s):
    n = len(s) // 2
    L = [0] * n
    rc = 0
    for i, ch in enumerate(s):
        if ch == ')':
            L[rc] = (i + 1) - (rc + 1)
            rc += 1
    return L

def brute_via_L(N, a_val, b_val):
    res = []
    for n in range(1, N+1):
        words = generate_dyck(n)
        total = 0
        for s in words:
            L = compute_L_seq(s)
            alice = sum(L)
            jumps = [0]
            pos = 0
            while pos < n:
                pos = L[pos]
                jumps.append(pos)
            bob = sum(n - jumps[j] for j in range(1, len(jumps)-1))
            total = (total + pow(a_val, alice, MOD) * pow(b_val, bob, MOD)) % MOD
        res.append(total)
    return res

from solution import solve
for N in range(1, 15):
    r1 = brute_via_L(N, 2, 3)
    r2 = [int(x) for x in solve(N, 2, 3)]
    ok = all(a==b for a,b in zip(r1,r2))
    if not ok:
        for i,(a,b) in enumerate(zip(r1,r2)):
            if a!=b:
                print(f"N={N}: n={i+1} bf={a} sol={b}")
    else:
        print(f"N={N}: OK ({len(r1)} values)")
