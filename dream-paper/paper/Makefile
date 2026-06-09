PDF = main.pdf
TEX = main.tex

all: $(PDF)

$(PDF): $(TEX) sections/*.tex references.bib
	pdflatex -interaction=nonstopmode $(TEX)
	bibtex main
	pdflatex -interaction=nonstopmode $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)

# Anonymized build for double-blind venues: strips the author block.
anonymous: $(TEX)
	sed 's/^\\author{.*/\\author{Anonymous Submission}/; s/\\small Independent Researcher.*//' $(TEX) > main_anon.tex
	pdflatex -interaction=nonstopmode -jobname=main_anon main_anon.tex
	bibtex main_anon
	pdflatex -interaction=nonstopmode -jobname=main_anon main_anon.tex
	pdflatex -interaction=nonstopmode -jobname=main_anon main_anon.tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out main_anon.tex
