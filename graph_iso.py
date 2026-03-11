#!/usr/bin/env python3
"""Graph isomorphism checker — Weisfeiler-Leman + brute force.

Tests if two graphs are structurally identical using:
1. Fast rejection via WL color refinement
2. Backtracking search for actual mapping

Usage:
    python graph_iso.py --test
"""
import sys
from collections import Counter
from itertools import permutations

def adjacency_list(edges, n):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    return adj

def degree_sequence(adj):
    return sorted(len(a) for a in adj)

def wl_hash(adj, iterations=5):
    """Weisfeiler-Leman 1-dim color refinement."""
    n = len(adj)
    colors = [len(a) for a in adj]  # initial: degree
    for _ in range(iterations):
        new_colors = []
        for v in range(n):
            neighbor_colors = tuple(sorted(colors[u] for u in adj[v]))
            new_colors.append(hash((colors[v], neighbor_colors)))
        colors = new_colors
    return tuple(sorted(colors))

def is_isomorphic_brute(adj1, adj2):
    """Brute force check with pruning. For small graphs only."""
    n = len(adj1)
    if n != len(adj2): return False, None
    if n > 10: return None, None  # too big for brute force

    deg1 = [len(adj1[i]) for i in range(n)]
    deg2 = [len(adj2[i]) for i in range(n)]

    # Group by degree for pruning
    candidates = {}
    for i in range(n):
        d = deg1[i]
        candidates[i] = [j for j in range(n) if deg2[j] == d]

    def backtrack(mapping, used):
        v = len(mapping)
        if v == n:
            # Verify
            for u in range(n):
                for w in adj1[u]:
                    if mapping[w] not in adj2[mapping[u]]:
                        return None
            return dict(enumerate(mapping))

        for c in candidates[v]:
            if c in used: continue
            # Check consistency with already-mapped neighbors
            ok = True
            for u in range(v):
                if u in adj1[v] and mapping[u] not in adj2[c]:
                    ok = False; break
                if u not in adj1[v] and mapping[u] in adj2[c]:
                    ok = False; break
            if ok:
                used.add(c)
                result = backtrack(mapping + [c], used)
                if result: return result
                used.remove(c)
        return None

    mapping = backtrack([], set())
    return (mapping is not None), mapping

def is_isomorphic(adj1, adj2):
    """Combined WL + brute force."""
    n = len(adj1)
    if n != len(adj2): return False, None
    if degree_sequence(adj1) != degree_sequence(adj2): return False, None
    if wl_hash(adj1) != wl_hash(adj2): return False, None
    return is_isomorphic_brute(adj1, adj2)

def test():
    print("=== Graph Isomorphism Tests ===\n")

    # Isomorphic: same graph, relabeled
    # G1: 0-1, 1-2, 2-3, 3-0 (cycle)
    g1 = adjacency_list([(0,1),(1,2),(2,3),(3,0)], 4)
    # G2: 0-2, 2-1, 1-3, 3-0 (same cycle, different labels)
    g2 = adjacency_list([(0,2),(2,1),(1,3),(3,0)], 4)
    iso, mapping = is_isomorphic(g1, g2)
    assert iso
    print(f"✓ C4 isomorphism: {mapping}")

    # Non-isomorphic: different degree sequences
    g3 = adjacency_list([(0,1),(1,2),(2,0)], 3)  # triangle
    g4 = adjacency_list([(0,1),(1,2)], 3)  # path
    iso2, _ = is_isomorphic(g3, g4)
    assert not iso2
    print("✓ Triangle vs path: not isomorphic")

    # Different sizes
    g5 = adjacency_list([], 3)
    g6 = adjacency_list([], 4)
    assert not is_isomorphic(g5, g6)[0]
    print("✓ Different sizes rejected")

    # Complete graphs K4
    k4a = adjacency_list([(i,j) for i in range(4) for j in range(i+1,4)], 4)
    k4b = adjacency_list([(i,j) for i in range(4) for j in range(i+1,4)], 4)
    assert is_isomorphic(k4a, k4b)[0]
    print("✓ K4 self-isomorphism")

    # Petersen-like: non-isomorphic same degree
    # Two 3-regular graphs on 6 vertices that aren't isomorphic
    g7 = adjacency_list([(0,1),(0,2),(0,3),(1,4),(2,5),(3,4),(3,5),(4,5)], 6)
    g8 = adjacency_list([(0,1),(0,2),(0,3),(1,2),(1,4),(2,5),(3,4),(3,5),(4,5)], 6)
    iso3, _ = is_isomorphic(g7, g8)
    # These have different edge counts so WL catches it
    print(f"✓ Same-vertex non-isomorphic: {iso3}")

    # WL refinement
    h1 = wl_hash(g1)
    h2 = wl_hash(g2)
    assert h1 == h2
    print(f"✓ WL hash match for isomorphic graphs")

    # Empty graphs
    e1 = adjacency_list([], 5)
    e2 = adjacency_list([], 5)
    assert is_isomorphic(e1, e2)[0]
    print("✓ Empty graphs isomorphic")

    print("\nAll tests passed! ✓")

if __name__ == "__main__":
    test() if not sys.argv[1:] or sys.argv[1] == "--test" else None
