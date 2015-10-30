# makefile to convert between different formats
# 'make update' downloads new chapters
# 'make all' downloads new chapters and builds all formats

# recursive rather than immediate expansion is used because
# the list of files must be up to date after new chapters are downloaded
DUMP_FILES = $(wildcard html-dump/*.htm)
MARKDOWN_TARGETS = $(DUMP_FILES:html-dump/%.htm=markdown/%.md)
LATEX_TARGETS = $(MARKDOWN_TARGETS:markdown/%.md=latex/%.tex)
HTML_TARGETS = $(MARKDOWN_TARGETS:markdown/%.md=html/%.htm)
CLASSIC_FILES = templates/latex/bookforprint.sty templates/latex/classic/classic.sty templates/latex/bookforprint.tex templates/latex/classic/before_chapters.tex templates/latex/classic/disclaimer.tex templates/latex/classic/titlepage.tex

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
pdf: pdf/book.pdf
#pdf: pdf/hpmor-trade-hpotter.pdf pdf/hpmor-trade-classic.pdf

pdf/book.pdf: $(LATEX_TARGETS) $(CLASSIC_FILES)
	mkdir -p .build
	python script/convert.py --format pdf -o out --style-class classic --font-size 10 --paper-size a5paper --double-sided
	mv -f .build/out.pdf pdf/book.pdf

.build/classic-test.pdf: $(LATEX_TARGETS) $(CLASSIC_FILES)
	mkdir -p .build
	python script/convert.py --start-chapter 72 --end-chapter 73 --format pdf -o classic-test --style-class classic --font-size 10 --paper ebook --double-sided

.PHONY: all
# download chapters and re-build all formats
all: update markdown latex html pdf

.PHONY: clean
clean:
	-rm -r .build
