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

all_trees = []
for n in range(1, N+1):
    for s in generate_dyck(n):
        X, bob = x_seq_and_bob(s)
        k = len(X)
        first = X[0]
        last = X[-1]
        Xw = pair_seq([1] + X)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        first_w = Xw[0]
        last_w = Xw[-1]
        all_trees.append({
            's': s, 'n': n,
            'bob': bob, 'k': k, 'first': first, 'last': last,
            'bobw': bobw, 'kw': kw, 'first_w': first_w, 'last_w': last_w,
            'X': list(X), 'Xw': list(Xw)
        })

print("="*70)
print("CRITICAL: Does (bob, k, first, last) determine wrapping?")
print("="*70)

groups = defaultdict(list)
for t in all_trees:
    groups[(t['bob'], t['k'], t['first'], t['last'])] .append(t)

collisions = 0
for key, trees in groups.items():
    bobw_set = set(t['bobw'] for t in trees)
    kw_set = set(t['kw'] for t in trees)
    firstw_set = set(t['first_w'] for t in trees)
    lastw_set = set(t['last_w'] for t in trees)
    if len(bobw_set) > 1 or len(kw_set) > 1:
        collisions += 1
        if collisions <= 10:
            print(f"\n  COLLISION: (bob={key[0]}, k={key[1]}, first={key[2]}, last={key[3]})")
            print(f"    bobw values: {bobw_set}, kw: {kw_set}, first_w: {firstw_set}, last_w: {lastw_set}")
            for t in trees:
                print(f"    {t['s']:25s} X={t['X']} Xw={t['Xw']} bobw={t['bobw']} kw={t['kw']}")

print(f"\nTotal groups: {len(groups)}")
print(f"Collisions: {collisions}")

print()
print("="*70)
print("Also check: (bob, k, first, last, n) determines wrapping?")
print("="*70)

groups5 = defaultdict(list)
for t in all_trees:
    groups5[(t['bob'], t['k'], t['first'], t['last'], t['n'])].append(t)

collisions5 = 0
for key, trees in groups5.items():
    bobw_set = set(t['bobw'] for t in trees)
    kw_set = set(t['kw'] for t in trees)
    if len(bobw_set) > 1 or len(kw_set) > 1:
        collisions5 += 1

print(f"Total 5-param groups: {len(groups5)}")
print(f"Collisions: {collisions5}")
