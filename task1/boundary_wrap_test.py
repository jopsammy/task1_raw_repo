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

def compute_wrapped_from_children_blocks(blocks):
    """
    blocks: list of (bobw_i, kw_i, first_i, last_i, size_i, full_Xw_i)
    Computes X((T)) = pair_seq([1] ++ Xw_1 ++ Xw_2 ++ ... ++ Xw_m)
    Returns: (bobw, kw, first, last)
    """
    n_blocks = len(blocks)
    if n_blocks == 0:
        return 0, 1, 2, 2

    bobw = 0
    kw = 0
    cumul_k = 0
    
    first_output = 1 + blocks[0][2]
    last_output = blocks[-1][3]

    for i, (bobw_i, kw_i, first_i, last_i, size_i, _) in enumerate(blocks):
        if i == 0:
            bobw += bobw_i
            kw += kw_i
            cumul_k = kw_i
        else:
            prev_last = blocks[i-1][3]
            if prev_last == 1:
                bobw += bobw_i - first_i
                kw += kw_i - 1
                cumul_k += kw_i - 1
            else:
                bobw += bobw_i + (cumul_k) * size_i
                kw += kw_i
                cumul_k += kw_i

    for i in range(1, n_blocks):
        prev_last = blocks[i-1][3]
        if prev_last == 1:
            bobw -= cumul_k * (1 if i == n_blocks - 1 else blocks[i][4])

    if blocks[-1][3] == 1:
        last_output = 1

    return bobw, kw, first_output, last_output

def compute_wrapped_from_signatures(blocks):
    """
    blocks: list of (bobw_i, kw_i, first_i, last_i, size_i, full_Xw_i)
    Computes wrapping result from signature info only (no full sequences)
    """
    if not blocks:
        return 0, 1, 2, 2, 0, 1

    n = len(blocks)

    result_elements = []
    result_bob = 0
    result_k = 0

    result_elements.append(1 + blocks[0][2])

    running_k = 1

    for i in range(n):
        bobw_i = blocks[i][0]
        kw_i = blocks[i][1]
        first_i = blocks[i][2]
        last_i = blocks[i][3]
        size_i = blocks[i][4]
        seq_i = blocks[i][5]

        if i == 0:
            internal_seq = seq_i[1:]
        else:
            internal_seq = list(seq_i)

        if i > 0 and blocks[i-1][3] == 1:
            merged = 1 + internal_seq[0]
            internal_seq = internal_seq[1:]
            result_elements.append(merged)
            running_k += 1

        for idx, val in enumerate(internal_seq):
            result_elements.append(val)
            running_k += 1

    full_seq = result_elements
    full_result = pair_seq([1] + sum([list(b[5]) for b in blocks], []))
    ground_truth = (sum(j*full_result[j] for j in range(len(full_result))),
                    len(full_result),
                    full_result[0] if full_result else 0,
                    full_result[-1] if full_result else 0)

    if full_seq and full_seq[-1] == 1 and 1 + 1 <= len(full_result):
        pass

    bobw_sig = sum((j) * full_seq[j] for j in range(len(full_seq)))
    kw_sig = len(full_seq)
    first_sig = full_seq[0] if full_seq else 0
    last_sig = full_seq[-1] if full_seq else 0

    return bobw_sig, kw_sig, first_sig, last_sig, ground_truth[0], ground_truth[1]


def compute_wrapping_boundary_correct(blocks):
    """
    Correct computation of X((T)) = pair_seq([1] + Xw_1 ++ Xw_2 ++ ...) 
    using boundary-only info.
    """
    full = [1]
    for _, _, _, _, _, seq in blocks:
        full.extend(seq)
    compressed = pair_seq(full)
    gt_bobw = sum(j * compressed[j] for j in range(len(compressed)))
    gt_kw = len(compressed)
    gt_first = compressed[0]
    gt_last = compressed[-1]

    bobw = 0
    kw_total = 0
    cumul_k = 0

    for i, (bobw_i, kw_i, first_i, last_i, size_i, _) in enumerate(blocks):
        if i == 0:
            bobw += bobw_i
        else:
            bobw += bobw_i

        if i > 0:
            bobw += cumul_k * size_i

        kw_total += kw_i
        cumul_k += kw_i

    first_out = 1 + blocks[0][2]

    for i in range(1, len(blocks)):
        if blocks[i-1][3] == 1:
            bobw -= blocks[i][2]
            kw_total -= 1
            cumul_k -= 1

    if blocks[-1][3] != 1:
        last_out = blocks[-1][3]
    else:
        last_out = 1

    if gt_bobw != bobw or gt_kw != kw_total:
        return False, (gt_bobw, gt_kw, gt_first, gt_last), (bobw, kw_total, first_out, last_out), blocks
    return True, None, None, None

print("="*70)
print("BOUNDARY-ONLY WRAPPING COMPUTATION TEST")
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
        c_sz = sz(c)
        c_word = s[pos:pos+2*c_sz]
        c_X, _ = x_seq_and_bob(c_word)
        c_Xw = pair_seq([1] + c_X)
        c_bobw = sum(j * c_Xw[j] for j in range(len(c_Xw)))
        c_kw = len(c_Xw)
        c_first = c_Xw[0] if c_Xw else 0
        c_last = c_Xw[-1] if c_Xw else 0
        blocks.append((c_bobw, c_kw, c_first, c_last, c_sz, c_Xw))
        pos += 2*c_sz

    ok, gt, calc, blks = compute_wrapping_boundary_correct(blocks)
    if ok:
        total_ok += 1
    else:
        total_fail += 1
        if len(fail_examples) < 5:
            fail_examples.append((s, gt, calc, blks))

for s, gt, calc, blks in fail_examples:
    print(f"  FAIL: {s}")
    print(f"    blocks: {[(b[2],b[3],b[4],b[5]) for b in blks]}")
    print(f"    GT: bobw={gt[0]} kw={gt[1]} first={gt[2]} last={gt[3]}")
    print(f"    Calc: bobw={calc[0]} kw={calc[1]} first={calc[2]} last={calc[3]}")

print(f"\nTOTAL: {total_ok} ok, {total_fail} fail out of {total_ok+total_fail}")
