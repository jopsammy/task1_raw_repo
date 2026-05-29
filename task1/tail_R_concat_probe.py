import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, x_seq_and_bob

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

N_P = 8

def wrapped_state_from_word(s):
    X_raw, _ = x_seq_and_bob(s)
    Xw = pair_seq([1] + X_raw)
    bobw = sum(j * Xw[j] for j in range(len(Xw)))
    kw = len(Xw)
    x1w = Xw[0]
    sum_Xw = sum(Xw)
    tr_seq = Xw[1:]
    tr_bob = sum(j * tr_seq[j] for j in range(len(tr_seq)))
    tr_k = len(tr_seq)
    tr_last = tr_seq[-1] if tr_seq else 0
    tr_sum = sum(tr_seq)
    return {'Xw': list(Xw), 'bobw': bobw, 'kw': kw, 'x1w': x1w, 'sum_Xw': sum_Xw,
            'tr_seq': list(tr_seq), 'tr_bob': tr_bob, 'tr_k': tr_k,
            'tr_last': tr_last, 'tr_sum': tr_sum, 'n': len(s) // 2}

def _param_merge(p, q):
    tr_last_p = p['tr_last']
    x1w_q = q['x1w']
    trb_q, trk_q, trl_q, trs_q = q['tr_bob'], q['tr_k'], q['tr_last'], q['tr_sum']
    if tr_last_p == 1 and p['tr_k'] > 0:
        new_trl = trl_q if trk_q > 0 else (1 + x1w_q)
        return (p['tr_bob'] - (p['tr_k'] - 1) + (p['tr_k'] - 1) * (1 + x1w_q)
                + trb_q + p['tr_k'] * trs_q,
                p['tr_k'] + trk_q,
                p['tr_sum'] - 1 + (1 + x1w_q) + trs_q,
                new_trl)
    else:
        bob_R_q = trb_q + trs_q
        sum_R_q = x1w_q + trs_q
        new_trl = trl_q if trk_q > 0 else x1w_q
        return (p['tr_bob'] + bob_R_q + p['tr_k'] * sum_R_q,
                p['tr_k'] + 1 + trk_q,
                p['tr_sum'] + x1w_q + trs_q,
                new_trl)

def param_concat(p, q):
    trb, trk, trs, trl = _param_merge(p, q)
    return {'sum_Xw': p['sum_Xw'] + q['sum_Xw'], 'x1w': p['x1w'],
            'tr_bob': trb, 'tr_k': trk, 'tr_last': trl, 'tr_sum': trs}

def apply_wrapping(forest_params, total_n):
    fp = forest_params
    return {
        'bobw': fp['tr_bob'] + (fp['sum_Xw'] - fp['x1w']),
        'kw': 1 + fp['tr_k'],
        'sum_Xw': 1 + fp['x1w'] + fp['tr_sum'],
        'x1w': 1 + fp['x1w'],
        'tr_bob': fp['tr_bob'], 'tr_k': fp['tr_k'],
        'tr_last': fp['tr_last'], 'tr_sum': fp['tr_sum'],
        'n': total_n + 1,
    }

print("="*70)
print("TASK 1e-1 v7: Concat + Wrapping with forest/wrapped distinction")
print("="*70)
print("FOREST: concat of children's Xw (NOT a wrapped word)")
print("WRAPPED: parent = pair_seq([1] + forest_concat)")
print("PARAM-ONLY: both operations use only aggregated parameters")

print()
print("="*70)
print("TEST 1: Forest concat from Xw → params (ground truth)")
print("="*70)

fo = 0; ff = 0
for n_p in range(1, N_P):
    for n_q in range(1, N_P - n_p + 1):
        for p_s in generate_dyck(n_p):
            for q_s in generate_dyck(n_q):
                ps = wrapped_state_from_word(p_s)
                qs = wrapped_state_from_word(q_s)

                full_seq = ps['tr_seq'] + [qs['x1w']] + qs['tr_seq']
                tr_result = pair_seq(full_seq)

                gt = {
                    'sum_Xw': ps['sum_Xw'] + qs['sum_Xw'],
                    'x1w': ps['x1w'],
                    'tr_bob': sum(j * tr_result[j] for j in range(len(tr_result))),
                    'tr_k': len(tr_result),
                    'tr_last': tr_result[-1] if tr_result else 0,
                    'tr_sum': sum(tr_result),
                }
                predicted = {
                    'sum_Xw': ps['sum_Xw'] + qs['sum_Xw'],
                    'x1w': ps['x1w'],
                    'tr_bob': _param_merge(ps, qs)[0],
                    'tr_k': _param_merge(ps, qs)[1],
                    'tr_last': _param_merge(ps, qs)[3],
                    'tr_sum': _param_merge(ps, qs)[2],
                }

                if all(predicted[k] == gt[k] for k in gt): fo += 1
                else: ff += 1

print(f"Forest concat: {fo} ok, {ff} fails")
print("★★★ FOREST CONCAT CORRECT ★★★" if ff == 0 else f"FAILED: {ff}")

print()
print("="*70)
print("TEST 2: Wrapping correctness (forest → primitive)")
print("="*70)

wo = 0; wf = 0
for n_total in range(2, N_P + 1):
    for s in generate_dyck(n_total):
        depth = 0; inner_end = 0
        for i, ch in enumerate(s):
            if ch == '(': depth += 1
            else: depth -= 1
            if depth == 0: inner_end = i; break
        if inner_end != len(s) - 1:
            continue
        inner = s[1:inner_end]
        actual_pw = wrapped_state_from_word(s)

        children = []
        child_start = 0; d = 0
        for j, ch in enumerate(inner):
            if ch == '(':
                if d == 0: child_start = j
                d += 1
            else:
                d -= 1
                if d == 0:
                    child_word = inner[child_start:j+1]
                    children.append(wrapped_state_from_word(child_word))

        forest = {
            'sum_Xw': children[0]['sum_Xw'], 'x1w': children[0]['x1w'],
            'tr_bob': children[0]['tr_bob'], 'tr_k': children[0]['tr_k'],
            'tr_last': children[0]['tr_last'], 'tr_sum': children[0]['tr_sum'],
        }
        for c in children[1:]:
            forest = param_concat(forest, c)

        forest_n = sum(c['n'] for c in children)
        predicted = apply_wrapping(forest, forest_n)

        fields = ['bobw', 'kw', 'sum_Xw', 'x1w', 'tr_bob', 'tr_k', 'tr_sum', 'tr_last', 'n']
        match = all(predicted[f] == actual_pw[f] for f in fields)
        if match: wo += 1
        else:
            wf += 1
            if wf <= 3:
                print(f"\n  FAIL: {s}")
                print(f"  Forest: {forest}")
                for f in fields:
                    if predicted[f] != actual_pw[f]:
                        print(f"    {f}: pred={predicted[f]}, act={actual_pw[f]}")

print(f"Wrapping: {wo} ok, {wf} fails")
print("★★★ WRAPPING CORRECT ★★★" if wf == 0 else f"Wrapping: {wf} FAILS")

print()
print("="*70)
print("State cardinality")
print("="*70)
all_states = {}
for n in range(1, N_P + 1):
    for s in generate_dyck(n):
        all_states[s] = wrapped_state_from_word(s)

for n in range(1, 9):
    tn = [t for s, t in all_states.items() if t['n'] == n]
    distinct = set((t['bobw'], t['kw'], t['sum_Xw'], t['x1w'],
                     t['tr_bob'], t['tr_k'], t['tr_last'], t['tr_sum']) for t in tn)
    print(f"  n={n}: Catalan={len(tn):4d}, distinct states={len(distinct):3d}")
