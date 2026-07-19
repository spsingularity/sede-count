"""
Section 2.5 of Paper III: for alpha < d the Ryu-Takayanagi minimum cut is NOT a surface.

Lattice ball radius R.  All-pairs bonds w_ij = r_ij^-alpha (UNBUDGETED here on purpose --
this is the illegitimate network whose pathology motivates the leg budget of Sec. 2.1).
Boundary legs of the upper cap are tied to a source, the lower cap to a sink, both at
infinite capacity, so every cut passes through the bulk.

Two normalisation-free diagnostics:
  thickness : weighted RMS midpoint height of the severed bonds, IN LATTICE UNITS.
              R-independent  -> a membrane.   proportional to R -> no membrane.
  shellfrac : fraction of the source side of the min cut that is boundary sites.
              -> 1.000 means the cut has degenerated onto the boundary shell.
"""
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow

SCALE = 200
NEIGH = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]


def ball(R):
    Ri = int(np.floor(R))
    return np.array([(x, y, z)
                     for x in range(-Ri, Ri+1)
                     for y in range(-Ri, Ri+1)
                     for z in range(-Ri, Ri+1)
                     if x*x + y*y + z*z <= R*R])


def run(R, alpha):
    pts = ball(R); N = len(pts)
    inside = set(map(tuple, pts))
    bnd = np.array([i for i, (x, y, z) in enumerate(pts)
                    if any((x+a, y+b, z+c) not in inside for a, b, c in NEIGH)])
    A = bnd[pts[bnd, 2] > 0]
    B = bnd[pts[bnd, 2] < 0]

    D = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)
    np.fill_diagonal(D, np.inf)
    W = np.rint(SCALE * D**(-alpha)).astype(np.int64)

    INF, S, T = 10**9, N, N+1
    C = np.zeros((N+2, N+2), dtype=np.int64)
    C[:N, :N] = W
    C[S, A] = INF
    C[B, T] = INF
    assert C.max() <= np.iinfo(np.int32).max
    C32 = C.astype(np.int32)

    res = maximum_flow(csr_matrix(C32), S, T)
    resid = C32 - res.flow.toarray()

    seen = np.zeros(N+2, bool); seen[S] = True; stack = [S]
    while stack:
        u = stack.pop()
        for v in np.nonzero(resid[u] > 0)[0]:
            if not seen[v]:
                seen[v] = True; stack.append(v)
    Sset = seen[:N]

    iS, jT = np.nonzero(Sset)[0], np.nonzero(~Sset)[0]
    sub = W[np.ix_(iS, jT)]
    ii, jj = np.nonzero(sub > 0)
    w = sub[ii, jj].astype(float)
    zmid = 0.5*(pts[iS[ii], 2] + pts[jT[jj], 2])

    thickness = np.sqrt((w*zmid**2).sum()/w.sum())          # lattice units
    shellfrac = len(set(iS.tolist()) & set(bnd.tolist()))/max(Sset.sum(), 1)
    return dict(R=R, N=N, alpha=alpha, mincut=int(res.flow_value),
                thickness=thickness, shellfrac=shellfrac, Sfrac=Sset.sum()/N)


def check(Rs=(3, 4, 5, 6), alphas=(0.5, 1.0, 2.0, 3.0, 4.0, 6.0), verbose=True):
    tab = {a: [run(R, a) for R in Rs] for a in alphas}
    if verbose:
        print("thickness of the severed-bond set, in LATTICE UNITS")
        print(f"{'alpha':>6} " + " ".join(f"{'R='+str(R):>8}" for R in Rs) + "   shellfrac(max R)")
        for a in alphas:
            t = [r['thickness'] for r in tab[a]]
            print(f"{a:6.1f} " + " ".join(f"{x:8.3f}" for x in t) + f"   {tab[a][-1]['shellfrac']:.3f}")

    t1 = [r['thickness'] for r in tab[1.0]]
    t6 = [r['thickness'] for r in tab[6.0]]
    assert t1[-1]/t1[0] > 2.0, "alpha=1 thickness should grow ~ R"
    assert np.std(t6) < 0.01, "alpha=6 thickness should be R-independent"
    # for alpha <= d the cut degenerates onto the boundary shell (exactly 1.000 for R >= 4;
    # R = 3 shows a small lattice artefact at alpha = 2)
    for a in (0.5, 1.0, 2.0):
        assert all(r['shellfrac'] > 0.97 for r in tab[a]), f"alpha={a} cut not shell-degenerate"
        assert all(abs(r['shellfrac'] - 1.0) < 1e-9 for r in tab[a] if r['R'] >= 4), \
            f"alpha={a} cut not exactly shell-degenerate at R >= 4"
    assert tab[6.0][-1]['shellfrac'] < 0.5, "alpha=6 cut should be a bulk membrane"
    return tab


if __name__ == "__main__":
    check()
