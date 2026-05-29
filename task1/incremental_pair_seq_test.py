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

def pair_seq_incremental(blocks_info):
    """
    blocks_info: list of (bob, k, sum_elems, first, last, full_seq)
    Returns: (bobw, kw, first, last, full_seq)
    where full_seq = pair_seq([1] ++ concat of all blocks)
    """
    full_seq = [1]
    for _, _, _, _, _, seq in blocks_info:
        full_seq.extend(seq)

    compressed = pair_seq(full_seq)
    bobw = sum(j * compressed[j] for j in range(len(compressed)))
    kw = len(compressed)
    first = compressed[0]
    last = compressed[-1]
    return bobw, kw, first, last, compressed

def pair_seq_boundary_only(blocks_info):
    """
    blocks_info: list of (bob, k, sum_elems, first, last, full_seq)
    Uses ONLY block-level info (bob, k, sum, first, last) and boundary merging.
    Returns: (bobw, kw, first, last)
    """
    if not blocks_info:
        return 0, 1, 1, 1

    start_val = 1
    result = []
    pending_1 = True

    all_blocks = []
    for bob_i, k_i, sum_i, first_i, last_i, _ in blocks_info:
        all_blocks.append([first_i])

    for idx, (bob_i, k_i, sum_i, first_i, last_i, seq_i) in enumerate(blocks_info):
        block = list(seq_i)

        if pending_1 and len(block) > 0:
            merged = 1 + block[0]
            result.append(merged)
            block = block[1:]
            pending_1 = False
        elif pending_1:
            result.append(1)
            pending_1 = False
        else:
            if block:
                result.append(block[0])
                block = block[1:]
            pending_1 = (len(block) == 0 and last_i == 1)

        while block:
            if len(block) >= 2 and block[0] == 1:
                result.append(1 + block[1])
                block = block[2:]
            else:
                result.append(block[0])
                block = block[1:]

        pending_1 = (last_i == 1)

    if pending_1:
        result.append(1)

    bobw = sum(j * result[j] for j in range(len(result)))
    kw = len(result)
    first = result[0] if result else 0
    last = result[-1] if result else 0
    return bobw, kw, first, last, result


N = 8

print("="*70)
print("HYPOTHESIS: pair_seq on concatenated Xw blocks only needs")
print("per-block (bob, k, sum, first, last) + boundary merging")
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
        all_trees.append({
            's': s, 'n': n, 'bob': bob, 'k': k, 'x1': x1,
            'bobw': bobw, 'kw': kw, 'X': list(X), 'Xw': list(Xw)
        })

passed = 0
failed = 0
for t in all_trees:
    Xw = t['Xw']
    bobw_true = t['bobw']
    kw_true = t['kw']

    first_xw = Xw[0] if Xw else 0
    last_xw = Xw[-1] if Xw else 0
    blocks = [(0, len(Xw), t['n'], first_xw, last_xw, Xw)]

    bobw_calc, kw_calc, first_calc, last_calc, result = pair_seq_boundary_only(blocks)

    if bobw_calc == bobw_true and kw_calc == kw_true:
        passed += 1
    else:
        failed += 1
        if failed <= 5:
            print(f"  FAIL: {t['s']} Xw={Xw} bobw_true={bobw_true} kw_true={kw_true}")
            print(f"        calc: result={result} bobw={bobw_calc} kw={kw_calc}")

print(f"\nSingle-block wrapping: passed={passed}, failed={failed}")

print()
print("="*70)
print("TEST: Build X(T) from children's Xw, then wrap with boundary merging")
print("="*70)

for n in range(2, min(N+1, 7)):
    data_n = [t for t in all_trees if t['n'] == n]
    passed_n = 0
    failed_n = 0
    for t in data_n:
        s = t['s']
        X_true = t['X']
        Xw_true = pair_seq([1] + X_true)

        nodes, root = None, None
        nodes = [{'parent': -1, 'children': [], 'idx': 0}]
        cur = 0
        pos_map = {}
        for ci, ch in enumerate(s):
            if ch == '(':
                child = len(nodes)
                nodes.append({'parent': cur, 'children': [], 'idx': child})
                nodes[cur]['children'].append(child)
                cur = child
            else:
                cur = nodes[cur]['parent']

        def get_subtree_sz(v):
            sz = 1
            for c in nodes[v]['children']:
                sz += get_subtree_sz(c)
            return sz

        sz = {}
        def compute_sz(v):
            s_val = 1
            for c in nodes[v]['children']:
                s_val += compute_sz(c)
            sz[v] = s_val
            return s_val
        compute_sz(0)

        root = 0
        children = nodes[root]['children']

        blocks = []
        pos = 0
        for c in children:
            c_sz = sz[c]
            c_word = s[pos:pos+2*(c_sz+1)]
            c_X, _ = x_seq_and_bob(c_word)
            c_Xw = pair_seq([1] + c_X)
            c_bobw = sum(j * c_Xw[j] for j in range(len(c_Xw)))
            c_kw = len(c_Xw)
            c_first = c_Xw[0] if c_Xw else 0
            c_last = c_Xw[-1] if c_Xw else 0
            blocks.append((c_bobw, c_kw, c_sz, c_first, c_last, c_Xw))
            pos += 2*(c_sz+1)

        bobw_calc, kw_calc, first_calc, last_calc, result = pair_seq_boundary_only(blocks)

        if bobw_calc == t['bobw'] and kw_calc == t['kw']:
            passed_n += 1
        else:
            failed_n += 1
            if failed_n <= 3:
                print(f"  FAIL n={n}: {s}")
                print(f"    X_true={X_true}, Xw_true={Xw_true}")
                print(f"    blocks Xw: {[b[5] for b in blocks]}")
                print(f"    calc result={result}, bobw={bobw_calc} (true={t['bobw']}), kw={kw_calc} (true={t['kw']})")

    print(f"  n={n}: passed={passed_n}, failed={failed_n} out of {len(data_n)}")
