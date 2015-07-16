all: genome.pdf

genome.pdf: genome.tex
	latex genome
	bibtex genome
	latex genome
	bibtex genome
	pdflatex genome.tex
