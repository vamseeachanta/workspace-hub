---
name: pandoc-5-custom-latex-templates
description: 'Sub-skill of pandoc: 5. Custom LaTeX Templates (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 5. Custom LaTeX Templates (+1)

## 5. Custom LaTeX Templates


```latex
%% template.tex - Custom Pandoc LaTeX template
\documentclass[$if(fontsize)$$fontsize$,$endif$$if(papersize)$$papersize$paper,$endif$]{article}

%% Packages
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{fontspec}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{listings}

%% Fonts
$if(mainfont)$
\setmainfont{$mainfont$}
$endif$
$if(sansfont)$
\setsansfont{$sansfont$}
$endif$
$if(monofont)$
\setmonofont{$monofont$}
$endif$

%% Colors
\definecolor{linkcolor}{RGB}{0, 102, 204}
\definecolor{codebackground}{RGB}{248, 248, 248}

%% Hyperlinks
\hypersetup{
    colorlinks=true,
    linkcolor=linkcolor,
    urlcolor=linkcolor,
    pdfauthor={$author$},
    pdftitle={$title$}
}

%% Headers and footers
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{$title$}
\fancyhead[R]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

%% Code blocks
\lstset{
    backgroundcolor=\color{codebackground},
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    numbers=left,
    numberstyle=\tiny\color{gray}
}

%% Section formatting
\titleformat{\section}
    {\Large\bfseries\color{linkcolor}}
    {\thesection}{1em}{}
\titleformat{\subsection}
    {\large\bfseries}
    {\thesubsection}{1em}{}

%% Title
$if(title)$
\title{$title$}
$endif$
$if(author)$
\author{$author$}
$endif$
$if(date)$
\date{$date$}
$endif$

\begin{document}

$if(title)$
\maketitle
$endif$

$if(abstract)$
\begin{abstract}
$abstract$
\end{abstract}
$endif$

$if(toc)$
\tableofcontents
\newpage
$endif$

$body$

\end{document}
```

```bash
# Use custom template
pandoc document.md -o document.pdf \
    --template=template.tex \
    --pdf-engine=xelatex \
    -V title="My Document" \
    -V author="Your Name" \
    -V date="2026-01-17" \
    --toc
```


## 6. YAML Metadata in Documents


```markdown
---
title: "Technical Report"
author:
  - name: "John Smith"
    affiliation: "University of Example"
    email: "john@example.edu"
  - name: "Jane Doe"
    affiliation: "Tech Corp"
date: "January 17, 2026"
abstract: |
  This document demonstrates advanced Pandoc features
  including custom metadata, citations, and formatting.
keywords:
  - documentation
  - pandoc
  - markdown
lang: en-US
toc: true
toc-depth: 3
numbersections: true
geometry: margin=1in
fontsize: 11pt
mainfont: "Georgia"
monofont: "Fira Code"
linkcolor: blue
bibliography: references.bib
csl: ieee.csl
---

# Introduction

Your document content starts here...
```
