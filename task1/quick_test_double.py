"""
Quick verification: does double wrapping preserve bob and k for specific words?
"""
from verify_bf import generate_dyck, x_seq_and_bob

test_cases = [
    "()",
    "()()",
    "(())",
    "()()()",
    "()(())",
    "(())()",
    "(()())",
    "((()))",
    "()()()()",
    "()()(())",
    "()(())()",
    "(())()()",
    "()(()())",
    "(()())()",
    "(()(()))",
    "((()))()",
    "((())())",
    "((()()))",
    "(((())))",
    "()()()()()",
    "()()()(())",
    "()()(())()",
    "()(())()()",
    "(())()()()",
    "()()()()()(())()",  # This was an UNEXPECTED case
]

print("Checking bob/k preservation under double wrapping:")
print("A                 | bob(P) k(P) | bob(DP) k(DP) | match?")
print("-" * 70)

all_ok = True
for a in test_cases:
    P = '(' + a + ')'
    DP = '(' + P + ')'
    
    Xp, bobp = x_seq_and_bob(P)
    kp = len(Xp)
    
    Xdp, bobdp = x_seq_and_bob(DP)
    kdp = len(Xdp)
    
    bob_ok = bobp == bobdp
    k_ok = kp == kdp
    
    if not bob_ok or not k_ok:
        print(f"{a:17s} | bob={bobp:2d} k={kp} X={str(Xp):20s} | bob={bobdp:2d} k={kdp} X={str(Xdp):20s} | {'  ✗✗✗'}")
        all_ok = False
    else:
        if Xp != Xdp:
            print(f"{a:17s} | bob={bobp:2d} k={kp} X={str(Xp):20s} | bob={bobdp:2d} k={kdp} X={str(Xdp):20s} | ✓ (X changed but bob/k preserved)")

if all_ok:
    print("\nALL CASES: bob and k preserved ✓")

print("\n\nLooking at the X_seq change pattern:")
for a in test_cases:
    P = '(' + a + ')'
    DP = '(' + P + ')'
    Xp, _, _ = x_seq_and_bob(P)
    Xdp, _, _ = x_seq_and_bob(DP)
    if Xp != Xdp:
        print(f"  A={a}")
        print(f"    X(P)= {Xp}")
        print(f"    X(DP)={Xdp}")
        print(f"    diff: +{Xdp[0]-Xp[0]} on first, then: {'merged' if len(Xdp)<len(Xp) else 'same length'}")
