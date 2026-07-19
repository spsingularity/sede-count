"""
External-standard check of eq. (2.9): the operator ∇²_S + 2 is the Andersson–Mars–Simon
MOTS stability operator specialised to the FRW apparent horizon.

AMS (Adv. Theor. Math. Phys. 12 (2008) 853) give the MOTS stability operator for the
variation of the outer expansion θ₊:

    L ψ = −Δ_S ψ + 2 s^A D_A ψ + ( ½ R_S − |σ⁺|² − s_A s^A + D_A s^A − 8π T_{ab} ℓ^a k^b ) ψ .

On the FRW apparent horizon the surface is a round 2-sphere of areal radius R̄ = 1/H, so
s_A = 0 (spherical symmetry), σ⁺ = 0 (shear-free), and — for the *within-slice* shape
variation in the shear-free Newtonian slice — the operator reduces to the classical
mean-curvature Jacobi operator −(Δ_S + |A|²) with |A|² = 2/R̄².  That is exactly ∇²_S + 2:

    δ𝓜 = −(1/R̄)(∇²_S + 2) f ,   eigenvalues on Y_ℓ:  ℓ(ℓ+1) − 2 ,   ℓ=1 ↦ 0 (translations).

Two things are checked here, both against the *external* AMS/Jacobi standard rather than
against the divergence-of-normal derivation used in horizon_constraint.py:

  (1) a SECOND, independent geometric derivation (surface-of-revolution principal curvatures)
      reproduces δ𝓜 = −(1/R̄)(∇²_S + 2) f, with the published spectrum ℓ(ℓ+1) − 2 and the
      ℓ=1 translation zero mode;
  (2) the AMS matter term for FRW is 8π T_{ab} ℓ^a k^b = 3H² + Ḣ, so the *null-direction*
      (MOTT-evolution) stability operator carries an Ḣ that the *within-slice* shape operator
      does not — which is why eq. (2.9) is elliptic (no ∂_t).  The clean elliptic form is
      therefore slicing-specific (shear-free slice + flat spatial sections): the slicing caveat.
"""
import sympy as sp


def jacobi_from_principal_curvatures():
    """δ𝓜 for r = R̄(1+εf(θ)) via the surface-of-revolution principal curvatures
    (independent of the divergence method in horizon_constraint.py)."""
    th = sp.symbols('theta', positive=True)            # θ ∈ (0, π) ⇒ sinθ > 0
    Rb, eps = sp.symbols('R_bar epsilon', positive=True)
    f = sp.Function('f')
    R = Rb*(1 + eps*f(th))
    rho, z = R*sp.sin(th), R*sp.cos(th)                 # profile of the surface of revolution
    rp, zp = sp.diff(rho, th), sp.diff(z, th)
    rpp, zpp = sp.diff(rho, th, 2), sp.diff(z, th, 2)
    sp2 = rp**2 + zp**2
    k_mer = (zp*rpp - rp*zpp)/sp2**sp.Rational(3, 2)    # meridian principal curvature
    k_par = -zp/(rho*sp.sqrt(sp2))                      # azimuthal principal curvature
    Mcurv = k_mer + k_par                              # 𝓜 = κ₁ + κ₂ (outward normal ⇒ 𝓜₀ = +2/R̄)
    M0 = sp.simplify(Mcurv.subs(eps, 0))
    dM = sp.diff(Mcurv, eps).subs(eps, 0)
    return th, Rb, eps, f, Mcurv, M0, dM


def ams_matter_term():
    """8π T_{ab} ℓ^a k^b on the FRW horizon, with ℓ,k the null normals (ℓ·k = −1),
    T perfect fluid, and the Friedmann relations.  Returns the simplified value."""
    rho, p, H, Hdot = sp.symbols('rho p H Hdot', real=True)
    # ℓ = (u + e_r)/√2, k = (u − e_r)/√2 ⇒ (u·ℓ)(u·k) = 1/2, ℓ·k = −1
    #   T_{ab} ℓ^a k^b = (ρ+p)(u·ℓ)(u·k) + p(ℓ·k) = (ρ+p)/2 − p = (ρ − p)/2
    Tlk = (rho - p)/2
    # Friedmann (8πG=1): 8πρ = 3H²,  Ḣ = −4π(ρ+p)  ⇒  8πp = −2Ḣ − 3H²
    subs = {8*sp.pi*rho: 3*H**2}
    val = sp.simplify((8*sp.pi*Tlk)
                      .rewrite(sp.Add)
                      .subs({rho: 3*H**2/(8*sp.pi), p: (-2*Hdot - 3*H**2)/(8*sp.pi)}))
    return sp.simplify(val), H, Hdot


def check():
    th, Rb, eps, f, Mcurv, M0, dM = jacobi_from_principal_curvatures()

    # (0) background: round-sphere CMC 𝓜₀ = 2/R̄  (= 2H, Paper III's condition)
    assert sp.simplify(M0*Rb - 2) == 0, f"background mean curvature wrong: {M0}"

    # (1) operator: δ𝓜 = −(1/R̄)(∇²_S + 2) f   (∇²_S f = f'' + cotθ f')
    lap = sp.diff(f(th), th, 2) + sp.cos(th)/sp.sin(th)*sp.diff(f(th), th)
    resid = sp.simplify(sp.trigsimp(dM + (lap + 2*f(th))/Rb))
    assert resid == 0, f"AMS/Jacobi operator mismatch, residual = {resid}"

    # (2) published spectrum ℓ(ℓ+1) − 2, with ℓ=1 the translation zero mode
    th0 = sp.pi/3
    spectrum = {}
    for l in range(0, 6):
        Pl = sp.legendre(l, sp.cos(th))
        dMl = sp.diff(Mcurv, eps).subs(eps, 0).subs(f(th), Pl).doit()
        val = int(sp.nsimplify(sp.simplify((Rb*dMl/Pl).subs(th, th0))))
        assert val == l*(l+1) - 2, f"ℓ={l}: got {val}, expected {l*(l+1)-2}"
        spectrum[l] = val
    assert spectrum[1] == 0, "ℓ=1 must be the translation zero mode"

    # (3) AMS matter term ⇒ the slicing caveat (null variation carries Ḣ; the shape op does not)
    Tterm, H, Hdot = ams_matter_term()
    assert sp.simplify(Tterm - (3*H**2 + Hdot)) == 0, f"AMS matter term wrong: {Tterm}"
    null_potential = sp.simplify(H**2 - Tterm)          # ½R_S − 8πTℓk,  ½R_S = 1/R̄² = H²
    within_slice_potential = -2*H**2                    # −|A|² = −2/R̄² = −2H²
    dHt = sp.simplify(null_potential - within_slice_potential)
    assert sp.simplify(dHt + Hdot) == 0, f"expected the two operators to differ by −Ḣ, got {dHt}"

    print("(1) surface-of-revolution derivation:  δ𝓜 = −(1/R̄)(∇²_S + 2) f   [matches horizon_constraint]")
    print("(2) AMS/Jacobi spectrum ℓ(ℓ+1)−2:     ", [spectrum[l] for l in range(6)],
          "  (ℓ=1 = 0, translation zero mode)")
    print("(3) AMS matter term 8πT_{ab}ℓ^a k^b =  3H² + Ḣ")
    print("    within-slice shape operator (elliptic):  potential −2H²   ⇒  ∇²_S + 2")
    print("    null-direction (MOTT) operator:          potential −2H² − Ḣ")
    print("    ⇒ the elliptic form is slicing-specific (shear-free + flat slice): the slicing caveat.")
    return dict(operator="∇²_S + 2", spectrum=[spectrum[l] for l in range(6)],
                ams_matter_term="3H^2 + Hdot", translation_zero_mode=(spectrum[1] == 0))


if __name__ == "__main__":
    print(check())
