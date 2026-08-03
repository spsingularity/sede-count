#!/usr/bin/env bash
# Build the Physical Review D PDF (revtex4-2) for Paper II from SEDE_count.md.
#   makedoc (title/abstract/keywords -> YAML, fold figures, number sections)
#   -> pandoc --natbib with template_prd.tex -> pdflatex + bibtex.
# The CQG/iopart build is build.sh; this is the PRD sibling after the Aug 2026 reframe.
set -e
cd "$(dirname "$0")"
mkdir -p tex_prd
BASE=SEDE_count

python3 tools/makedoc.py $BASE.md .build_prd.md
trap 'rm -f .build_prd.md' EXIT
# drop the citeproc "## References / ::: {#refs}" placeholder — natbib \bibliography handles it.
# NOTE: unlike Paper VII's PRD build we do NOT wrap inline $...$ as raw-LaTeX spans. Paper II's
# markdown carries native display/inline math (integrals, \rho, sub/superscripts) that the wrap
# corrupts into "Bad math environment delimiter". Its iopart build (build.sh) omits the wrap too.
python3 - <<'PY_INNER'
import re
t=open('.build_prd.md',encoding='utf-8').read()
t=re.sub(r'\n##\s+References\s*\n+:::\s*\{#refs\}\s*\n:::\s*\n','\n',t)
open('.build_prd.md','w',encoding='utf-8').write(t)
PY_INNER

pandoc -f markdown-superscript-subscript .build_prd.md -o tex_prd/$BASE.tex \
  --standalone --shift-heading-level-by=-1 --natbib \
  --template=tools/template_prd.tex

# figure paths: from tex_prd/ the repo results dir is ../../results ; prefer vector .pdf
perl -0pi -e 's#\{\.\./results/([^}]+?)\.png\}#{../../results/\1}#g' tex_prd/$BASE.tex
# numeric journal: no author-prominent form — normalise \citet -> \citep
perl -0pi -e 's#\\citet\{#\\citep{#g' tex_prd/$BASE.tex
# make long monospace paths breakable (prevents right-margin overflow)
perl -0pi -e 's{\\texttt\{([^{}]*)\}}{"\\texttt{".($1=~s#([/._])#$1\\allowbreak #gr)."}"}ge' tex_prd/$BASE.tex
# number display equations: pandoc emits \[ ... \]; convert to a numbered environment
perl -0pi -e 's/\\\[/\\begin{equation}/g; s/\\\]/\\end{equation}/g' tex_prd/$BASE.tex

( cd tex_prd && \
  pdflatex -interaction=nonstopmode $BASE.tex >$BASE.build.log 2>&1 ; \
  BIBINPUTS="..:$BIBINPUTS" bibtex $BASE      >>$BASE.build.log 2>&1 ; \
  pdflatex -interaction=nonstopmode $BASE.tex >>$BASE.build.log 2>&1 ; \
  pdflatex -interaction=nonstopmode $BASE.tex >>$BASE.build.log 2>&1 ) || true

if [ -f tex_prd/$BASE.pdf ]; then
  cp tex_prd/$BASE.pdf ${BASE}_prd.pdf
  echo "built paper/${BASE}_prd.pdf  (Physical Review D)"
  grep -c "^!" tex_prd/$BASE.build.log | awk '{print $1" LaTeX errors (see tex_prd/'$BASE'.build.log)"}'
  grep -c "Warning--" tex_prd/$BASE.build.log 2>/dev/null | awk '{print $1" bibtex warnings"}'
  grep -c "Citation.*undefined" tex_prd/$BASE.build.log 2>/dev/null | awk '{print $1" undefined citations"}'
else
  echo "BUILD FAILED — see tex_prd/$BASE.build.log"; grep -A2 '^!' tex_prd/$BASE.build.log | head -20
fi
