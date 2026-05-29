import subprocess, sys, random
sys.path.insert(0, '.')
from verify_bergeron import brute_force_Fn, compute_Fn_from_bergeron

MOD = 998244353

def run_v14(N, a, b):
    p = subprocess.run(['./solution_v14.exe'],
                       input=f'{N} {a} {b}',
                       capture_output=True, text=True, timeout=30)
    return [int(x) for x in p.stdout.strip().split()]

def test_bf_small():
    """Test v14 vs brute force for n<=8 with random params"""
    print("=== BF Test (n<=8) vs random params ===")
    random.seed(42)
    for test_id in range(50):
        a = random.randint(1, MOD - 1)
        b = random.randint(1, MOD - 1)
        v14 = run_v14(8, a, b)
        bf = brute_force_Fn(8, a, b)
        ok = all(v14[i] == bf[i] for i in range(8))
        if not ok:
            print(f"FAIL test {test_id}: a={a}, b={b}")
            for i in range(8):
                if v14[i] != bf[i]:
                    print(f"  n={i+1}: v14={v14[i]} bf={bf[i]}")
        else:
            print(f"  test {test_id}: a={a%1000}..., b={b%1000}... OK")
    print()

def test_bergeron_medium():
    """Test v14 vs Python Bergeron GH reference for n<=50"""
    print("=== Bergeron Ref Test (n<=50) vs random params ===")
    random.seed(123)
    for test_id in range(30):
        a = random.randint(1, MOD - 1)
        b = random.randint(1, MOD - 1)
        N = random.randint(5, 50)
        try:
            v14 = run_v14(N, a, b)
            berg = compute_Fn_from_bergeron(N, a, b)
            ok = all(v14[i] == berg[i] for i in range(N))
            if not ok:
                print(f"FAIL test {test_id}: N={N}, a={a%1000}..., b={b%1000}...")
                for i in range(N):
                    if v14[i] != berg[i]:
                        print(f"  n={i+1}: v14={v14[i]} berg={berg[i]}")
                return
            else:
                print(f"  test {test_id}: N={N}, a={a%1000}..., b={b%1000}... OK")
        except Exception as e:
            print(f"  test {test_id}: N={N}, a={a}, b={b} ERROR: {e}")
    print()

def test_specific_params():
    """Test specific problematic parameter combinations"""
    print("=== Specific Param Tests ===")
    params = [
        (1, 1), (1, 2), (1, 3), (1, 7), (1, 123),
        (2, 1), (2, 2), (2, 3), (2, 5), (2, 7),
        (3, 1), (3, 2), (3, 3), (3, 5), (3, 7),
        (5, 5), (5, 7), (7, 7), (11, 13),
        (123, 456), (998244352, 998244352),
        (998244352, 1), (1, 998244352),
        (MOD-1, MOD-1), (MOD-2, MOD-2),
    ]
    for a, b in params:
        try:
            v14 = run_v14(10, a, b)
            berg = compute_Fn_from_bergeron(10, a, b)
            ok = all(v14[i] == berg[i] for i in range(10))
            status = "OK" if ok else "FAIL"
            print(f"  a={a%10000}..., b={b%10000}... (n<=10): {status}")
            if not ok:
                for i in range(10):
                    if v14[i] != berg[i]:
                        print(f"    n={i+1}: v14={v14[i]} berg={berg[i]}")
        except Exception as e:
            print(f"  a={a}, b={b}: ERROR {e}")
    print()

def test_edge_values():
    """Test with parameters that are powers of the primitive root"""
    print("=== Edge Value Tests ===")
    for r in range(1, 11):
        a = pow(3, r, MOD)
        b = pow(3, r + 5, MOD)
        try:
            v14 = run_v14(15, a, b)
            berg = compute_Fn_from_bergeron(15, a, b)
            ok = all(v14[i] == berg[i] for i in range(15))
            status = "OK" if ok else "FAIL"
            print(f"  a=3^{r}, b=3^{r+5} (n<=15): {status}")
            if not ok:
                for i in range(15):
                    if v14[i] != berg[i]:
                        print(f"    n={i+1}: v14={v14[i]} berg={berg[i]}")
        except Exception as e:
            print(f"  a=3^{r}, b=3^{r+5}: ERROR {e}")
    print()

if __name__ == '__main__':
    test_bf_small()
    test_bergeron_medium()
    test_specific_params()
    test_edge_values()
