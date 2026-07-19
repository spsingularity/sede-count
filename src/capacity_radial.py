"""
Section 2.3 of Paper III: the bond-cut capacity of a leg-budgeted long-range network.

Spherically-symmetric reduction using the EXACT angular average

    <|x-y|^-a>_angles = [ (s+s')^(2-a) - max(|s-s'|, acut)^(2-a) ] / (2 s s' (2-a))
    (log form at a = 2; at a = 1 this is Newton's theorem, 1/max(s,s'), with acut -> 0)

so the ambient radius L can be pushed far beyond rho.  A symmetric Sinkhorn scaling
imposes the per-site leg budget  sum_j w_ij = kappa  exactly.

Result:  s(rho) = C(rho)/N_in  ->  kappa   for alpha < d   (volume law, saturated)
                              ->  ~ 1/rho  for alpha > d   (area law)
with the crossover at alpha = d = 3.
"""
import numpy as np


def kernel(s, a, acut=1.0):
    S, SP = np.meshgrid(s, s, indexing='ij')
    lo = np.maximum(np.abs(S - SP), acut)
    hi = S + SP
    ok = hi > lo
    lo = np.where(ok, lo, 1.0); hi = np.where(ok, hi, 1.0)
    if abs(a - 2.0) < 1e-12:
        A = np.log(hi/lo)/(2*S*SP)
    else:
        A = (hi**(2-a) - lo**(2-a))/(2*S*SP*(2-a))
    return np.where(ok, A, 0.0)


def budgeted_network(alpha, L=200.0, M=600, kappa=1.0, acut=1.0, tol=1e-12, iters=5000):
    ds = L/M
    s = (np.arange(M) + 0.5)*ds
    n = 4*np.pi*s**2*ds                      # sites per shell (unit number density)
    A = np.outer(n, n)*kernel(s, alpha, acut)
    d = np.ones(M)
    for _ in range(iters):                   # symmetric Sinkhorn, sqrt-damped
        t = A @ d
        dn = np.sqrt(d*(kappa*n)/t)
        if np.max(np.abs(dn - d)/d) < tol:
            d = dn; break
        d = dn
    W = A*d[:, None]*d[None, :]
    err = np.max(np.abs(W.sum(1)/(kappa*n) - 1))
    assert err < 1e-6, f"Sinkhorn did not converge: {err:.2e}"
    return s, n, W


def capacity(alpha, rhos=(2, 5, 10, 20, 40), **kw):
    s, n, W = budgeted_network(alpha, **kw)
    out = []
    for rho in rhos:
        i = s < rho
        C = W[np.ix_(i, ~i)].sum()
        out.append((rho, C, C/n[i].sum()))
    return out


def convergence(alpha, L=1500.0, M=3000, ratio=0.12, nrho=10):
    """Large-rho capacity curve; C/rho^2 separates the area phases:
       constant (clean area, alpha > d+1),  ~ln rho (marginal alpha = d+1),
       ~power   (alpha < d+1, still non-volume).  Ambient L pushed far past rho."""
    s, n, W = budgeted_network(alpha, L=L, M=M)
    rhos = np.geomspace(8.0, ratio*L, nrho)
    C = np.array([W[np.ix_(s < r, ~(s < r))].sum() for r in rhos])
    return rhos, C


def check(alphas=(1.0, 2.0, 2.5, 4.0, 6.0), verbose=True):
    rhos = (2, 5, 10, 20, 40)
    res = {}
    for a in alphas:
        o = capacity(a, rhos)
        rho = np.array([x[0] for x in o], float)
        C = np.array([x[1] for x in o], float)
        q = np.polyfit(np.log(rho), np.log(C), 1)[0]
        res[a] = dict(dens=[x[2] for x in o], q=q)
    if verbose:
        print("s(rho) = capacity per enclosed dof   (kappa = 1);   q from C ~ rho^q")
        print(f"{'alpha':>6} " + " ".join(f"{'rho='+str(r):>9}" for r in rhos) + f" {'q':>7}")
        for a in alphas:
            print(f"{a:6.1f} " + " ".join(f"{x:9.4f}" for x in res[a]['dens']) + f" {res[a]['q']:7.2f}")

    assert 2.90 <= res[1.0]['q'] <= 3.05, "alpha=1 must give the volume law q=3"
    assert res[1.0]['dens'][0] > 0.999,   "alpha=1 must saturate the leg budget"
    assert 1.95 <= res[6.0]['q'] <= 2.10, "alpha=6 must give the area law q=2"
    d = res[6.0]['dens']
    assert abs(d[-2]/d[-1] - 2.0) < 0.05, "alpha=6 density must halve when rho doubles"

    # --- alpha=4 = d+1 is the MARGINAL area case: C ~ rho^2 * ln(rho), not an intermediate
    #     exponent.  alpha=5 (> d+1) is the clean area law.  This resolves the slow alpha=4
    #     convergence in the L=200 table above and reinforces the binary dichotomy of 2.4.
    r4, C4 = convergence(4.0)
    r5, C5 = convergence(5.0)
    g4 = C4 / r4**2
    g5 = C5 / r5**2
    b4 = np.polyfit(np.log(r4), g4, 1)[0]          # C/rho^2 vs ln rho: slope > 0 => log
    q5 = np.polyfit(np.log(r5), np.log(C5), 1)[0]  # clean area exponent
    flat5 = (g5.max() - g5.min()) / g5.mean()      # flatness of C/rho^2 at alpha=5
    if verbose:
        print("\nlarge-rho area diagnostic  C(rho)/rho^2   (rho up to %.0f):" % r4[-1])
        print("  alpha=4 (=d+1): " + " ".join(f"{v:6.2f}" for v in g4) +
              f"   -> rises as {b4:.2f}*ln rho  => C ~ rho^2 ln rho (marginal area)")
        print("  alpha=5 (>d+1): " + " ".join(f"{v:6.2f}" for v in g5) +
              f"   -> flat to {flat5*100:.0f}%, q={q5:.3f}  => clean area law")
    assert b4 > 0.5,            "alpha=4 must show a positive C/rho^2 log-slope (marginal area)"
    assert flat5 < 0.12,        "alpha=5 C/rho^2 must be flat (clean area law)"
    assert 1.95 <= q5 <= 2.10,  "alpha=5 must give the area law q=2"
    res['conv'] = dict(b4=b4, q5=q5, flat5=flat5)
    return res


if __name__ == "__main__":
    check()
