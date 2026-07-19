"""
Section 5 of Paper III: the edge correction and the infrared cutoff.

At alpha = 1, Newton's theorem gives the exact angular average <1/|x-y|> = 1/max(s,s'),
so no short-distance regulator is needed and the deficit is a pure number:

    D(x) = 1 - s(rho)/kappa = c * x^(d-alpha),      x = rho/L,   c = 0.6730 at alpha=1

and the effective deformation is

    Delta(x) = 1 - x D'(x)/(1 - D(x)) = 1 - (d-a) c x^(d-a) / (1 - c x^(d-a)).

Delta = 1 EXACTLY in the limit L -> infinity.  Nothing in SEDE fixes L, so any finite L
is a fitted dark-sector parameter; the flat infinite spatial slice forces L -> infinity.
"""
import numpy as np

D_ALPHA = 1.0   # gravity


def solve_newton(M=3000, kappa=1.0, tol=1e-14, iters=20000):
    """Sinkhorn-budgeted radial network at alpha=1, ambient L=1, exact Newton kernel."""
    ds = 1.0/M
    s = (np.arange(M) + 0.5)*ds
    n = 4*np.pi*s**2*ds
    K = 1.0/np.maximum(s[:, None], s[None, :])
    A = np.outer(n, n)*K
    d = np.ones(M)
    for _ in range(iters):
        t = A @ d
        dn = np.sqrt(d*(kappa*n)/t)
        if np.max(np.abs(dn - d)/d) < tol:
            d = dn; break
        d = dn
    W = A*d[:, None]*d[None, :]
    assert np.abs(W.sum(1)/(kappa*n) - 1).max() < 1e-8
    return s, n, W


def deficit(s, n, W, x):
    i = s < x
    return 1.0 - W[np.ix_(i, ~i)].sum()/n[i].sum()


def delta_of_x(x, c=0.6730, alpha=1.0, d=3.0):
    """Eq. (5.2)."""
    D = c*x**(d - alpha)
    return 1.0 - (d - alpha)*D/(1.0 - D)


def check(verbose=True):
    s, n, W = solve_newton()
    xs = np.array([0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50])
    D = np.array([deficit(s, n, W, x) for x in xs])
    p = np.polyfit(np.log(xs[:5]), np.log(D[:5]), 1)[0]
    # c is the LIMIT of D/x^2 as x -> 0, not the intercept of a fit over finite x
    # (D/x^2 drifts upward with x; see the table).  Take the smallest x.
    c = float(D[0]/xs[0]**2)

    if verbose:
        print(f"{'x':>6} {'D(x)':>12} {'D/x^2':>9} {'Delta(x)':>10}")
        for x, dv in zip(xs, D):
            print(f"{x:6.2f} {dv:12.6f} {dv/x**2:9.4f} {1 - 2*dv/(1-dv):10.4f}")
        print(f"\nD(x) = c x^p:   p = {p:.4f}  (predicted d-alpha = 2)")
        print(f"c = lim_(x->0) D/x^2 = {c:.4f}")
        print("c is NOT 2/3 = 0.66667 (differs by 1%, outside discretisation error)\n")
        print("Delta vs the ambient IR cutoff L   (exact D, not the asymptotic form):")
        for x, lab in [(1e-3, 'network far exceeds the horizon  -> Delta = 1'),
                       (0.10, 'L = 10 R_H'),
                       (0.3125, 'L = comoving particle horizon'),
                       (0.50, 'L = 2 R_H')]:
            Dx = deficit(s, n, W, x)
            print(f"  R_H/L = {x:<7.4f}  Delta = {1 - 2*Dx/(1-Dx):.4f}   {lab}")

    assert 1.98 <= p <= 2.02,      f"deficit exponent {p:.4f} != d-alpha = 2"
    assert 0.672 <= c <= 0.674,    f"c = {c:.4f} outside converged range"
    assert (D >= 0).all(),         "deficit must be one-signed (D >= 0 => Delta <= 1)"
    assert abs(delta_of_x(1e-6, c) - 1.0) < 1e-9, "L -> infinity must give Delta = 1"
    return dict(c=c, exponent=p)


def convergence(Ms=(750, 1500, 3000)):
    print(f"{'M':>6} {'D(0.02)/x^2':>14} {'D(0.03)/x^2':>14}")
    for M in Ms:
        s, n, W = solve_newton(M=M)
        row = [deficit(s, n, W, x)/x**2 for x in (0.02, 0.03)]
        print(f"{M:6d} {row[0]:14.6f} {row[1]:14.6f}")


if __name__ == "__main__":
    check()
    print()
    convergence()
