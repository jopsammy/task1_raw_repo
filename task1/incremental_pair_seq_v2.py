import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

def wrap_children_incremental(child_xws):
    """
    child_xws: list of (first, last, bobw, kw, seq) for each child's wrapped X-sequence
    Computes pair_seq([1] ++ concat of child seqs) using incremental boundary-aware merging.
    Returns: (bobw, kw, first, last, result_seq)
    """
    result = []

    if child_xws and child_xws[0][4]:
        result.append(1 + child_xws[0][4][0])
        first_consumed = True
    else:
        result.append(1)
        first_consumed = False

    pending_1 = False

    for idx, (first, last, bobw, kw, seq) in enumerate(child_xws):
        s = list(seq)
        if idx == 0 and first_consumed:
            s = s[1:]

        if pending_1 and s:
            result[-1] = 1 + s[0]
            s = s[1:]
            pending_1 = False

        if pending_1:
            result.append(1)
            pending_1 = False

        result.extend(s)

        if s and s[-1] == 1:
            pending_1 = True
            result.pop()
        else:
            pending_1 = False

    if pending_1:
        result.append(1)

    bobw = sum(j * result[j] for j in range(len(result)))
    kw = len(result)
    first_r = result[0] if result else 0
    last_r = result[-1] if result else 0
    return bobw, kw, first_r, last_r, result

N = 8

all_trees = []
for n in range(1, N+1):
    for s in generate_dyck(n):
        X, bob = x_seq_and_bob(s)
        Xw = pair_seq([1] + X)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        all_trees.append({
            's': s, 'n': n, 'bob': bob, 'k': len(X), 'x1': X[0],
            'bobw': bobw, 'kw': kw, 'X': list(X), 'Xw': list(Xw)
        })

print("="*70)
print("INCREMENTAL BOUNDARY-AWARE pair_seq TEST")
print("="*70)

single_pass = 0
single_fail = 0
for t in all_trees:
    Xw = t['Xw']
    first_xw = Xw[0] if Xw else 0
    last_xw = Xw[-1] if Xw else 0
    blocks = [(first_xw, last_xw, 0, len(Xw), Xw)]
    bobw_c, kw_c, _, _, res = wrap_children_incremental(blocks)
    if bobw_c == t['bobw'] and kw_c == t['kw'] and res == Xw:
        single_pass += 1
    else:
        single_fail += 1
        if single_fail <= 3:
            print(f"  FAIL single: {t['s']} Xw={Xw} res={res}")

print(f"Single-block: pass={single_pass} fail={single_fail}")

print("\nTree decomposition test:")
total_pass = 0
total_fail = 0
for n in range(2, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    pass_n = 0
    for t in data_n:
        s = t['s']
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

        def compute_sz(v):
            s_val = 1
            for c in nodes[v]['children']:
                s_val += compute_sz(c)
            return s_val
        sz = {v: compute_sz(v) for v in range(len(nodes))}

        children = nodes[0]['children']
        blocks = []
        pos = 0
        for c in children:
            c_sz = sz[c]
            c_word = s[pos:pos+2*(c_sz+1)]
            c_X, _ = x_seq_and_bob(c_word)
            c_Xw = pair_seq([1] + c_X)
            c_first = c_Xw[0] if c_Xw else 0
            c_last = c_Xw[-1] if c_Xw else 0
            c_bobw = sum(j * c_Xw[j] for j in range(len(c_Xw)))
            c_kw = len(c_Xw)
            blocks.append((c_first, c_last, c_bobw, c_kw, c_Xw))
            pos += 2*(c_sz+1)

        bobw_c, kw_c, _, _, res = wrap_children_incremental(blocks)

        if bobw_c == t['bobw'] and kw_c == t['kw']:
            pass_n += 1
        else:
            if total_fail < 5:
                print(f"  FAIL n={n}: {s}")
                print(f"    X_true={t['X']}, Xw_true={t['Xw']}")
                print(f"    blocks: {[b[4] for b in blocks]}")
                print(f"    result={res}, bobw={bobw_c} true={t['bobw']}, kw={kw_c} true={t['kw']}")

    print(f"  n={n}: {pass_n}/{len(data_n)} passed")
    total_pass += pass_n
    total_fail += len(data_n) - pass_n

print(f"\nTOTAL: {total_pass} passed, {total_fail} failed out of {total_pass+total_fail}")
