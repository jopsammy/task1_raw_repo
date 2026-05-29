"""
Bounce path analysis v2: verify additivity without sub-word extraction.
Use L(i) sequence and geometry to verify area/bob decomposition.

Key facts:
  area = sum_{i=1..n} (P(i) - 2i) where P(i)=1-based position of i-th ')'
  bob = sum_{j=1}^{k-1} (n - l_j) where l_j are jump points
  
Bounce path diagonal points: [n, p1, p2, ..., 0]
Segment lengths: x_j = diag[j] - diag[j+1]
These segment lengths = x_seq elements.
"""
import sys

MOD = 998244353


def generate_dyck(n):
    words = []
    def bt(s, op, cl):
        if cl > op or op > n:
            return
        if len(s) == 2 * n:
            if op == n and cl == n:
                words.append(s)
            return
        bt(s + '(', op + 1, cl)
        bt(s + ')', op, cl + 1)
    bt('', 0, 0)
    return words


def compute_L_seq(s):
    """L(i) = P(i) - i, where P(i) is 1-based position of i-th ')'"""
    n = len(s) // 2
    L = [0] * n
    rc = 0
    for idx, ch in enumerate(s):
        if ch == ')':
            L[rc] = (idx + 1) - (rc + 1)
            rc += 1
    return L


def area_of(s):
    n = len(s) // 2
    rc = 0
    area = 0
    for idx, ch in enumerate(s):
        if ch == ')':
            rc += 1
            area += (idx + 1) - 2 * rc
    return area


def x_seq_and_bob(s):
    n = len(s) // 2
    h = [0] * (2 * n + 1)
    for i in range(2 * n):
        h[i + 1] = h[i] + (1 if s[i] == '(' else -1)
    l = 0
    X = []
    while l < n:
        pos = 2 * l
        best_x = 0
        t = 1
        while pos + t <= 2 * n:
            if h[pos + t] == t:
                best_x = t
                t += 1
            elif h[pos + t] > t:
                t += 1
            else:
                break
        if best_x == 0:
            best_x = 1
        X.append(best_x)
        l += best_x
    bob = sum(j * X[j] for j in range(len(X)))
    return X, bob


def compute_vertical_steps(s):
    """vertical_step_x[y] = x coord of N step at height y (for y=0..n-1)"""
    n = len(s) // 2
    vs = {}
    x, y = 0, 0
    for ch in s:
        if ch == '(':
            vs[y] = x
            y += 1
        else:
            x += 1
    return vs


def bounce_decompose(s):
    """Returns: diag_pts, seg_lengths, (si, ei) for each segment"""
    n = len(s) // 2
    vs = compute_vertical_steps(s)
    diag_pts = [n]
    d = n
    while d > 0:
        hit_x = vs[d - 1]
        d = hit_x
        diag_pts.append(d)
    seg_lengths = [diag_pts[i] - diag_pts[i + 1] for i in range(len(diag_pts) - 1)]
    segments = [(diag_pts[i + 1], diag_pts[i], seg_lengths[i]) for i in range(len(seg_lengths))]
    return diag_pts, seg_lengths, segments


def bounce_area_verify(max_n=8):
    """
    Approach: use bounce path geometry to compute segment area.
    
    For a Dyck path D, the i-th bounce segment is a path from (d_{i+1}, d_{i+1})
    to (d_i, d_i) staying above the diagonal y=x.
    
    This is VERTICALLY SHIFTED by d_{i+1} from a canonical Dyck path of size x_i.
    
    For any point on the canonical path at (a, h(a)), the shifted point is at
    (a + d_{i+1}, h(a) + d_{i+1}). The area contribution (squares between path
    and diagonal) for the canonical cell at (a, y) becomes:
      (y+d_{i+1}) - (a+d_{i+1}) = y - a  ← same as canonical!
    
    Wait, that means the shift doesn't change area at all for cells above the diagonal?
    No - the DIAGONAL is at y=x. After shifting by d, the path cell at (a+d, y+d)
    has area contribution (y+d) - (a+d) = y-a, same as before. But the paths are
    geometrically different because of the segment boundaries.
    
    Actually, let me reconsider. Each segment is bounded by diagonal points.
    The segment path lies between y = d_{i+1} and y = d_i.
    
    The area of the segment = sum_{(x,y) in segment, y>x} 1
    For a canonical Dyck path C of size x_i, area = sum_{(a,b) in C, b>a} 1
    For the shifted segment: we map (a+offset, b+offset) where offset = d_{i+1}
    area = sum_{(a,b) in C, b+offset > a+offset} 1 = area(C). Same!
    
    But total area of D = sum_i area(segment_i)? Let's verify numerically.
    """
    print(f"=== Bounce area additivity (geometric) for n <= {max_n} ===\n")

    for n in range(1, max_n + 1):
        words = generate_dyck(n)
        errors = 0

        for s in words:
            total_area = area_of(s)
            diag_pts, seg_lengths, segments = bounce_decompose(s)
            X, bob = x_seq_and_bob(s)

            # First check: bounce path segment lengths == X
            if seg_lengths != X:
                print(f"  SEG_X mismatch: {s}")
                continue

            # Verify bob additivity (should be trivial since it's just
            # sum of (j-1)*x_j = sum over segments of prev_sum*seg_len)
            bob_from_segs = 0
            prev_sum = 0
            for i, (si, ei, length) in enumerate(segments):
                bob_from_segs += prev_sum * length
                prev_sum += length
            if bob_from_segs != bob:
                print(f"  BOB mismatch: {s}: {bob_from_segs} vs {bob}")
                errors += 1
                continue

            # Now verify area decomposition: for each segment, compute its
            # area contribution from the original path geometry.
            #
            # The segment covers y-range [si, ei). The N steps in this range
            # are at heights si..ei-1. The E steps are paired with these N steps.
            #
            # For the segment, we can compute its area contribution as:
            #   area_i = sum over cells (x,y) where:
            #     - si <= y < ei (within segment height)
            #     - y > x (above diagonal)
            #     - cell is below the Dyck path
            #
            # Actually, we can compute the segment area from the Dyck path by
            # looking at the subpath between x=d_{i+1} and x=d_i.

            # The Dyck path goes from (0,0) to (n,n). The bounce segment i
            # corresponds to the portion of the path where x is between 
            # d_{i+1} and d_i.
            
            # Alternative: compute segment area using the L(i) sequence.
            # For position j (1-indexed), area contribution = L(j) - j.
            # The bounce segment that position j belongs to is determined by:
            # which segment's height range contains the matching '(' height.
            # Actually, position j has a matching '(' at height h, where 
            # h is determined by the Dyck word structure.
            # 
            # Even simpler: the x-coordinate of the j-th ')' is j (by definition
            # of the Dyck path). The matching '(' is at height h where the path
            # makes its N step. In the bounce decomposition, N steps at heights
            # si..ei-1 belong to segment i.
            #
            # So the j-th ')' belongs to segment i if its matching '(' is at
            # height h where si <= h < ei.

            # Now verify: the segment area can be computed as the weighted
            # sum of area contributions from each ')' belonging to the segment.

            # area = sum_j (P(j) - 2j) = sum_j [L(j) - j]  (since L(j) = P(j)-j)
            # Let's group by bounce segment.

            # Build mapping: for each height h (0..n-1), which bounce segment
            # does its N step belong to?
            n_height_seg = {}
            for i, (si, ei, length) in enumerate(segments):
                for h in range(si, ei):
                    n_height_seg[h] = i

            # For each ')', determine its matching '(' height.
            # In a Dyck word, the j-th ')' matches with the '(' that makes
            # the height return to the right value.
            # Compute matching heights for each ')' using a stack.
            matching_heights = {}
            stack = []  # (position, height)
            y = 0
            rc = 0
            for idx, ch in enumerate(s):
                if ch == '(':
                    stack.append((idx, y))
                    y += 1
                else:
                    rc += 1
                    open_pos, open_h = stack.pop()
                    matching_heights[rc - 1] = open_h  # rc-1 = 0-indexed ')'

            # Now compute segment area contributions
            seg_areas = [0] * len(segments)
            for j in range(n):
                seg_idx = n_height_seg[matching_heights[j]]
                seg_areas[seg_idx] += (2*(j+1)) - 1  # Hmm, this is wrong.
                # Actually, area contribution from j-th ')' = P(j) - 2j - 1? 
                # No: area = sum_j (P(j) - 2j - 1)? Let me recheck.
            
            # Let me just directly verify: total_area = sum_i area_i ?
            # by computing area_i from the geometry directly.

            # For each bounce segment, compute its area as:
            # area_i = number of whole squares between diagonal and Dyck path
            # that are within the x-range [d_{i+1}, d_i].
            
            # The Dyck path at x-coordinate x (integer, 0..n) has y = D(x)
            # where D(x) is the height. D is monotone, D(0)=0, D(n)=n.
            # area = sum_{x=0}^{n-1} (D(x) - (x+1))? No.
            # Area = number of integer points (p,q) with 0<=q<D(p) and q>=p+1
            # Actually area = sum_{x=1}^{n} max(0, D(x-1) - x)? This is getting messy.

            # Let me use a different approach: directly compute segment area
            # from the sub-Dyck path extracted geometrically.

            # Build the full Dyck path as (x, y) coordinates
            path = [(0, 0)]
            x, y = 0, 0
            for ch in s:
                if ch == '(':
                    y += 1
                else:
                    x += 1
                path.append((x, y))

            # For each bounce segment, it's the portion of the path between
            # x=d_{i+1} and x=d_i, shifted. But we need to close the segment
            # at both ends - the segment starts and ends on the diagonal.
            
            # Actually, the bounce segment IS the portion of the full Dyck path
            # between x-coordinates d_{i+1} and d_i, with the understanding
            # that it starts at diagonal point (d_{i+1}, d_{i+1}) and ends at
            # (d_i, d_i). The full path naturally does this because the bounce
            # points are on the diagonal.

        if errors == 0 and n <= 2:
            print(f"n={n}: ALL OK (bob verified)")

    # Let me take a simpler approach - verify using brute force per-segment
    # by checking if the total F[n] can be expressed as sum over bounce
    # segment compositions.

    print(f"\n=== Key verification: area decomposition feasibility ===\n")
    
    for n in range(1, max_n + 1):
        words = generate_dyck(n)
        # Collect all distinct (X, area) pairs
        X_area_pairs = {}
        for s in words:
            X, bob = x_seq_and_bob(s)
            area = area_of(s)
            key = tuple(X)
            if key not in X_area_pairs:
                X_area_pairs[key] = []
            X_area_pairs[key].append(area)
        
        # Check: for each X sequence, is area uniquely determined?
        ambiguous = 0
        for X, areas in X_area_pairs.items():
            if len(set(areas)) > 1:
                ambiguous += 1
                if n <= 4:
                    print(f"  X={list(X)}: areas={sorted(set(areas))}")
        
        if ambiguous > 0:
            print(f"n={n}: {ambiguous} X-sequences have multiple area values")
            print(f"  → area is NOT uniquely determined by X alone")
            print(f"  → DP must track segment internal structure, not just lengths")
        else:
            print(f"n={n}: area IS uniquely determined by X (this would be a breakthrough!)")

    # Let's also check: for fixed X[0], what's the relationship between
    # the rest of the bounce path and the remaining Dyck word?
    print(f"\n=== Bounce-first decomposition analysis ===\n")
    
    for n in range(1, 5):
        words = generate_dyck(n)
        for s in words:
            X, bob = x_seq_and_bob(s)
            area = area_of(s)
            diag_pts, seg_lengths, segments = bounce_decompose(s)
            
            # First segment: size x1 = X[0], starts at (n,n), ends at (n-x1, n-x1)
            # The first segment corresponds to the sub-Dyck path from (n-x1, n-x1)
            # to (n, n), staying above the diagonal.
            # Shifted down: this is a Dyck path of size x1.
            # The remaining path from (0,0) to (n-x1, n-x1) is also a Dyck path.
            
            # The bounce decomposition naturally gives us:
            # D = [seg_0] concat [seg_1] concat ... concat [seg_{k-1}]
            # where each seg_i is a Dyck path of size x_i, shifted appropriately.
            # Concatenation here means: lay them out along the diagonal.
            
            # Now, for DP purposes, the key question is:
            # Can we compute F[n] by iterating over all possible first bounce
            # segments (size x1) and remaining Dyck paths (size n-x1)?
            
            # The first segment: a Dyck path of size x1, shifted to start at (n-x1, n-x1).
            # Its area contribution = area(unshifted_sub_dyck) + (n-x1) * x1??
            # Actually: if the canonical Dyck path has N steps at heights 0..x1-1,
            # the shifted version has N steps at heights (n-x1)..(n-1).
            # Area of shifted = area(canonical) + shift_contribution
            
            # Let's compute the shift contribution. For a cell at (a, h(a)) in the
            # canonical path (below path, above diagonal), after shifting by offset o:
            # cell becomes (a+o, h(a)+o). Its distance to diagonal:
            # (h(a)+o) - (a+o) = h(a) - a. Same as before.
            # So shift doesn't change per-cell area.
            # BUT: the canonical path's cells are counted differently after shift.
            # Wait, no - if we shift the ENTIRE subpath, the area is exactly the same.
            
            # Hmm, but then how can the total area differ from sum of segment areas?
            # Because segment boundaries might create additional area!
            # The segments are separated by diagonal points. Between segments,
            # there might be area that's counted by the global area but not by
            # segment areas separately. Or vice versa.
            
            # Let me just test: for a specific word, compute each segment's 
            # canonical Dyck word by "compressing" the subpath.
            
            pass
        
    print("\n=== Summary ===")
    print("TODO after resolving sub-word extraction")


if __name__ == '__main__':
    bounce_area_verify(6)
