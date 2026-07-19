# sede-count

**SEDE II: The Horizon Count — Delta = 1 from a Leg-Budgeted Long-Range Network**

Paper II: the volume-law horizon count. Derives Delta=1 with zero parameters from network capacity; includes the finite-L deformation family and falsifiers.

Part of the USC research program (SEDE / ECCG / APDM unification).

## Status
Pre-submission working repository, seeded 2026-07-17 from a private research hub;
full research history (including audit trails and
retractions) lives there.

## Layout
- `paper/` — manuscript sources (md + tex + build scripts; built PDF included); `paper/tools/` = build tooling
- `src/` + `reproduce.py` — the capacity/deficit computations backing every number in the paper (`results/RESULTS.txt` = reference output)
- `figures/make_figures.py` — regenerates the four figures into `results/`
- `results/` — reference outputs (figures + RESULTS.txt)

## License
- **Text and figures** (the paper): [CC-BY-4.0](LICENSE-CC-BY-4.0.txt)
- **Code**: [MIT](LICENSE)

## Citation
See `CITATION.cff`. A Zenodo DOI will be minted at first release.
