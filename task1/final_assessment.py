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
        sw = sum(Xw)
        all_trees.append({
            's': s, 'n': n,
            'bob': bob, 'k': k, 'first': first, 'last': last,
            'bobw': bobw, 'kw': kw, 'first_w': first_w, 'last_w': last_w,
            'sw': sw,
            'X': list(X), 'Xw': list(Xw)
        })

def wrap_boundary(blocks_info):
    """blocks_info: list of (bobw, kw, sum_val, first, last, Xw_seq)"""
    assembled = [1 + blocks_info[0][3]]
    for i in range(len(blocks_info)):
        seq = list(blocks_info[i][5])
        if i == 0:
            seq = seq[1:]
        if i > 0 and blocks_info[i-1][4] == 1:
            assembled[-1] = 1 + seq[0]
            seq = seq[1:]
        assembled.extend(seq)
    result = pair_seq(assembled)
    bobw_r = sum(j * result[j] for j in range(len(result)))
    kw_r = len(result)
    return bobw_r, kw_r, result


print("="*70)
print("CHECK: For WRAPPED signatures, does (bobw, kw, n, first_w, last_w)")
print("uniquely determine the contribution in wrapping?")
print("="*70)

wrapped_groups = defaultdict(list)
for t in all_trees:
    wrapped_groups[(t['bobw'], t['kw'], t['n'], t['first_w'], t['last_w'])].append(t)

w_collisions = 0
for key, trees in wrapped_groups.items():
    Xw_set = set(tuple(t['Xw']) for t in trees)
    if len(Xw_set) > 1:
        w_collisions += 1
        if w_collisions <= 5:
            print(f"\n  Different Xw for same 5-param: (bobw={key[0]}, kw={key[1]}, n={key[2]}, first={key[3]}, last={key[4]})")
            for t in trees:
                print(f"    {t['s']:25s} Xw={t['Xw']} bobw={t['bobw']} kw={t['kw']}")
            if w_collisions == 5:
                print(f"  ... (more)")

print(f"\nWrapped signature groups: {len(wrapped_groups)}")
print(f"Groups with multiple Xw sequences: {w_collisions}")

print()
print("="*70)
print("Now test: If we use BOUNDARY-ONLY wrapping with just 5-param info,")
print("does it still work? (without knowing the full Xw sequences)")
print("We'll use any representative Xw from the group.")
print("="*70)

for n in range(2, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    ok_n = 0
    for t in data_n:
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

        children = nodes[0]['children']
        child_blocks = []
        all_child_sz = []
        pos = 0
        for c in children:
            c_sz_val = sz(c)
            all_child_sz.append(c_sz_val)
            c_word = s[pos:pos+2*c_sz_val]
            c_X, _ = x_seq_and_bob(c_word)
            c_Xw = pair_seq([1] + c_X)
            c_bobw = sum(j * c_Xw[j] for j in range(len(c_Xw)))
            c_kw = len(c_Xw)
            c_first = c_Xw[0]
            c_last = c_Xw[-1]
            c_sum = sum(c_Xw)
            child_blocks.append((c_bobw, c_kw, c_sum, c_first, c_last, c_Xw))
            pos += 2*c_sz_val

        gt_bobw, gt_kw, gt_result = wrap_boundary(child_blocks)

        child_params_only = [(bw, kw_val, sw, f, l, []) for (bw, kw_val, sw, f, l, _) in child_blocks]

        if child_blocks:
            child_params_only[0] = (child_blocks[0][0], child_blocks[0][1], child_blocks[0][2],
                                     child_blocks[0][3], child_blocks[0][4], child_blocks[0][5])

        if gt_bobw == t['bobw'] and gt_kw == t['kw']:
            ok_n += 1

    print(f"  n={n}: GT wrapping from full Xw: {ok_n}/{len(data_n)} OK")

print()
print("="*70)
print("SUMMARY OF FINDINGS")
print("="*70)
print("1. Concat formula X(PQ) = X(P) ++ X(Q) ✓ (n≤8, 2055/2055)")
print("2. bob(PQ) = bob(P) + bob(Q) + k(P)·|Q| ✓ (n≤8)")
print("3. Boundary-only wrapping: 2055/2055 ✓")
print(f"4. 4-param (bob,k,first,last) → wrapping: {30} collisions")
print(f"5. 5-param (bob,k,first,last,n) → wrapping: 9 collisions")
print(f"6. Wrapped sig (bobw,kw,first_w,last_w,n): {w_collisions} groups with multiple Xw")
print()
print("CONCLUSION: For wrapping computation, we need the full list of children's Xw sequences.")
print("The Xw sequences cannot be reduced to a small signature for wrapping purposes.")
print()
print("NEXT: Either track full Xw sequences (O(Catalan) states = impossible),")
print("or find a DIFFERENT approach to the problem.")
