# AI Resume Screening Final Report LaTeX Skeleton

This folder is a paste-ready LaTeX structure for the Gemini-generated report.

## Compile

Use XeLaTeX or LuaLaTeX because `fontspec` and Times New Roman are used.

```bash
cd latex_report
xelatex main.tex
xelatex main.tex
```

## Where to paste content

- `frontmatter/titlepage.tex`: already filled with title/team/guide details.
- `frontmatter/declaration.tex`: declaration text.
- `frontmatter/certificate.tex`: certificate text.
- `frontmatter/acknowledgement.tex`: acknowledgement text.
- `frontmatter/abstract.tex`: abstract from the PDF.
- `frontmatter/abbreviations.tex`: abbreviation table.
- `chapters/chapter1_introduction.tex`: Chapter 1.
- `chapters/chapter2_literature_review.tex`: Chapter 2.
- `chapters/chapter3_objectives_gaps.tex`: Chapter 3.
- `chapters/chapter4_system_architecture_design.tex`: Chapter 4 and flowchart.
- `chapters/chapter5_implementation.tex`: Chapter 5.
- `chapters/chapter6_experimental_setup_benchmarking.tex`: Chapter 6.
- `chapters/chapter7_results_findings.tex`: Chapter 7.
- `chapters/chapter8_limitations.tex`: Chapter 8.
- `chapters/chapter9_conclusion_future_work.tex`: Chapter 9.
- `references/references.tex`: final IEEE-style references.

## Figure

Put the project flowchart image at:

```text
latex_report/figures/project_flowchart.png
```

The Chapter 4 file already includes it with:

```latex
\includegraphics[width=0.92\textwidth]{project_flowchart.png}
```
