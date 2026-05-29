import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob
from collections import defaultdict, Counter

def dyck_to_tree(s):
    nodes = [{'parent': -1, 'children': [], 'idx': 0}]
    cur = 0
    for ch in s:
        if ch == '(':
            child = len(nodes)
            nodes.append({'parent': cur, 'children': [], 'idx': child})
            nodes[cur]['children'].append(child)
            cur = child
        else:
            cur = nodes[cur]['parent']
    return nodes, 0

def compute_tree_params(nodes, root):
    depth = {}
    sz = {}
    lc = {}
    cc = {}
    si = {}
    def dfs(v):
        d = 0 if nodes[v]['parent'] == -1 else depth[nodes[v]['parent']] + 1
        depth[v] = d
        s = 1
        ch = nodes[v]['children']
        cc[v] = len(ch)
        for i, c in enumerate(ch):
            si[c] = i
            s += dfs(c)
        sz[v] = s
        lc[v] = 1 if len(ch) == 0 else 1 + lc[ch[0]]
        return s
    si[root] = 0; depth[root] = 0
    dfs(root)
    return depth, sz, lc, cc, si

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

N = 8
out_lines = []

out_lines.append("=" * 70)
out_lines.append("TREE BOB ANALYSIS: n=1..{}".format(N))
out_lines.append("=" * 70)

all_trees = []
for n in range(1, N+1):
    for s in generate_dyck(n):
        nodes, root = dyck_to_tree(s)
        depth, sz, lc, cc, si = compute_tree_params(nodes, root)
        X, bob = x_seq_and_bob(s)
        k = len(X)
        al = alice_of(s)
        x1 = X[0]
        Xw = pair_seq([1] + X)
        kw = len(Xw)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))
        X_R = pair_seq(X)
        k_R = len(X_R)
        bob_R = sum(j * X_R[j] for j in range(len(X_R)))
        all_trees.append({
            's': s, 'n': n, 'al': al, 'bob': bob, 'k': k,
            'x1': x1, 'X': list(X),
            'kw': kw, 'bobw': bobw, 'Xw': list(Xw),
            'k_R': k_R, 'bob_R': bob_R, 'X_R': list(X_R),
            'nodes': nodes, 'root': root,
            'depth': depth, 'sz': sz, 'lc': lc, 'cc': cc, 'si': si
        })

out_lines.append(f"Total Dyck words enumerated: {len(all_trees)}")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 1: x1 = lc[root] verification")
out_lines.append("=" * 70)
all_ok = True
for t in all_trees:
    if t['x1'] != t['lc'][t['root']]:
        out_lines.append(f"  MISMATCH: {t['s']} x1={t['x1']} lc={t['lc'][t['root']]}")
        all_ok = False
out_lines.append(f"  Result: {'ALL MATCH ✓' if all_ok else 'FAILURES FOUND ✗'}")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 2: Distinct (bobw, kw) pairs per subtree size")
out_lines.append("=" * 70)

subtree_catalog = defaultdict(list)
for t in all_trees:
    s = t['s']
    nodes = t['nodes']
    def process_node(v, sp):
        children = nodes[v]['children']
        subsz = 1 + sum(t['sz'][c] for c in children)
        subs = s[sp:sp+2*subsz]
        Xs, bobs = x_seq_and_bob(subs) if subs else ([], 0)
        Xws = pair_seq([1] + Xs) if Xs else [1]
        bobws = sum(j * Xws[j] for j in range(len(Xws)))
        kws = len(Xws)
        subtree_catalog[subsz].append({
            's': subs, 'lc': t['lc'][v], 'm': len(children),
            'bob': bobs, 'k': len(Xs), 'bobw': bobws, 'kw': kws,
            'x1': Xs[0] if Xs else 0,
        })
        nxt = sp + 1
        for c in children:
            process_node(c, nxt)
            nxt += 2 * t['sz'][c]
    process_node(0, 0)

for sz in range(1, min(N+1, 9)):
    entries = subtree_catalog[sz]
    bobw_kw = Counter((e['bobw'], e['kw']) for e in entries)
    bob_k = Counter((e['bob'], e['k']) for e in entries)
    catalan = len(entries)
    out_lines.append(f"  size={sz}: Catalan={catalan:5d}  distinct(bobw,kw)={len(bobw_kw):3d}  distinct(bob,k)={len(bob_k):3d}")
    if len(bobw_kw) <= 15:
        for (bw, kw_val), cnt in bobw_kw.most_common():
            x1_vals = set(e['x1'] for e in entries if e['bobw']==bw and e['kw']==kw_val)
            lc_vals = set(e['lc'] for e in entries if e['bobw']==bw and e['kw']==kw_val)
            m_vals = set(e['m'] for e in entries if e['bobw']==bw and e['kw']==kw_val)
            out_lines.append(f"    (bobw={bw:3d}, kw={kw_val:2d}): {cnt:4d} trees  x1∈{x1_vals} lc∈{lc_vals} m∈{m_vals}")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 3: Can (bobw, kw) be derived from (n, lc, m)?")
out_lines.append("=" * 70)

for sz in range(1, min(N+1, 7)):
    entries = subtree_catalog[sz]
    groups = defaultdict(list)
    for e in entries:
        key = (e['lc'], e['m'])
        groups[key].append(e)
    out_lines.append(f"\nsize={sz}: {len(entries)} subtrees, {len(groups)} (lc,m) groups")
    for (lc_val, m_val), grp in sorted(groups.items()):
        bobw_set = set(e['bobw'] for e in grp)
        kw_set = set(e['kw'] for e in grp)
        bob_set = set(e['bob'] for e in grp)
        k_set = set(e['k'] for e in grp)
        unique = "UNIQUE" if len(bobw_set) == 1 and len(kw_set) == 1 else f"bobw∈{len(bobw_set)} kw∈{len(kw_set)}"
        out_lines.append(f"  (lc={lc_val}, m={m_val}): {len(grp):3d} trees -> {unique}")
        if len(bobw_set) > 1:
            out_lines.append(f"    bobw values: {sorted(bobw_set)}")
            for e2 in grp:
                out_lines.append(f"      {e2['s']:25s} bobw={e2['bobw']} kw={e2['kw']} bob={e2['bob']} k={e2['k']}")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 4: bob vs Σ(v's subtree_size * sibling_index)")
out_lines.append("=" * 70)

for n in range(1, min(N+1, 6)):
    data_n = [t for t in all_trees if t['n'] == n]
    total = len(data_n)
    correct = 0
    for t in data_n:
        sum_si_sz = sum(t['si'][v] * t['sz'][v] for v in range(len(t['nodes'])))
        if sum_si_sz == t['bob']:
            correct += 1
    out_lines.append(f"  n={n}: bob == Σsi[v]*sz[v] for {correct}/{total} trees ({100*correct//total if total else 0}%)")
    for t in data_n:
        sum_si_sz = sum(t['si'][v] * t['sz'][v] for v in range(len(t['nodes'])))
        match = "✓" if sum_si_sz == t['bob'] else f"✗ diff={sum_si_sz - t['bob']}"
        out_lines.append(f"    {t['s']:20s} bob={t['bob']:3d} Σsi*sz={sum_si_sz:3d} {match}")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 5: bob = Σ v (step_order_of_v)")
out_lines.append("=" * 70)
out_lines.append("The x-seq process assigns each node to a step.")
out_lines.append("bob = Σ step_index(v)")

# Simulate x-seq traversal to get step indices
def get_step_indices_from_s(s):
    n = len(s) // 2
    X, _ = x_seq_and_bob(s)
    step_of_char = [-1] * (2*n)
    ci = 0
    for step_j, xj in enumerate(X):
        for _ in range(xj):
            if ci < 2*n:
                step_of_char[ci] = step_j
                ci += 1
    return step_of_char, X

for n in range(1, min(N+1, 5)):
    data_n = [t for t in all_trees if t['n'] == n]
    out_lines.append(f"\nn={n}:")
    for t in data_n:
        step_char, X = get_step_indices_from_s(t['s'])
        out_lines.append(f"  {t['s']:20s} X={X} bob={t['bob']}")
        for v in range(len(t['nodes'])):
            open_pos = None
            for ci, ch in enumerate(t['s']):
                if ch == '(':
                    open_pos = ci
            out_lines.append(f"    node{v} depth={t['depth'][v]} sz={t['sz'][v]} lc={t['lc'][v]} si={t['si'][v]} children={t['cc'][v]}")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 6: KEY - x-seq decomposition for tree root with children")
out_lines.append("=" * 70)
out_lines.append("Tree T = root[C1,C2,...,Cm]. Dyck(T) = (C1)(C2)...(Cm)")
out_lines.append("X(T) = X((C1)) ++ X((C2)) ++ ... ++ X((Cm))")
out_lines.append("")
out_lines.append("Each (Ci) has xi1 = lc(Ci) as first x-step after wrapping.")
out_lines.append("x1(T) = x1((C1)) = lc(C1) + 0? Actually x1((C1)) = lc(C1)")
out_lines.append("  Wait — x1((C1)) = 1 + x1(C1) when x1(C1) >= 2")
out_lines.append("  And x1((C1)) involves pair_seq([1]+X(C1))")

# Verify: X(T) = concat of X((Ci))
for n in range(2, min(N+1, 7)):
    data_n = [t for t in all_trees if t['n'] == n]
    for t in data_n:
        nodes = t['nodes']
        children = nodes[t['root']]['children']
        if len(children) == 0:
            continue
        X_list = []
        for c in children:
            subsz = t['sz'][c]
            subs_dyck = '(' + t['s'][1:1+2*subsz] + ''
            c_start = t['s'].index('(', 1)
            actual_start = None
            cur_pos = 1
            for ci_child in children:
                if ci_child == c:
                    actual_start = cur_pos - 1
                    break
                cur_pos += 2 * t['sz'][ci_child]
            sub_word = t['s'][actual_start:actual_start+2*(subsz+1)]
            sub_tree = t['s'][actual_start:actual_start+2*(subsz+1)]

for n in range(2, min(N+1, 7)):
    data_n = [t for t in all_trees if t['n'] == n]
    for t in data_n:
        nodes = t['nodes']
        root = t['root']
        children = nodes[root]['children']
        m = len(children)
        if m == 0:
            continue
        child_sizes = [t['sz'][c] for c in children]
        out_lines.append(f"\n  {t['s']} (n={n}, m={m})")
        out_lines.append(f"    X(T) = {t['X']}")
        out_lines.append(f"    children lc = {[t['lc'][c] for c in children]}")
        out_lines.append(f"    children sz = {child_sizes}")

        pos = 0
        all_Xw = []
        for c in children:
            c_sz = t['sz'][c]
            c_word = t['s'][pos+1:pos+1+2*c_sz]
            c_X, c_bob = x_seq_and_bob(c_word)
            c_Xw = pair_seq([1] + c_X)
            all_Xw.append(c_Xw)
            pos += 2*(c_sz+1)
        out_lines.append(f"    Xw(Ci) = {all_Xw}")
        out_lines.append(f"    concat of Xw = {sum(all_Xw, [])}")
        if sum(all_Xw, []) == t['X']:
            out_lines.append(f"    CONCAT VERIFIED ✓")
        else:
            out_lines.append(f"    MISMATCH! X(T) should be {t['X']}")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 7: Compute bob(T) from children's (bobw, kw)")
out_lines.append("=" * 70)
out_lines.append("bob(T) = Σ_i bobw_i + Σ_{i<j} kw_i * size_j")
out_lines.append("where size_j = sz(Cj) + 1 (wrapped size)")

for n in range(2, min(N+1, 8)):
    data_n = [t for t in all_trees if t['n'] == n]
    all_ok = True
    for t in data_n:
        nodes = t['nodes']
        root = t['root']
        children = nodes[root]['children']
        if len(children) == 0:
            continue
        bobw_list = []
        kw_list = []
        size_list = []
        pos = 0
        for c in children:
            c_sz = t['sz'][c]
            c_word = t['s'][pos+1:pos+1+2*c_sz]
            c_X, _ = x_seq_and_bob(c_word)
            c_Xw = pair_seq([1] + c_X)
            bobw_i = sum(j * c_Xw[j] for j in range(len(c_Xw)))
            kw_i = len(c_Xw)
            bobw_list.append(bobw_i)
            kw_list.append(kw_i)
            size_list.append(c_sz + 1)
            pos += 2*(c_sz+1)

        bob_concat = 0
        for i in range(len(children)):
            bob_concat += bobw_list[i]
            for j in range(i+1, len(children)):
                bob_concat += kw_list[i] * size_list[j]

        if bob_concat != t['bob']:
            out_lines.append(f"  MISMATCH: {t['s']} bob={t['bob']} computed={bob_concat}")
            all_ok = False
    if all_ok:
        out_lines.append(f"  n={n}: ALL MATCH ✓")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 8: Tree-shape DP feasibility study")
out_lines.append("=" * 70)
out_lines.append("If we know (bobw, kw) for each possible child subtree of size k,")
out_lines.append("we can compute bob(T) for any tree via the concat formula.")
out_lines.append("")
out_lines.append("The number of DISTINCT (bobw, kw) pairs per size:")
for sz in range(1, N+1):
    entries = subtree_catalog[sz]
    bobw_kw = set((e['bobw'], e['kw']) for e in entries)
    out_lines.append(f"  size {sz}: {len(bobw_kw)} pairs (from {len(entries)} subtrees)")
out_lines.append("")
out_lines.append("However, this still requires iterating over all (bobw, kw) pairs")
out_lines.append("and their multiplicities. For size N, this could be O(N * distinct_pairs).")
out_lines.append(f"The growth rate: size 7 has {len(set((e['bobw'], e['kw']) for e in subtree_catalog[7]))} pairs from 429 trees.")

out_lines.append("")
out_lines.append("=" * 70)
out_lines.append("ANALYSIS 9: Relationship between bob and sum of left_chain lengths")
out_lines.append("=" * 70)
for n in range(1, min(N+1, 6)):
    data_n = [t for t in all_trees if t['n'] == n]
    for t in data_n:
        sum_lc = sum(t['lc'][v] for v in range(len(t['nodes'])))
        sum_depth = sum(t['depth'][v] for v in range(len(t['nodes'])))
        out_lines.append(f"  {t['s']:20s} bob={t['bob']:3d} Σlc={sum_lc:3d} Σdepth={sum_depth:3d}  bob-Σlc={t['bob']-sum_lc}")

with open('tree_analysis_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print("Output written to tree_analysis_output.txt")
print(f"Lines: {len(out_lines)}")
