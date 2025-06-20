.PHONY: help notebook pdf clean install sync

# Default target
help:
	@echo "Available targets:"
	@echo "  notebook    - Convert README.md to interactive Jupyter notebook"
	@echo "  pdf         - Build PDF from README.md using Pandoc"
	@echo "  install     - Install project dependencies with Rye"
	@echo "  sync        - Sync Rye environment"
	@echo "  clean       - Clean generated files"
	@echo "  all         - Build both notebook and PDF"

# Convert README to Jupyter notebook
notebook:
	@echo "🔄 Converting README.md to Jupyter notebook..."
	python3 convert_to_notebook.py README.md -o Mastering-New-Python-Libraries.ipynb
	@echo "✅ Notebook created: Mastering-New-Python-Libraries.ipynb"

# Build PDF from README
pdf:
	@echo "🔄 Building PDF from README.md..."
	pandoc README.md \
		--pdf-engine=xelatex \
		--variable=geometry:margin=1in \
		--variable=fontsize:11pt \
		--variable=mainfont:"DejaVu Sans" \
		--variable=monofont:"DejaVu Sans Mono" \
		--variable=colorlinks:true \
		--variable=linkcolor:blue \
		--variable=urlcolor:blue \
		--variable=toccolor:gray \
		--toc \
		--number-sections \
		--output=Mastering-New-Python-Libraries.pdf
	@echo "✅ PDF created: Mastering-New-Python-Libraries.pdf"

# Install dependencies
install:
	@echo "🔄 Installing dependencies with Rye..."
	rye sync
	@echo "✅ Dependencies installed"

# Sync Rye environment
sync:
	@echo "🔄 Syncing Rye environment..."
	rye sync
	@echo "✅ Environment synced"

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	rm -f Mastering-New-Python-Libraries.ipynb
	rm -f Mastering-New-Python-Libraries.pdf
	@echo "✅ Cleaned"

# Build everything
all: notebook pdf
	@echo "🎉 All builds completed!"

# Watch for changes and rebuild notebook
watch-notebook:
	@echo "👀 Watching README.md for changes..."
	@while inotifywait -e modify README.md; do \
		echo "🔄 README.md changed, rebuilding notebook..."; \
		make notebook; \
	done 