import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob
from collections import defaultdict

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

N = 8

print("="*70)
print("CRITICAL CHECK: For x1=1 trees, does (bob, k, n) determine (bobw, kw)?")
print("="*70)

all_trees = []
for n in range(1, N+1):
    for s in generate_dyck(n):
        X, bob = x_seq_and_bob(s)
        k = len(X)
        x1 = X[0]
        Xw = pair_seq([1] + X)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        all_trees.append({'s': s, 'n': n, 'bob': bob, 'k': k, 'x1': x1, 'bobw': bobw, 'kw': kw, 'X': X})

x1_eq_1 = [t for t in all_trees if t['x1'] == 1]

by_bob_k_n = defaultdict(list)
for t in x1_eq_1:
    by_bob_k_n[(t['bob'], t['k'], t['n'])].append(t)

collisions = 0
for key, trees in by_bob_k_n.items():
    bobw_set = set(t['bobw'] for t in trees)
    kw_set = set(t['kw'] for t in trees)
    if len(bobw_set) > 1 or len(kw_set) > 1:
        collisions += 1
        print(f"\nCOLLISION: (bob={key[0]}, k={key[1]}, n={key[2]})")
        print(f"  bobw values: {bobw_set}, kw values: {kw_set}")
        for t in trees:
            print(f"  {t['s']:25s} bobw={t['bobw']} kw={t['kw']} X={t['X']} Xw={pair_seq([1]+t['X'])}")

print(f"\nTotal x1=1 trees: {len(x1_eq_1)}")
print(f"Distinct (bob,k,n) tuples: {len(by_bob_k_n)}")
print(f"Collisions: {collisions}")

if collisions == 0:
    print("\n★★★ (bob, k, n) UNIQUELY determines (bobw, kw) for x1=1! ★★★")

print()
print("="*70)
print("CHECK 2: For x1>=2 trees, (bob, k) determines wrapping trivially")
print("bobw = bob, kw = k (verified for all n)")
print("="*70)

x1_ge2 = [t for t in all_trees if t['x1'] >= 2]
all_ok = all(t['bobw'] == t['bob'] and t['kw'] == t['k'] for t in x1_ge2)
print(f"  x1>=2 count: {len(x1_ge2)}, all correct: {all_ok}")

print()
print("="*70)
print("CHECK 3: Full classification — for each tree, wrapping = f(bob,k,n,x1)")
print("="*70)
by_quad = defaultdict(list)
for t in all_trees:
    by_quad[(t['bob'], t['k'], t['n'], t['x1'])].append(t)

collisions_quad = 0
for key, trees in by_quad.items():
    bobw_set = set(t['bobw'] for t in trees)
    kw_set = set(t['kw'] for t in trees)
    if len(bobw_set) > 1 or len(kw_set) > 1:
        collisions_quad += 1
        if collisions_quad <= 5:
            print(f"\nCOLLISION: (bob={key[0]}, k={key[1]}, n={key[2]}, x1={key[3]})")
            print(f"  bobw values: {bobw_set}, kw values: {kw_set}")
            for t in trees:
                print(f"  {t['s']:25s} bobw={t['bobw']} kw={t['kw']} X={t['X']}")

print(f"\nTotal trees: {len(all_trees)}")
print(f"Distinct (bob,k,n,x1) tuples: {len(by_quad)}")
print(f"Collisions with full 4-param: {collisions_quad}")

print()
print("="*70)
print("CHECK 4: Can we compute the wrapping from ONLY (bob, k, n, x1)?")
print("="*70)

print("For x1>=2: bobw=bob, kw=k ✓")
print("For x1=1: verified unique by (bob,k,n) ✓")
print()
print("This means we can wrap ANY tree knowing only (bob, k, n, x1)!")
print()
print("The wrapping function is:")
print("  wrap(bob, k, n, x1):")
print("    if x1 >= 2: return (bob, k)        # bobw=bob, kw=k")
print("    if x1 == 1: return table[bob, k, n] # precomputed from brute force!")

print()
print("="*70)
print("CHECK 5: alice wrapping — already known")
print("="*70)
print("alice((A)) = alice(A) + 2n + 1 ✓ (n = |A|)")
print()
print("For generating function G_n(L) = Σ a^{alice}·b^{bob+k·L}:")
print("wrapping multiplies by a^{2n+1} and transforms (bob,k) as above.")
print()
print("Concatenation (known correct):")
print("  G_n(L) = Σ_m a^{m(n-m)} · P_m(L+n-m) · G_{n-m}(L)")
print("  where P_m is the wrapped generating function of subtrees of size m-1.")

print()
print("="*70)
print("SUMMARY: FEASIBLE DP APPROACH")
print("="*70)
print("1. DP state: dp[n][bob_idx][k_idx] or indexed by hash of (bob,k)")
print("2. Number of distinct (bob,k) per n is small (≤2n from data)")
print("3. Wrapping: lookup/function from (bob,k,n,x1) → (bobw,kw)")
print("4. x1 = leftmost chain length = need to track or derive")
print("5. Concat: standard formula with a^{m(n-m)} factor")
print()
print("Remaining question: Do we need to track x1 in the DP state?")
print("For x1>=2: wrapping is identity → x1 doesn't matter for concat")
print("For x1=1: wrapping changes bob, k → need to know x1")
print()
print("Maybe we can split trees by x1: those with x1=1 (leaf-first)")
print("and those with x1>=2 (non-leaf-first)?")

# Check: can we deduce x1 from (bob,k,n)?
by_bob_k_n_all = defaultdict(list)
for t in all_trees:
    by_bob_k_n_all[(t['bob'], t['k'], t['n'])].append(t)

x1_ambiguous = 0
for key, trees in by_bob_k_n_all.items():
    x1_set = set(t['x1'] for t in trees)
    if len(x1_set) > 1:
        x1_ambiguous += 1
        if x1_ambiguous <= 5:
            print(f"\n  x1 AMBIGUOUS: (bob={key[0]}, k={key[1]}, n={key[2]}) → x1∈{x1_set}")
            for t in trees[:3]:
                print(f"    {t['s']:20s} x1={t['x1']} bobw={t['bobw']} kw={t['kw']}")

print(f"\nTotal (bob,k,n) groups: {len(by_bob_k_n_all)}")
print(f"Groups with ambiguous x1: {x1_ambiguous}")
