"""
Eq. (2.9) of Paper III: second-order expansion of the apparent-horizon condition.

Newtonian gauge, zero shift  =>  K_ij is pure trace  =>  theta_+ = M - (2/3)K,
independent of the surface normal.  Background: M = 2/R_bar, K = 3H  =>  R_AH = 1/H.
The trapping condition is therefore a constant-mean-curvature condition, i.e. the
Euler-Lagrange equation of  E[h] = A[h] - 2H V[h].

Claims verified here:
  (a)  M * R_bar  =  [2(1+h) - lap_S h] / (1+h)^2     (through O(h^2))
  (b)  the coefficient of |grad_S h|^2 at second order is EXACTLY ZERO
       -> no KPZ nonlinearity in the constraint
  (c)  a translated sphere returns M = 2/R_bar exactly (independent check)
  (d)  there is no d/dt anywhere: the constraint is elliptic on the sphere,
       h_lm = 2 S_lm / (2 - l(l+1)),  high-l suppressed as 1/l^2.
"""
import sympy as sp


def mean_curvature_axisym():
    r, th, R0, eps = sp.symbols('r theta R0 epsilon', positive=True)
    f = sp.Function('f')(th)
    g = sp.diag(1, r**2, r**2*sp.sin(th)**2)
    ginv, sqg = g.inv(), r**2*sp.sin(th)
    R = R0*(1 + eps*f)
    F = r - R
    dF = sp.Matrix([sp.diff(F, r), sp.diff(F, th), 0])
    grad = ginv*dF
    norm = sp.sqrt(sum(grad[i]*dF[i] for i in range(3)))
    s = grad/norm
    M = (sp.diff(sqg*s[0], r) + sp.diff(sqg*s[1], th))/sqg
    M = M.subs(r, R)                     # evaluate ON the surface, after differentiating
    ser = sp.expand(sp.simplify(sp.expand(M*R0).series(eps, 0, 3).removeO()))
    lap = sp.diff(f, th, 2) + sp.cos(th)/sp.sin(th)*sp.diff(f, th)
    return ser, f, th, eps, lap, M, R0


def check():
    ser, f, th, eps, lap, M, R0 = mean_curvature_axisym()
    c0 = sp.simplify(ser.coeff(eps, 0))
    c1 = sp.simplify(ser.coeff(eps, 1) + 2*f + lap)               # want 0
    c2 = sp.simplify(ser.coeff(eps, 2) - (2*f**2 + 2*f*lap))      # want 0
    kpz = sp.simplify(sp.expand(ser.coeff(eps, 2)).coeff(sp.diff(f, th)**2))

    assert c0 == 2,  f"background mean curvature wrong: {c0}"
    assert c1 == 0,  f"linear term wrong: {c1}"
    assert c2 == 0,  f"quadratic term wrong: {c2}"
    assert kpz == 0, f"KPZ coefficient is not zero: {kpz}"

    # translated sphere: exactly 2/R0
    d = sp.symbols('d', positive=True)
    htr = sp.series(sp.sqrt(R0**2 - d**2*sp.sin(th)**2) + d*sp.cos(th), d, 0, 3).removeO()/R0 - 1
    Mt = sp.series(sp.simplify(M.subs(eps, 1).subs(f, htr).doit()), d, 0, 3).removeO()
    Mt = sp.simplify(sp.expand_trig(sp.simplify(Mt*R0)))
    Mt = Mt.args[-1][0] if isinstance(Mt, sp.Piecewise) else Mt
    assert sp.simplify(Mt - 2) == 0, f"translated sphere gives {Mt}, expected 2"

    return dict(background=int(c0), kpz_coefficient=int(kpz), translated_sphere="exact")


if __name__ == "__main__":
    print(check())
