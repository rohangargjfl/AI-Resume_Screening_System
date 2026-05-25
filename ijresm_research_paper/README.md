# IJRESM Research Paper

This folder contains the IJRESM-style manuscript version of the AI Resume Screening System research paper.

## Files

- `main.tex` - IJRESM-themed LaTeX skeleton that includes all modular files.
- `preamble.tex` - packages, spacing, captions, headings, and author-block macros.
- `frontmatter/titleblock.tex` - title, guide/student table, abstract, and keywords.
- `chapters/` - modular paper sections.
- `references/references.tex` - numbered reference list.
- Figures are reused from `../latex_report/figures/`.

## Template Basis

This version was adapted from:

- `IJRESM_Manuscript_Template_2026.docx`
- `Conference Paper Text Watermarking.pdf`

The layout follows the observed IJRESM conventions:

- A4 two-column manuscript layout
- Times-style typography
- 24 pt centered title
- 11 pt centered author names
- 8 pt affiliations, captions, table text, and references
- 9 pt abstract and keywords
- 10 pt body text
- Roman-numbered centered primary sections
- Alphabetic italic subsections
- `Fig. 1.` style figure captions
- `TABLE I` style table captions
- Bordered author table and sample-style abstract/keywords block

## Compile

Use Overleaf or a local LaTeX installation:

```bash
pdflatex main.tex
pdflatex main.tex
```

The current workspace does not have a LaTeX compiler installed, so a PDF was not generated locally.
