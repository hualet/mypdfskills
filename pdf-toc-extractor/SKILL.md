---
name: pdf-toc-extractor
description: Extract table of contents/bookmarks from PDF files. Use when users need to get the outline structure, bookmarks hierarchies, or document navigation structure from PDFs for generating document outlines, creating navigation indexes, analyzing document structure, or converting TOC to different formats.
---

# PDF Table of Contents Extractor

## Overview

This skill extracts hierarchical table of contents (bookmarks/outlines) from PDF documents, providing structured navigation data including titles, page numbers, and nesting levels. It includes both extraction of existing PDF bookmarks and **automatic generation** of table of contents for PDFs without embedded bookmarks by analyzing document structure, typography, and content patterns.

### Key Features
- **Bookmark Extraction**: Extract existing PDF bookmarks/outline structure
- **Auto-Generation**: Generate TOC for PDFs without bookmarks using AI-powered analysis
- **Confidence Scoring**: Get confidence levels for generated TOC entries
- **Multiple Output Formats**: Text, JSON, and Markdown formats supported
- **Typography Analysis**: Analyzes font sizes, styles, and text patterns to identify headings
- **Pattern Recognition**: Detects numbered chapters, sections, and title formatting
- **Adjustable Sensitivity**: Control the balance between accuracy and coverage with confidence thresholds

## Quick Start

### Extracting Existing Bookmarks
Use the extraction script to get existing bookmarks from any PDF:

```bash
# Basic text output
python scripts/extract_toc.py document.pdf

# JSON output
python scripts/extract_toc.py --json document.pdf

# Pretty-printed JSON
python scripts/extract_toc.py --json --pretty document.pdf
```

### Auto-Generating Table of Contents
For PDFs without bookmarks, use the auto-generation feature to analyze document structure and create a table of contents:

```bash
# Auto-generate TOC with default settings
python scripts/extract_toc.py --generate-if-missing document.pdf

# Set confidence threshold (0-1) for more accurate results
python scripts/extract_toc.py -g -c 0.8 document.pdf

# Output with confidence scores visible
python scripts/extract_toc.py --generate-if-missing --json document.pdf
```

## Core Capabilities

### 1. Extract Table of Contents Structure

The script extracts both existing bookmarks and generates new ones by analyzing document content:
- **Bookmark Extraction**: Captures existing PDF outlines from document metadata
- **Automatic Generation**: Creates TOC by analyzing typography, patterns, and layout
- Chapter/section titles with page numbers and nested structure levels
- Confidence scores for generated entries indicating reliability
- Detection method metadata showing how each entry was identified

### 2. Multiple Output Formats

Choose between human-readable text or structured JSON:
- **Text format**: Indented outline with page numbers
- **JSON format**: Machine-readable structure with metadata for programmatic use
- **Auto-generated format**: Includes confidence scores and detection methods

### 3. Handle Complex PDFs

Supports PDFs with:
- Nested bookmark hierarchies (extracted or generated)
- Missing or incomplete TOC data
- Various PDF encoding schemes and document structures
- Different heading styles and formats (numbered, named, etc.)

### 4. Advanced Auto-Generation Features

**Typography Analysis**:
- Automatic font size detection and analysis
- Style variations (bold, italic, weight differences)
- Position-based hierarchy inference

**Pattern Recognition**:
- Numbered patterns: 1, 1.1, 1.1.1, etc.
- Named patterns: Chapter, Section, Part, etc.
- Roman numerals and letter-based numbering
- Uppercase and title case detection

**Confidence Scoring**:
- Each generated TOC entry includes a confidence score (0-1)
- Transparent detection method reporting
- Configurable threshold to balance accuracy vs coverage

## Integration Examples

### Extract TOC for Analysis
```python
from scripts.extract_toc import extract_pdf_toc, toc_to_json

# Extract existing bookmarks
toc_data = extract_pdf_toc("report.pdf")

# Generate TOC from content (if no bookmarks exist)
toc_data = extract_pdf_toc("document.pdf", auto_generate=True, confidence_threshold=0.7)

# Convert to JSON
json_format = toc_to_json(toc_data, pretty=True)
print(json_format)
```

### Command Line Options

**Basic Options**:
- `--pdf_file`: Path to the PDF file (required argument)
- `--json / -j`: Output as JSON instead of text
- `--pretty / -p`: Pretty-print JSON output

**Auto-Generation Options**:
- `--generate-if-missing / -g`: Enable TOC generation for PDFs without bookmarks
- `--confidence-threshold / -c`: Set confidence threshold (0.0-1.0, default: 0.7)
  - Lower values (0.5-0.7): More inclusive, may include false positives
  - Higher values (0.8-1.0): More selective, reduces false positives
- `--quiet / -q`: Suppress warning messages

### Convert to Other Formats
Use the extracted TOC as input for:
- Markdown documentation
- HTML navigation menus
- Video chapters
- Document indices

## References

### Dependencies and Requirements

The skill requires the following Python packages:
- `PyPDF2>=3.0.0`: For PDF bookmark extraction
- `pdfplumber>=0.9.0`: For PDF structure analysis
- `pandas>=1.3.0`: For data processing and analysis

All dependencies are listed in `scripts/requirements.txt`.

### Performance and Limitations

**Performance**:
- Auto-generation typically takes 1-5 seconds per PDF page (depending on content density)
- Memory-efficient design for processing large documents

**Limitations**:
- Heavily formatted PDFs (with complex layouts) may require adjustment of confidence thresholds
- Subtle heading distinctions may be missed
- Multi-column documents are partially supported

See [references/api_reference.md](references/api_reference.md) for:
- Detailed API documentation
- Advanced usage patterns
- Error handling guidance

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Claude for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Claude's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Claude should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Claude produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
