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

def wrap_from_blocks(blocks):
    """
    blocks: list of Xw sequences (each already pair_seq-compressed)
    Returns pair_seq([1] + concat of blocks) as (bobw, kw, first, last)
    """
    full_seq = [1]
    for blk in blocks:
        full_seq.extend(blk)

    result = pair_seq(full_seq)
    bobw = sum(j * result[j] for j in range(len(result)))
    kw = len(result)
    first = result[0] if result else 0
    last = result[-1] if result else 0
    return bobw, kw, first, last, result

def wrap_boundary_only(blocks):
    """
    Computes the same wrapping result using ONLY block-level info.
    Blocks: list of (bobw_i, kw_i, first_i, last_i, sum_i, seq_i)
    where sum_i = sum of elements in seq_i = |inner_tree| + 1
    """
    result_seq = []
    n = len(blocks)

    if n == 0:
        result_seq = [2]
        return 0, 1, 2, 2, result_seq

    result_seq.append(1 + blocks[0][5][0])

    for i in range(n):
        seq = list(blocks[i][5])
        if i == 0:
            seq = seq[1:]

        if i > 0 and blocks[i-1][3] == 1:
            result_seq[-1] = 2 + blocks[i][5][0] if blocks[i-1][3]==1 else result_seq[-1]
            seq = seq[1:]
        else:
            result_seq.extend(seq)

    merged = []
    i = 0
    while i < len(result_seq):
        if result_seq[i] == 1 and i + 1 < len(result_seq):
            merged.append(1 + result_seq[i+1])
            i += 2
        else:
            merged.append(result_seq[i])
            i += 1

    bobw = sum(j * merged[j] for j in range(len(merged)))
    kw = len(merged)
    first_r = merged[0] if merged else 0
    last_r = merged[-1] if merged else 0
    return bobw, kw, first_r, last_r, merged


print("="*70)
print("BOUNDARY-ONLY WRAPPING — FINAL VERIFICATION")
print("="*70)

total_ok = 0
total_fail = 0
fail_examples = []

for t in all_trees:
    s = t['s']
    n = t['n']

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
    blocks = []
    pos = 0
    for c in children:
        c_sz_val = sz(c)
        c_word = s[pos:pos+2*c_sz_val]
        c_X, _ = x_seq_and_bob(c_word)
        c_Xw = pair_seq([1] + c_X)
        c_bobw = sum(j * c_Xw[j] for j in range(len(c_Xw)))
        c_kw = len(c_Xw)
        c_first = c_Xw[0] if c_Xw else 0
        c_last = c_Xw[-1] if c_Xw else 0
        c_sum = sum(c_Xw)
        blocks.append((c_bobw, c_kw, c_first, c_last, c_sum, c_Xw))
        pos += 2*c_sz_val

    gt_bobw, gt_kw, gt_first, gt_last, gt_result = wrap_from_blocks([b[5] for b in blocks])
    calc_bobw, calc_kw, calc_first, calc_last, calc_result = wrap_boundary_only(blocks)

    if gt_result == calc_result:
        total_ok += 1
    else:
        total_fail += 1
        if len(fail_examples) < 5:
            fail_examples.append((s, blocks, gt_result, calc_result))

for s, blks, gt, calc in fail_examples:
    print(f"  FAIL: {s}")
    print(f"    blocks: {[list(b[5]) for b in blks]}")
    print(f"    GT: {gt}, Calc: {calc}")

print(f"\nTOTAL: {total_ok} ok, {total_fail} fail out of {total_ok+total_fail}")
