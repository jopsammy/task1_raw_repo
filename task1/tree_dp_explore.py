# CORRECT tree DP with brute-force wrapping precomputation
# Validates theory for n≤8, identifies wrapping formulas
import sys; sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob
MOD = 998244353
a, b = 2, 3

pa = [1]; pb = [1]; pib = [1]
inv_b = pow(b, MOD-2, MOD)
for i in range(500):
    pa.append(pa[-1]*a%MOD)
    pb.append(pb[-1]*b%MOD)
    pib.append(pib[-1]*inv_b%MOD)

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

N = 7

# Brute-force all parameters for each Dyck word
# For each word of size n: (alice, bob, k, x1, X, bobt, kt, Xt)
# where bobt, kt, Xt = pair_seq(X[1:]) (tail pair_seq)
# and bobw, kw, Xw = pair_seq([1]+X) (wrapping)
# and bob_R, k_R, X_R = pair_seq(X) (full pair_seq)

data = {}
for n in range(1, N+1):
    data[n] = []
    for s in generate_dyck(n):
        al = alice_of(s)
        X, bob = x_seq_and_bob(s)
        k = len(X)
        x1 = X[0]
        
        tail = X[1:] if n>1 else []
        Xt = pair_seq(tail)
        kt = len(Xt)
        bobt = sum(j*Xw for j, Xw in enumerate(Xt))
        
        X_R = pair_seq(X)
        k_R = len(X_R)
        bob_R = sum(j*Xw for j, Xw in enumerate(X_R))
        
        Xw = pair_seq([1]+X)
        kw = len(Xw)
        bobw = sum(j*Xw for j, Xw in enumerate(Xw))
        
        data[n].append((s, al, bob, k, x1, list(X), bobt, kt, list(Xt), bobw, kw, list(Xw), bob_R, k_R, list(X_R)))

# Verify wrapping formula per word
print("=== Per-word wrapping verification ===")
all_ok = True
for n in range(2, N+1):
    for (s, al, bob, k, x1, X, bobt, kt, Xt, bobw, kw, Xw, bob_R, k_R, X_R) in data[n]:
        al_w = al + 2*n + 1  # alice((A)) = alice(A) + 2|A| + 1
        
        # Pair_seq decomposition: X((A)) = pair_seq([1]++X(A))
        # bob((A)) = bobw, k((A)) = kw
        # Verify: alice((A)) = alice(A) + 2n - 1
        wrap_s = '(' + s + ')'
        al_w_actual = alice_of(wrap_s)
        X_w_actual, bob_w_actual = x_seq_and_bob(wrap_s)
        
        if al_w != al_w_actual or bobw != bob_w_actual or kw != len(X_w_actual) or list(Xw) != list(X_w_actual):
            print(f"  FAIL: {s} wrapping mismatch")
            all_ok = False

if all_ok:
    print("  All wrapping per-word formulas verified! ✓")

# Now compute G[n][0] using tree DP with brute-force wrapping
# Tree = root + [T1,...,Tm] (ordered forest)
# Dyck(T) = (T1) (T2) ... (Tm)
# For each wrapped subtree, we have (al_w, bobw, kw)

# Precompute wrapped contributions for all words
wrap_contrib = {}
for n in range(N):
    wrap_contrib[n] = []  # list of (al_w, bobw, kw) for each tree of size n
for n in range(N):
    if n == 0:
        wrap_contrib[0].append((alice_of('()'), 0, 1))  # wrapping of empty = "()"
    else:
        for (s, al, bob, k, x1, X, bobt, kt, Xt, bobw, kw, Xw, bob_R, k_R, X_R) in data[n]:
            al_w = al + 2*n + 1  # alice((A)) = alice(A) + 2|A| + 1
            wrap_contrib[n].append((al_w, bobw, kw))

# DP: G[n][0] using concat of wrapped children
# G[0] = 1 (empty)
# G[n] = Σ_{m=0}^{n-1} Σ_{P ∈ wrap_contrib[m]} P_contrib * G[n-1-m] * a^{(m+1)*(n-1-m)} * b^{kw*(n-1-m)}

G_dp = [0]*(N+1)
G_dp[0] = 1

for n in range(1, N+1):
    total = 0
    for m in range(n):
        P_size = m + 1  # size of wrapped child = original size + 1
        rest = n - 1 - m
        if rest < 0: continue
        for al_w, bobw, kw in wrap_contrib[m]:
            # Primitive P = (T), size = P_size, contribution to n-word:
            # alice = al_w + alice(rest) + P_size * rest
            # bob = bobw + bob(rest) + kw * rest
            # k = kw + k(rest)
            # b^{bob+k*L} at L=0 → b^{bob}
            # contribution = a^{al_w} * b^{bobw} * G[rest] * a^{P_size*rest} * b^{kw*rest}
            contrib = pa[al_w] * pb[bobw] % MOD * G_dp[rest] % MOD * pa[P_size*rest] % MOD * pb[kw*rest] % MOD
            total = (total + contrib) % MOD
    G_dp[n] = total

print("\n=== Tree DP results ===")
G_bf = []
for n in range(1, N+1):
    total = 0
    for s in generate_dyck(n):
        al = alice_of(s)
        X, bob = x_seq_and_bob(s)
        total = (total + pa[al]*pb[bob]) % MOD
    G_bf.append(total)

for n in range(1, N+1):
    ok = "OK" if G_dp[n] == G_bf[n-1] else "MISMATCH"
    print(f"  n={n}: DP={G_dp[n]:10d} BF={G_bf[n-1]:10d} {ok}")

# Now analyze wrapping formula patterns
print("\n=== Wrapping formula analysis ===")
# For each tree T of size m:
# X(T) = [x1, x2, ..., xk]
# Wrapping: X((T)) = pair_seq([1, x1, x2, ..., xk])
# 
# Key decomposition: if x1=1: [1,1,...] → outer 1 eats x1
#                   if x1≥2: [1,x1,...] → outer 1 + x1 → 1+x1
# 
# After first step, tail pair_seq(X[1:]) is applied
# For x1≥2: k_w = 1 + kt, bob_w = bobt + (m - x1)
# For x1=1: k_w = 1 + k_R(m-1), bob_w = bob_R(m-1) + (m-1)

print("Verify: for x1≥2, kw=1+kt, bobw=bobt+(m-x1)")
for m in range(2, N):
    for (s, al, bob, k, x1, X, bobt, kt, Xt, bobw, kw, Xw, bob_R, k_R, X_R) in data[m]:
        if x1 >= 2:
            kw_formula = 1 + kt
            bobw_formula = bobt + (m - x1)
            if kw != kw_formula or bobw != bobw_formula:
                print(f"  FAIL: {s} x1={x1} kw={kw}!={kw_formula} bobw={bobw}!={bobw_formula}")
print("  (no output = all pass)")

print("Verify: for x1=1, kw=1+k_R(m-1), bobw=bob_R(m-1)+(m-1)")
# For x1=1: A = "()" + Q where Q has size m-1
# Vx[m][1][L] = a^{m-1} * R[m-1][L]  (from earlier analysis)
# kw = 1 + k_R(Q), bobw = bob_R(Q) + (m-1)
all_ok = True
for m in range(2, min(N, 6)):
    for (s, al, bob, k, x1, X, bobt, kt, Xt, bobw, kw, Xw, bob_R, k_R, X_R) in data[m]:
        if x1 == 1:
            # Q has size m-1. Need to find Q's R values.
            # We can compute directly: Q = s without the first "()"...
            # But the first x_step of 1 means first pair is "()"
            # Q starts at position 2 in the Dyck word
            q_dyck = s[2:]  # after the first "()"
            if q_dyck:
                X_Q, bob_Q = x_seq_and_bob(q_dyck)
                al_Q = alice_of(q_dyck)
                X_R_Q = pair_seq(X_Q)
                k_R_Q = len(X_R_Q)
                bob_R_Q = sum(j*Xw for j, Xw in enumerate(X_R_Q))
                
                kw_expected = 1 + k_R_Q
                bobw_expected = bob_R_Q + (m - 1)
                
                if kw != kw_expected or bobw != bobw_expected:
                    print(f"  FAIL: {s} kw={kw}!={kw_expected} bobw={bobw}!={bobw_expected}")
                    all_ok = False
            else:
                if kw != 1 or bobw != 0:
                    print(f"  FAIL: {s} (empty Q) kw={kw} bobw={bobw}")
                    all_ok = False
if all_ok:
    print("  All verified! ✓")
