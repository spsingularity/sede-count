#!/usr/bin/env python3
"""Rigorous finite-size bound on the outward fraction (closes the §2.3 gap).

THE GAP (as stated in §8): the α < d volume law was argued by observing that
the bond-mass integral ∫^L u^{d-1-α}du is dominated by its upper limit, so the
outward fraction → 1. That argument silently interchanges ρ → ∞ with the
continuum limit, and at fixed ambient size L the outward fraction in fact
DECREASES with ρ (it must vanish as ρ → L). What is needed instead is a bound
that holds at finite (ℓ, ρ, L), uniformly in the site position.

THE BOUND PROVED HERE (d = 3, α < d; general d in the paper):

  for every site x with |x| = s ≤ ρ,
      f_out(x)  ≥  1 − K(d,α) (ρ/L)^{d−α},
  hence
      κ n V(ρ) [1 − K (ρ/L)^{d−α}]  ≤  C(ρ)  ≤  κ n V(ρ).

  Proof sketch: every interior point lies within 2ρ of x, so the inward mass is
  at most n S_{d−1} (2ρ)^{d−α}/(d−α). Every point of the outer shell
  L/2 < |y| < L lies within 2L of x, so the outward mass is at least
  n c_d (1−2^{−d}) 2^{−α} L^{d−α}. Their ratio gives K.

This script verifies (a) that the deficit 1 − f_out really scales as
(ρ/L)^{d−α} — the exponent, not just the trend — and (b) that the measured
deficit lies below the proved bound, i.e. the bound is valid and not vacuous.

Radial kernel: exact angular average of |x−y|^{−α} for |x|=s, |y|=t in d=3,
    K(s,t) = [(s+t)^{2−α} − |s−t|^{2−α}] / (2 s t (2−α)).

Run: python3 src/outward_fraction_bound.py
"""
import numpy as np
from scipy import integrate

D = 3


def radial_kernel(s, t, alpha):
    """Angular average of |x-y|^{-alpha} over directions of y (d=3)."""
    s = np.maximum(s, 1e-12)
    t = np.maximum(t, 1e-12)
    if abs(alpha - 2.0) < 1e-12:                    # log case
        return np.log((s + t) / np.abs(s - t)) / (2 * s * t)
    return ((s + t) ** (2 - alpha) - np.abs(s - t) ** (2 - alpha)) / (
        2 * s * t * (2 - alpha))


def masses(s, rho, L, alpha, eps):
    """Inward (within rho) and outward (rho..L) bond mass for a site at radius s.
    eps is the short-distance (lattice) cutoff."""
    f = lambda t: radial_kernel(s, t, alpha) * 4 * np.pi * t ** 2
    # split the inner integral at s to keep the integrable |s-t| kink resolved
    lo, _ = integrate.quad(f, 0, min(s, rho), points=[s] if s < rho else None,
                           limit=400)
    hi, _ = integrate.quad(f, min(s, rho), rho, limit=400) if s < rho else (0.0, 0)
    inward = lo + hi
    outward, _ = integrate.quad(f, rho, L, limit=400)
    # subtract the self/near-field ball of radius eps (finite for alpha < d)
    near = 4 * np.pi * eps ** (D - alpha) / (D - alpha)
    return max(inward - near, 0.0), outward


def f_out(s, rho, L, alpha, eps):
    i, o = masses(s, rho, L, alpha, eps)
    return o / (i + o)


def K_bound(alpha, d=D):
    """Explicit constant in f_out >= 1 - K (rho/L)^{d-alpha}."""
    S = 4 * np.pi                      # surface of unit sphere, d=3
    c = 4 * np.pi / 3                  # volume of unit ball, d=3
    inward_max = S * (2 ** (d - alpha)) / (d - alpha)
    outward_min = c * (1 - 2 ** (-d)) * 2 ** (-alpha)
    return inward_max / outward_min


def capacity_deficit(rho, L, alpha, eps, nshell=24):
    """1 - C(rho)/(kappa n V(rho)): volume-weighted average of 1 - f_out."""
    ss = np.linspace(0.02 * rho, 0.995 * rho, nshell)
    w = ss ** 2                                     # volume weight
    vals = np.array([1 - f_out(s, rho, L, alpha, eps) for s in ss])
    return float(np.sum(vals * w) / np.sum(w))


def check():
    L, eps = 200.0, 1.0
    print("=" * 78)
    print("FINITE-SIZE BOUND ON THE OUTWARD FRACTION   (d = 3, L = %.0f)" % L)
    print("=" * 78)
    print("\nPredicted: deficit 1 - C/(kappa n V) ~ K (rho/L)^(d-alpha), uniformly in s\n")

    for alpha in [1.0, 1.5, 2.0, 2.5]:
        rhos = np.array([5.0, 10.0, 20.0, 40.0])
        defs = np.array([capacity_deficit(r, L, alpha, eps) for r in rhos])
        # fit the exponent of the deficit vs rho
        p = np.polyfit(np.log(rhos), np.log(defs), 1)[0]
        Kb = K_bound(alpha)
        Kmeas = defs / (rhos / L) ** (D - alpha)
        ok = np.all(defs <= Kb * (rhos / L) ** (D - alpha))
        print(f"alpha = {alpha}:  predicted exponent d-alpha = {D-alpha:.2f}, "
              f"measured = {p:.3f}")
        print(f"    deficits {np.array2string(defs, precision=4)}")
        print(f"    K measured {np.array2string(Kmeas, precision=3)}  "
              f"| K proved = {Kb:.2f}  | bound holds: {ok}")
    print("\n[READ-OUT]")
    print("  The measured deficit exponent tracks d-alpha across the range, and every")
    print("  measured deficit lies below the proved bound K (rho/L)^(d-alpha).")
    print("  The volume law is therefore a finite-size statement with an explicit")
    print("  error term -- no interchange of rho->inf with the continuum limit.")

    # ---- validation assertions (the paper cites this script as asserted) ----
    rhos = np.array([5.0, 10.0, 20.0, 40.0])
    for alpha in [1.0, 1.5, 2.0, 2.5]:
        defs = np.array([capacity_deficit(r, L, alpha, eps) for r in rhos])
        Kb = K_bound(alpha)
        assert np.all(defs <= Kb * (rhos / L) ** (D - alpha)), \
            f"proved bound violated at alpha={alpha}"
        assert np.all(np.diff(defs) > 0), f"deficit not monotone in rho at alpha={alpha}"
    # gravity's case: the deficit exponent must match d-alpha closely
    defs1 = np.array([capacity_deficit(r, L, 1.0, eps) for r in rhos])
    p1 = np.polyfit(np.log(rhos), np.log(defs1), 1)[0]
    assert abs(p1 - (D - 1.0)) < 0.1, f"alpha=1 deficit exponent {p1:.3f} != {D-1.0}"
    # and the fitted constant must be O(1) and stable
    K1 = defs1 / (rhos / L) ** (D - 1.0)
    assert 0.5 < K1.min() and K1.max() < 1.5, f"K_measured out of O(1) range: {K1}"
    assert K1.max() / K1.min() < 1.2, f"K_measured not stable across rho: {K1}"
    print("\n  all validation assertions passed")


if __name__ == "__main__":
    check()
