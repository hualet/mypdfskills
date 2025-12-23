---
name: pdf-toc-extractor
description: Extract table of contents/bookmarks from PDF files. Use when users need to get the outline structure, bookmarks hierarchies, or document navigation structure from PDFs for generating document outlines, creating navigation indexes, analyzing document structure, or converting TOC to different formats.
---

# PDF Table of Contents Extractor

## Overview

This skill extracts hierarchical table of contents (bookmarks/outlines) from PDF documents, providing structured navigation data including titles, page numbers, and nesting levels. It includes Python scripts for automating TOC extraction with various output formats.

## Quick Start

Use the extraction script to get TOC from any PDF:

```bash
# Basic text output
python scripts/extract_toc.py document.pdf

# JSON output
python scripts/extract_toc.py --json document.pdf

# Pretty-printed JSON
python scripts/extract_toc.py --json --pretty document.pdf
```

## Core Capabilities

### 1. Extract Table of Contents Structure

The script extracts hierarchical bookmarks/outlines from PDFs, capturing:
- Chapter/section titles
- Corresponding page numbers
- Nested structure levels
- Any metadata associated with bookmarks

### 2. Multiple Output Formats

Choose between human-readable text or structured JSON:
- **Text format**: Indented outline with page numbers
- **JSON format**: Machine-readable structure for further processing

### 3. Handle Complex PDFs

Supports PDFs with:
- Nested bookmark hierarchies
- Missing or incomplete TOC data
- Various PDF encoding schemes

## Integration Examples

### Extract TOC for Analysis
```python
from scripts.extract_toc import extract_pdf_toc, toc_to_json

toc_data = extract_pdf_toc("report.pdf")
json_format = toc_to_json(toc_data, pretty=True)
print(json_format)
```

### Convert to Other Formats
Use the extracted TOC as input for:
- Markdown documentation
- HTML navigation menus
- Video chapters
- Document indices

## References

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
