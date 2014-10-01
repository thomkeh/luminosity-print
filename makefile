# makefile to convert between different formats
# 'make update' downloads new chapters
# 'make all' downloads new chapters and builds all formats

# recursive rather than immediate expansion is used because
# the list of files must be up to date after new chapters are downloaded
DUMP_FILES = $(wildcard html-dump/*.htm)
MARKDOWN_TARGETS = $(DUMP_FILES:html-dump/%.htm=markdown/%.md)
LATEX_TARGETS = $(MARKDOWN_TARGETS:markdown/%.md=latex/%.tex)
HTML_TARGETS = $(MARKDOWN_TARGETS:markdown/%.md=html/%.htm)
HPOTTER_FILES = templates/latex/hpmor.sty templates/latex/hpotter/hpotter.sty templates/latex/hpmor.tex templates/latex/hpotter/before_chapters.tex templates/latex/hpotter/halftitle.tex templates/latex/hpotter/titlepage.tex
CLASSIC_FILES = templates/latex/hpmor.sty templates/latex/classic/classic.sty templates/latex/hpmor.tex templates/latex/classic/before_chapters.tex templates/latex/classic/disclaimer.tex templates/latex/classic/titlepage.tex

.PHONY: update
# download new chapters from hpmor.com
update:
	python script/hpmor-scrape.py

html-dump: update

markdown: $(MARKDOWN_TARGETS)

latex: $(LATEX_TARGETS)

html: $(HTML_TARGETS)

latex/%.tex: markdown/%.md
	pandoc --chapters -o latex/$*.tex markdown/$*.md

# to prevent accidental overriding of formatting fixes, markdown files
# do not require html-dump files
markdown/%.md:
	pandoc -o markdown/$*.md html-dump/$*.htm

html/%.htm: markdown/%.md
	pandoc -o html/$*.htm markdown/$*.md

# xelatex generated pdf's
pdf: pdf/luminosity.pdf
#pdf: pdf/hpmor-trade-hpotter.pdf pdf/hpmor-trade-classic.pdf

#pdf/hpmor-trade-hpotter.pdf: $(LATEX_TARGETS) $(HPOTTER_FILES)
#	mkdir -p .build
#	python script/hpmor-convert.py --format pdf -o hpmor-trade-hpotter --style-class ../templates/latex/hpotter/hpotter --font-size 11 --paper ebook --double-sided
#	mv -f .build/hpmor-trade-hpotter.pdf pdf

pdf/luminosity.pdf: $(LATEX_TARGETS) $(CLASSIC_FILES)
	mkdir -p .build
	python script/hpmor-convert.py --format pdf -o hpmor-trade-classic --style-class classic --font-size 11 --paper-size a5paper --double-sided
	mv -f .build/hpmor-trade-classic.pdf pdf/luminosity.pdf

# layout tests
.build/hpotter-test.pdf: $(LATEX_TARGETS) $(HPOTTER_FILES)
	mkdir -p .build
	python script/hpmor-convert.py --start-chapter 72 --end-chapter 73 --format pdf -o hpotter-test --style-class hpotter --font-size 11 --paper ebook --double-sided

.build/classic-test.pdf: $(LATEX_TARGETS) $(CLASSIC_FILES)
	mkdir -p .build
	python script/hpmor-convert.py --start-chapter 72 --end-chapter 73 --format pdf -o classic-test --style-class classic --font-size 10 --paper ebook --double-sided

.PHONY: all
# download chapters and re-build all formats
all: update markdown latex html pdf

.PHONY: clean
clean:
	-rm -r .build
