#!/usr/bin/env bash
# Build the CQG-class PDF (iopart.cls) for Paper III from SEDE_count.md.
#   makedoc (title/abstract -> YAML) -> strip the citeproc refs placeholder
#   -> pandoc --natbib (emits \citep) with template_count.tex -> xelatex + bibtex.
set -e
cd "$(dirname "$0")"
mkdir -p tex

python3 tools/makedoc.py SEDE_count.md .SEDE.count.md
trap 'rm -f .SEDE.count.md' EXIT
# drop the citeproc "## References / ::: {#refs}" placeholder — natbib \bibliography handles it
python3 - <<'PY'
import re
t=open('.SEDE.count.md',encoding='utf-8').read()
t=re.sub(r'\n##\s+References\s*\n+:::\s*\{#refs\}\s*\n:::\s*\n','\n',t)
open('.SEDE.count.md','w',encoding='utf-8').write(t)
PY

pandoc -f markdown-superscript-subscript .SEDE.count.md -o tex/SEDE_count.tex \
  --standalone \
  --shift-heading-level-by=-1 \
  --natbib \
  --template=tools/template_count.tex

# figure paths: from tex/ the repo results dir is ../../results ; prefer vector .pdf
perl -0pi -e 's#\{\.\./results/([^}]+?)\.png\}#{../../results/\1}#g' tex/SEDE_count.tex
# numeric journal (iopart-num): no author-prominent form — normalise \citet -> \citep
perl -0pi -e 's#\\citet\{#\\citep{#g' tex/SEDE_count.tex

( cd tex && \
  xelatex -interaction=nonstopmode SEDE_count.tex >SEDE_count.build.log 2>&1 ; \
  BIBINPUTS="..:$BIBINPUTS" bibtex SEDE_count      >>SEDE_count.build.log 2>&1 ; \
  xelatex -interaction=nonstopmode SEDE_count.tex >>SEDE_count.build.log 2>&1 ; \
  xelatex -interaction=nonstopmode SEDE_count.tex >>SEDE_count.build.log 2>&1 ) || true

if [ -f tex/SEDE_count.pdf ]; then
  echo "built paper/tex/SEDE_count.pdf"
  grep -c "^!" tex/SEDE_count.build.log | awk '{print $1" LaTeX errors (see tex/SEDE_count.build.log)"}'
  grep -c "Warning--" tex/SEDE_count.build.log 2>/dev/null | awk '{print $1" bibtex warnings"}'
else
  echo "BUILD FAILED — see tex/SEDE_count.build.log"; grep -A2 '^!' tex/SEDE_count.build.log | head -20
fi
