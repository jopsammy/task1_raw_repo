"""
Find all a values where the q-factorial approach breaks.
"""
MOD = 998244353

def modpow(a, e):
    r = 1
    while e:
        if e & 1: r = r * a % MOD
        a = a * a % MOD
        e >>= 1
    return r

def find_order(a):
    """Find multiplicative order of a mod MOD"""
    if a == 0: return 0
    # Order must divide MOD-1 = 998244352 = 119 * 2^23
    # Check all divisors up to 2*N+2 where N=5000
    N2 = 10004  # 2*N + some margin
    val = a
    for d in range(1, N2 + 1):
        if val == 1:
            return d
        val = val * a % MOD
    return N2 + 1  # order > N2

def find_first_one(a, limit):
    """Find first i >= 1 where a^i == 1 mod MOD, or 0 if > limit"""
    val = a % MOD
    for i in range(1, limit + 1):
        if val == 1:
            return i
        val = val * a % MOD
    return 0

# Test with specific problematic values
print("=== Testing problematic a values ===")
N = 5000
problematic = []
for a_test in [998244352, 2, 3, 5, 7, 123, 456, MOD//2]:
    first = find_first_one(a_test, 2*N+5)
    order = find_order(a_test)
    print(f"a={a_test%10000}... first_one={first}, order={order}")

# Count how many a have small order
print("\n=== Distribution of orders ===")
# Sample random a values
import random
random.seed(0)
orders = {}
for _ in range(1000):
    a = random.randint(1, MOD-1)
    first = find_first_one(a, 2*N+5)
    if first == 0:
        orders['>10004'] = orders.get('>10004', 0) + 1
    else:
        key = f"={first}"
        orders[key] = orders.get(key, 0) + 1

for k in sorted(orders.keys(), key=lambda x: (0 if x.startswith('>') else int(x.split('=')[1]))):
    print(f"  order {k}: {orders[k]} samples")
