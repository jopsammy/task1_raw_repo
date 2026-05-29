import sys, subprocess
sys.path.insert(0, '.')
from verify_bergeron import brute_force_Fn

def run_v14(N, a, b):
    p = subprocess.run(['./solution_v14.exe'],
                       input=f'{N} {a} {b}',
                       capture_output=True, text=True)
    return [int(x) for x in p.stdout.strip().split()]

for a, b in [(2, 3), (5, 7), (3, 2), (1, 1)]:
    v14 = run_v14(8, a, b)
    bf = brute_force_Fn(8, a, b)
    ok = all(v14[i] == bf[i] for i in range(8))
    print(f'a={a}, b={b}: {"ALL OK" if ok else "FAIL"}')
    if not ok:
        for i in range(8):
            if v14[i] != bf[i]:
                print(f'  n={i+1}: v14={v14[i]} bf={bf[i]}')

for a, b in [(7, 11), (123, 456)]:
    v14 = run_v14(8, a, b)
    bf = brute_force_Fn(8, a, b)
    ok = all(v14[i] == bf[i] for i in range(8))
    print(f'a={a}, b={b}: {"ALL OK" if ok else "FAIL"}')
    if not ok:
        for i in range(8):
            if v14[i] != bf[i]:
                print(f'  n={i+1}: v14={v14[i]} bf={bf[i]}')
