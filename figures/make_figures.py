"""
make_figures.py — figures for Paper III (paper/SEDE_count.md).

Reuses the exact computations in src/ (capacity_radial, mincut_membrane, edge_deficit),
so every figure is regenerated from the same asserted code that produces the tables.
Writes to the repository output/ directory.

  count_fig0_reduction.png   — the reduction: count discharged by the leg-budget network (§1, §7)
  count_fig1_dichotomy.png   — the binary count: s(rho) phases + q(alpha) staircase (§2.3–2.4)
  count_fig2_membrane.png    — no minimum-cut surface: thickness ~ R vs const; shell fraction (§2.5)
  count_fig3_cutoff.png      — Delta = 1 and the IR cutoff; the deficit law (§5)

Run:  python experiments/paper3/make_figures.py
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Vector-friendly output: editable (TrueType) text in PDFs, tight bounding box.
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["savefig.bbox"] = "tight"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "src"))
OUT = os.path.join(REPO, "results")
os.makedirs(OUT, exist_ok=True)


def _save(fig, basename):
    """Save a figure as a vector PDF (primary) and a PNG (preview), to results/,
    with a tight bounding box so nothing is clipped."""
    pdf = os.path.join(OUT, basename + ".pdf")
    png = os.path.join(OUT, basename + ".png")
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(png, dpi=140, bbox_inches="tight", pad_inches=0.02)
    print("wrote", pdf)
    print("wrote", png)
    plt.close(fig)

import capacity_radial as cap
import mincut_membrane as mc
import edge_deficit as ed

GREEN, BLUE, ORANGE, GREY, RED = "#2e7d32", "#1565c0", "#e65100", "#555555", "#b71c1c"


# ---------------------------------------------------------------------------
def fig0_reduction():
    fig, ax = plt.subplots(figsize=(9.0, 5.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    def box(x, y, w, h, t, c, fc=None, fs=8.7):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.10",
                     lw=1.6, edgecolor=c, facecolor=fc or "white"))
        ax.text(x + w/2, y + h/2, t, ha="center", va="center", fontsize=fs, color="black")

    def arrow(x1, y1, x2, y2, c=GREY):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13, lw=1.3, color=c))

    box(3.0, 9.0, 4.0, 0.8, "SEDE input: volume-law horizon entropy\nS ∝ V   (Barrow Δ = 1)", GREY, "#f2f2f2")
    subs = [("state\nDERIVED (SYK)", GREEN, 0.2), ("form\nREDUCED (thermal)", BLUE, 2.65),
            ("scale\nDERIVED (CKN)", GREEN, 5.1), ("count\nbulk vs boundary", ORANGE, 7.55)]
    for t, c, x in subs:
        box(x, 7.3, 2.25, 0.85, t, c); arrow(5.0, 9.0, x + 1.12, 8.15, c)
    arrow(8.67, 7.3, 8.67, 6.6, ORANGE)
    box(5.3, 5.7, 4.5, 0.9, "THIS PAPER — leg-budgeted long-range network\n"
        "finite κ (unitarity) + bonds ∝ r^(−α)", ORANGE, "#fff3e6")
    arrow(7.55, 5.7, 6.2, 5.05, ORANGE)
    box(1.4, 3.9, 7.2, 1.05, "C(Ω) ≤ κ·|Ω|   ⇒   Δ ≤ 1   (theorem)\n"
        "α < d ⇒ volume (Δ=1);   α > d+1 ⇒ area (Δ=0);   gravity α=1 ⇒ volume\n"
        "flat infinite slice ⇒ L → ∞ ⇒ Δ = 1, zero parameters", GREEN, "#eaf5ea", fs=8.4)
    arrow(5.0, 3.9, 5.0, 3.25, GREEN)
    box(2.2, 2.15, 5.6, 0.9, "count REDUCED — a theorem (Δ ≤ 1) + two stated assumptions\n"
        "residue ↓ = the horizon's quantum state (foundations paper, route A)", GREEN, "#eaf5ea", fs=8.4)
    arrow(5.0, 2.15, 5.0, 1.5, GREY)
    box(2.6, 0.4, 4.8, 0.8, "DECIDED: Δ = 1 (cosmic) vs Δ = 0 (black hole)\nDESI DR3 + Euclid, σ(Δ) ≈ 0.09", BLUE)

    for i, (c, t) in enumerate([(GREEN, "derived / decided"), (BLUE, "measured"), (ORANGE, "the residue → discharged")]):
        ax.add_patch(FancyBboxPatch((0.2, 0.4 + i*0.5), 0.28, 0.28, boxstyle="round,pad=0.02",
                     edgecolor=c, facecolor="white", lw=1.6))
        ax.text(0.58, 0.54 + i*0.5, t, fontsize=7.3, va="center")
    ax.set_title("Reducing the count: a theorem (Δ ≤ 1) plus two stated assumptions", fontsize=11)
    fig.tight_layout(); _save(fig, "count_fig0_reduction")


# ---------------------------------------------------------------------------
def _q_measured(alpha, L=1200.0, M=2400):
    s, n, W = cap.budgeted_network(alpha, L=L, M=M)
    rhos = np.geomspace(6.0, 0.12*L, 8)
    C = np.array([W[np.ix_(s < r, ~(s < r))].sum() for r in rhos])
    half = rhos > rhos[len(rhos)//2]
    return float(np.polyfit(np.log(rhos[half]), np.log(C[half]), 1)[0])


def fig1_dichotomy():
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(10.0, 4.3))

    # (a) capacity per dof  s(rho)  for representative alpha
    rhos = [2, 3, 5, 8, 13, 20, 30, 40]
    styles = {1.0: (GREEN, "α = 1  (gravity, volume)"), 2.5: (BLUE, "α = 2.5"),
              4.0: (ORANGE, "α = 4  (= d+1, marginal)"), 6.0: (RED, "α = 6  (area)")}
    for a, (c, lab) in styles.items():
        o = cap.capacity(a, rhos)
        axa.plot([x[0] for x in o], [x[2] for x in o], "o-", color=c, ms=4, lw=1.6, label=lab)
    axa.set_xscale("log"); axa.set_xlabel("region radius  ρ  (Planck cells)")
    axa.set_ylabel("capacity per enclosed dof   s(ρ) = C/N_in")
    # Clean, non-overlapping x tick labels on the narrow log axis (major ticks only).
    from matplotlib.ticker import FixedLocator, NullLocator, FixedFormatter
    axa.xaxis.set_major_locator(FixedLocator([2, 5, 10, 20, 40]))
    axa.xaxis.set_major_formatter(FixedFormatter(["2", "5", "10", "20", "40"]))
    axa.xaxis.set_minor_locator(NullLocator())
    axa.axhline(1.0, color=GREY, ls=":", lw=1); axa.text(2.1, 1.02, "κ (budget saturated → volume)", fontsize=7.5, color=GREY)
    axa.set_ylim(0, 1.1); axa.legend(fontsize=7.8, loc="lower left"); axa.set_title("(a) the two phases", fontsize=10)

    # (b) capacity exponent q(alpha): theory staircase + measured points
    d = 3.0
    al = np.linspace(0.5, 6.0, 400)
    q_th = np.where(al < d, 3.0, np.where(al < d + 1, 3.0 - (al - d), 2.0))
    axb.plot(al, q_th, "-", color="k", lw=1.8, label="theory  q(α)")
    meas_a = [1.0, 2.0, 2.5, 3.5, 4.0, 5.0, 6.0]
    meas_q = [_q_measured(a) for a in meas_a]
    axb.plot(meas_a, meas_q, "s", color=BLUE, ms=6, label="measured (large ρ)")
    axb.axvspan(0.5, d, color=GREEN, alpha=0.08); axb.axvspan(d + 1, 6.0, color=RED, alpha=0.08)
    axb.text(1.0, 3.08, "VOLUME\n(α < d)", fontsize=8, color=GREEN, ha="center")
    axb.text(5.0, 2.12, "AREA\n(α > d+1)", fontsize=8, color=RED, ha="center")
    axb.axvline(1.0, color=GREEN, ls="--", lw=1.2); axb.text(1.05, 2.35, "gravity\n1/r", fontsize=7.6, color=GREEN)
    axb.axvline(d, color=GREY, ls=":", lw=1); axb.axvline(d + 1, color=GREY, ls=":", lw=1)
    axb.set_xlabel("bond-weight range exponent  α"); axb.set_ylabel("capacity exponent  q   (C ∝ ρ^q,  Δ = q − 2)")
    axb.set_ylim(1.85, 3.15); axb.legend(fontsize=8, loc="center right")
    axb.set_title("(b) the count is binary at the physical α", fontsize=10)

    fig.suptitle("The binary count: gravity (α=1) saturates the volume; no gravitational coupling gives intermediate Δ",
                 fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); _save(fig, "count_fig1_dichotomy")


# ---------------------------------------------------------------------------
def fig2_membrane():
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(10.0, 4.3))
    Rs = [3, 4, 5, 6]
    styles = {0.5: (GREEN, "-"), 1.0: (GREEN, "-"), 2.0: (BLUE, "-"), 3.0: (BLUE, "-"),
              4.0: (ORANGE, "--"), 6.0: (RED, "--")}
    shell = {}
    for a, (c, ls) in styles.items():
        rows = [mc.run(R, a) for R in Rs]
        th = [r["thickness"] for r in rows]
        axa.plot(Rs, th, ls, color=c, marker="o", ms=4, lw=1.6,
                 label=f"α = {a}" + ("  (∝R)" if a <= 3 else "  (const)"))
        shell[a] = rows[-1]["shellfrac"]
    axa.plot(Rs, [0.35*R for R in Rs], ":", color=GREY, lw=1.2)
    axa.text(4.6, 2.0, "∝ R  (no surface)", fontsize=8, color=GREY, rotation=32)
    axa.set_xlabel("ball radius  R  (lattice units)"); axa.set_ylabel("severed-bond thickness  (lattice units)")
    axa.set_title("(a) α ≤ d: the cut fills the volume; α > d: a membrane", fontsize=9.6)
    axa.legend(fontsize=7.8, ncol=2)

    aa = sorted(shell)
    cols = [GREEN if a <= 3 else RED for a in aa]
    axb.bar([str(a) for a in aa], [shell[a] for a in aa], color=cols, alpha=0.85)
    axb.axhline(1.0, color=GREY, ls=":", lw=1)
    axb.set_ylabel("boundary fraction of the min-cut source side"); axb.set_xlabel("α")
    axb.set_ylim(0, 1.1)
    axb.text(0.5, 1.03, "= 1.000 : cut degenerates onto the boundary (no bulk surface)", fontsize=7.6, color=GREEN)
    axb.set_title("(b) for α ≤ d there is no bulk min-cut surface", fontsize=9.6)

    fig.suptitle("No minimum-cut surface for a long-range horizon ⇒ no height field, no roughening (§2.5)", fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); _save(fig, "count_fig2_membrane")


# ---------------------------------------------------------------------------
def fig3_cutoff():
    s, n, W = ed.solve_newton()
    xs = np.geomspace(1e-3, 0.55, 60)
    Dx = np.array([ed.deficit(s, n, W, x) for x in xs])
    Delta = 1 - 2*Dx/(1 - Dx)

    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    ax.plot(xs, Delta, "-", color=BLUE, lw=2)
    ax.axhline(1.0, color=GREEN, ls="--", lw=1.3)
    ax.text(1.1e-3, 0.955, "Δ = 1  (L → ∞, flat slice)", fontsize=8.8, color=GREEN)
    # the trap points of §5.4 — labels anchored in axes fraction, arrows to the data points
    x0 = 0.3125; d0 = 1 - 2*ed.deficit(s, n, W, x0)/(1 - ed.deficit(s, n, W, x0))
    ax.plot(x0, d0, "o", color=ORANGE, ms=8)
    ax.annotate("L = comoving particle horizon\n→ Δ = 0.855", xy=(x0, d0),
                xytext=(0.63, 0.44), textcoords="axes fraction", fontsize=8.5, color=ORANGE,
                ha="center", arrowprops=dict(arrowstyle="->", color=ORANGE))
    i93 = int(np.argmin(np.abs(Delta - 0.93)))
    ax.plot(xs[i93], 0.93, "s", color=RED, ms=8)
    ax.annotate("some finite L gives Δ = 0.93 exactly\n(do not choose it — §5.4)", xy=(xs[i93], 0.93),
                xytext=(0.40, 0.66), textcoords="axes fraction", fontsize=8.5, color=RED,
                ha="center", arrowprops=dict(arrowstyle="->", color=RED))
    ax.set_xscale("log"); ax.set_xlabel("R_H / L   (horizon radius / network IR cutoff)")
    ax.set_ylabel("effective deformation  Δ(R_H/L)"); ax.set_ylim(0.5, 1.03)
    ax.set_title("Δ = 1 is the L → ∞ endpoint; any finite L is a fitted parameter (§5)", fontsize=10)

    # inset: the deficit law D(x) = c x^2  (lower-left, under the flat part of the curve).
    # Raised off the bottom so its ticks/label clear the main x-axis; major-only log ticks
    # so the inset's own tick labels don't crowd or collide.
    from matplotlib.ticker import LogLocator, NullLocator
    axi = fig.add_axes([0.17, 0.30, 0.26, 0.26])
    xi = np.geomspace(0.02, 0.3, 20); Di = np.array([ed.deficit(s, n, W, x) for x in xi])
    axi.loglog(xi, Di, "o", color=BLUE, ms=3); axi.loglog(xi, 0.6730*xi**2, "-", color=GREY, lw=1.2)
    axi.set_title("D(x) = c x²,  c = 0.673", fontsize=7.5); axi.tick_params(labelsize=6.5)
    axi.set_xlabel("x = ρ/L", fontsize=7, labelpad=1.5)
    axi.set_ylabel("deficit D", fontsize=7, labelpad=1.5)
    axi.xaxis.set_major_locator(LogLocator(base=10.0))
    axi.xaxis.set_minor_locator(NullLocator())
    axi.yaxis.set_minor_locator(NullLocator())
    axi.patch.set_alpha(0.95)

    _save(fig, "count_fig3_cutoff")


if __name__ == "__main__":
    fig0_reduction()
    fig1_dichotomy()
    fig2_membrane()
    fig3_cutoff()
