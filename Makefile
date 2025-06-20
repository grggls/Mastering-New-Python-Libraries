.PHONY: help notebook pdf clean install sync test validate test-conversion validate-notebook

# Default target
help:
	@echo "Available targets:"
	@echo "  notebook        - Convert README.md to interactive Jupyter notebook"
	@echo "  pdf             - Build PDF from README.md using Pandoc"
	@echo "  install         - Install project dependencies with Rye"
	@echo "  sync            - Sync Rye environment"
	@echo "  test            - Run code validation tests"
	@echo "  test-conversion - Test conversion script with various edge cases"
	@echo "  validate        - Validate code blocks and conversion"
	@echo "  validate-notebook - Execute and validate the generated notebook"
	@echo "  all             - Build both notebook and PDF"
	@echo "  ci              - Run full CI pipeline (test + build)"

# Convert README to Jupyter notebook
notebook:
	@echo "🔄 Converting README.md to Jupyter notebook..."
	python3 -m library_exploration.convert_to_notebook README.md -o Mastering-New-Python-Libraries.ipynb
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

# Run code validation tests
test:
	@echo "🧪 Running code validation tests..."
	python3 -m library_exploration.test_code_blocks

# Test conversion script with edge cases
test-conversion:
	@echo "🧪 Testing conversion script with edge cases..."
	python3 -m library_exploration.test_conversion

# Test conversion script with verbose output
test-conversion-verbose:
	@echo "🧪 Testing conversion script with verbose output..."
	python3 -m library_exploration.test_conversion --verbose

# Validate code blocks and conversion
validate: test
	@echo "🔍 Validating conversion..."
	python3 -m library_exploration.convert_to_notebook README.md -o test-notebook.ipynb
	@echo "✅ Validation complete"

# Execute and validate the generated notebook
validate-notebook:
	@echo "🔍 Executing and validating notebook..."
	python3 -m library_exploration.validate_notebook Mastering-New-Python-Libraries.ipynb
	@echo "✅ Notebook validation complete"

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	rm -f Mastering-New-Python-Libraries.ipynb
	rm -f Mastering-New-Python-Libraries.pdf
	rm -f test-notebook.ipynb
	rm -f test_*.ipynb
	@echo "✅ Cleaned"

# Build everything
all: notebook pdf
	@echo "🎉 All builds completed!"

# Full CI pipeline
ci: test test-conversion validate notebook validate-notebook pdf
	@echo "🚀 Full CI pipeline completed!"

# Watch for changes and rebuild notebook
watch-notebook:
	@echo "👀 Watching README.md for changes..."
	@while inotifywait -e modify README.md; do \
		echo "🔄 README.md changed, rebuilding notebook..."; \
		make notebook; \
	done 