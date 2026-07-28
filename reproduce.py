#!/usr/bin/env python3
"""Single entry point. Regenerates every number in the Paper III draft, with assertions."""
import sys, os, time, importlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

STAGES = [
    ("horizon_constraint", "Eq. (2.9): AH constraint, KPZ coefficient = 0"),
    ("ams_stability",      "Eq. (2.9) = AMS MOTS stability operator (external-standard check)"),
    ("capacity_radial",    "Sec. 2.3: alpha crossover, budgeted capacity"),
    ("outward_fraction_bound", "Prop. 2.1: finite-size outward-fraction bound, uniform in position"),
    ("edge_deficit",       "Sec. 5.1-5.2: deficit law D(x) = c x^2, c = 0.6730"),
    ("mincut_membrane",    "Sec. 2.5: no min-cut surface for alpha < d"),
]

if __name__ == "__main__":
    ok = True
    for mod, desc in STAGES:
        t = time.time()
        print("=" * 78); print(f"[{mod}]  {desc}"); print("=" * 78)
        try:
            importlib.import_module(mod).check()
            print(f"\n  PASS  ({time.time()-t:.1f}s)\n")
        except AssertionError as e:
            ok = False; print(f"\n  FAIL  {e}\n")
    print("ALL STAGES PASS" if ok else "SOME STAGES FAILED")
    sys.exit(0 if ok else 1)
