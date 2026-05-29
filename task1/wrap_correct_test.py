import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob
from collections import defaultdict, Counter

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

def wrap_boundary(blocks):
    """blocks: list of x-sequences (X(P_i) for child primitives)"""
    if not blocks:
        return [2]
    assembled = [1 + blocks[0][0]]
    for i in range(len(blocks)):
        seq = list(blocks[i])
        if i == 0:
            seq = seq[1:]
        if i > 0 and assembled and assembled[-1] == 1:
            assembled[-1] = 1 + seq[0]
            seq = seq[1:]
        assembled.extend(seq)
    return pair_seq(assembled)

N = 8

all_trees = []
for n in range(1, N+1):
    for s in generate_dyck(n):
        X, bob = x_seq_and_bob(s)
        k = len(X)
        Xw = pair_seq([1] + X)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        all_trees.append({
            's': s, 'n': n, 'bob': bob, 'k': k, 'first': X[0], 'last': X[-1],
            'bobw': bobw, 'kw': kw, 'first_w': Xw[0], 'last_w': Xw[-1],
            'X': list(X), 'Xw': list(Xw)
        })

print("="*70)
print("CORRECTED: Boundary wrapping with child primitive X-sequences")
print("="*70)
print("For T = (C₁)(C₂)...(Cₘ):")
print("  blocks = X(P₁), X(P₂), ..., X(Pₘ) = X((C₁)), X((C₂)), ...")
print("  But X((C)) = Xw(C) = pair_seq([1]+X(C))")
print("  So blocks = Xw(C_i) — the wrapped X of INNER trees")
print("  NOT the wrapping of Xw, but Xw itself!")
print()
print("Actually, X(P) where P = (C) is: X(P) = Xw(C) (pair_seq([1]+X(C)))")
print("And the block for child P is X(P) = Xw(C)")
print()
print("So the blocks ARE Xw(C). But Xw(C) for the INNER tree of each child.")
print("In my tree encoding: child node represents P = (C). sz(node) = |C|+1.")
print("The inner C has size sz(node)-1.")
print("X(C) = x-seq of the inner C's Dyck word.")
print("X(P) = Xw(C) = pair_seq([1]+X(C)).")
print("="*70)

total_ok = 0
total_fail = 0
fail_examples = []

for t in all_trees:
    s = t['s']
    nodes = [{'parent': -1, 'children': []}]
    cur = 0
    for ch in s:
        if ch == '(':
            child = len(nodes)
            nodes.append({'parent': cur, 'children': []})
            nodes[cur]['children'].append(child)
            cur = child
        else:
            cur = nodes[cur]['parent']

    def sz(v):
        s_val = 1
        for c in nodes[v]['children']:
            s_val += sz(c)
        return s_val

    # Get top-level primitives = children of node 0
    children = nodes[0]['children']
    blocks_Xw = []
    pos = 0
    for c in children:
        c_sz = sz(c)
        # c is the node representing the outer '(' of (C_inner)
        # Inner tree size = c_sz - 1
        inner_sz = c_sz - 1
        # Inner tree Dyck word starts at pos+1 (after the wrapping '(')
        inner_word = s[pos+1:pos+1+2*inner_sz] if inner_sz > 0 else ''
        inner_X, _ = x_seq_and_bob(inner_word)
        # X(P) = X((C_inner)) = pair_seq([1] + X(C_inner))
        X_P = pair_seq([1] + inner_X)
        blocks_Xw.append(X_P)
        pos += 2 * c_sz  # Advance past this primitive

    # Ground truth: X((T)) = pair_seq([1] + X(T))
    Xw_true = pair_seq([1] + t['X'])

    # Our wrapping: pair_seq([1] + concat of X(P_i))
    our_Xw = wrap_boundary(blocks_Xw)

    if our_Xw == Xw_true:
        total_ok += 1
    else:
        total_fail += 1
        if len(fail_examples) < 8:
            fail_examples.append((s, t['X'], blocks_Xw, Xw_true, our_Xw))

for s, X, blks, gt, calc in fail_examples:
    print(f"  FAIL: {s}")
    print(f"    X(T)={X}, children X(P_i)={blks}")
    print(f"    GT Xw={gt}, Our Xw={calc}")

print(f"\nTOTAL: {total_ok} ok, {total_fail} fail out of {total_ok+total_fail}")
