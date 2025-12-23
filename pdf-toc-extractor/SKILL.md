---
name: pdf-toc-extractor
description: Extract table of contents/bookmarks from PDF files. Use when users need to get the outline structure, bookmarks hierarchies, or document navigation structure from PDFs for generating document outlines, creating navigation indexes, analyzing document structure, or converting TOC to different formats.
---

# PDF Table of Contents Extractor

## Overview

This skill extracts hierarchical table of contents (bookmarks/outlines) from PDF documents, providing structured navigation data including titles, page numbers, and nesting levels. It includes both extraction of existing PDF bookmarks and **automatic detection of table of contents pages** for PDFs without embedded bookmarks by locating and parsing actual TOC pages within the document.

### Key Features
- **Bookmark Extraction**: Extract existing PDF bookmarks/outline structure
- **TOC Page Detection**: Find and parse actual table of contents pages in documents
- **Pattern Recognition**: Detect various TOC formats (dots, tabs, spaces, numbering)
- **Enhanced Parsing**: Handle Roman numerals, multi-level numbering, and special formats
- **Confidence Scoring**: Get confidence levels for detected TOC entries
- **Flexible Thresholds**: Control detection sensitivity
- **Multiple Output Formats**: Text, JSON, and Markdown formats supported

## Implementation Workflow: Extract TOC from First 10 Pages

This skill implements a comprehensive solution to extract table of contents from PDF documents by analyzing the first 10 pages. The implementation combines AI-powered pattern recognition with Python scripts for robust TOC detection.

### Architecture Overview

The implementation follows a three-tier approach:

1. **AI Analysis Layer**: Uses Claude to understand document structure and identify TOC patterns
2. **Pattern Detection Layer**: Python scripts with regex patterns for various TOC formats
3. **Validation Layer**: Confidence scoring and cross-validation of detected entries

### Step-by-Step Implementation

#### Step 1: Initial Document Analysis (AI)
```
When a PDF is provided, first analyze its structure:
1. Check if the PDF has existing bookmarks/outline
2. If no bookmarks exist, proceed to analyze the first 10 pages
3. Look for TOC indicators like:
   - Pages titled "Table of Contents", "Contents", "Index"
   - Sequential numbered entries
   - Dot leaders (......) or tab-separated content
```

#### Step 2: Pattern-Based Detection (Scripts)
Use the `toc_pattern_matcher.py` script to detect TOC patterns:

```python
# Detection patterns include:
- Dot leader: "Chapter 1 Introduction......12"
- Tab-based: "Chapter 1\t12"
- Space-aligned: "Chapter 1    12"
- Numbered: "1.1 Introduction    15"
- Roman numerals: "i, ii, iii, iv, v"
```

#### Step 3: Page Analysis (Scripts)
The `toc_page_analyzer.py` analyzes each of the first 10 pages:

```python
# Page analysis includes:
- Text extraction with positional information
- Line-by-line pattern matching
- Confidence scoring for each detected entry
- Multi-page TOC detection for spanning TOCs
```

#### Step 4: Entry Extraction and Validation
Combine AI insights with script outputs:

```python
# Validation criteria:
- Minimum 2 valid entries per page
- Sequential page numbers (optional, with gaps allowed)
- Consistent formatting patterns
- Confidence threshold (default 0.6)
```

### Quick Start

#### Prerequisites
Install dependencies using uv:
```bash
uv pip install -r scripts/requirements.txt
```

#### Extracting Existing Bookmarks
Use the extraction script to get existing bookmarks from any PDF:

```bash
# Basic text output
python scripts/extract_toc.py document.pdf

# JSON output
python scripts/extract_toc.py --json document.pdf

# Pretty-printed JSON
python scripts/extract_toc.py --json --pretty document.pdf
```

#### Detecting Table of Contents Pages
For PDFs without bookmarks, use TOC page detection to locate and parse actual table of contents pages:

```bash
# Auto-detect and parse TOC pages (first 10 pages)
python scripts/extract_toc.py --detect-toc document.pdf

# Set confidence threshold (0-1) for detection sensitivity
python scripts/extract_toc.py -d -t 0.8 document.pdf

# Output with confidence scores visible
python scripts/extract_toc.py -d --json document.pdf
```

### Advanced Usage

#### Custom Pattern Detection
For documents with unique TOC formats, extend the pattern matching:

```python
from scripts.toc_pattern_matcher import TOCPatternMatcher, TOCFormat

# Add custom pattern
matcher = TOCPatternMatcher()
custom_pattern = r'^(Chapter\s+\d+:\s+.*?)\.{3,}(\d+)$'
# Chapter 1: Introduction......12
```

#### Multi-Page TOC Analysis
For TOCs spanning multiple pages:

```python
from scripts.toc_page_analyzer import TOCPAGEAnalyzer

analyzer = TOCPAGEAnalyzer()
# Analyze first 10 pages (default)
results = analyzer.analyze_pdf("document.pdf", max_pages=10)

# Combine results from multiple pages
combined_entries = []
for result in results:
    combined_entries.extend(result.entries)
```

## Core Capabilities

### 1. Extract Table of Contents Structure

The script extracts both existing bookmarks and detects table of contents pages:
- **Bookmark Extraction**: Captures existing PDF outlines from document metadata
- **TOC Page Detection**: Locates actual table of contents pages and parses their contents
- Chapter/section titles with page numbers and nested structure levels
- Confidence scores for detected entries indicating reliability
- Support for various TOC formats (dot leaders, tabs, spaces, numbering)

### 2. Multiple Output Formats

Choose between human-readable text or structured JSON:
- **Text format**: Indented outline with page numbers
- **JSON format**: Machine-readable structure with metadata for programmatic use
- **Auto-detected format**: Includes confidence scores and detection methods

### 3. TOC Page Detection Features

Supports PDFs with:
- Early page analysis (first 10 pages) for performance
- Dot leader patterns ("Chapter 1 Introduction......12")
- Tab-separated entries ("Chapter 1	12")
- Space-aligned formats ("Chapter 1    12")
- Numbered sections ("1.1 Introduction    15")
- Roman numerals and multi-digit numbering
- Page confidence scoring for validation
- Various PDF encoding schemes and document structures
- Academic papers, books, technical manuals

### 4. Pattern Recognition Technology

**Format Detection**:
- Multiple pattern recognition engines
- Dot leader, tab, and space-based alignment
- Numbered section matching (1, 1.1, 1.1.1)
- Roman numeral support (i, ii, iii, iv, v)
- Hybrid format detection for complex layouts

**Page Analysis**:
- Focused analysis of first 10 pages
- Content density evaluation
- Sequential page number validation
- Page-level confidence scoring

**Reliability Measures**:
- Each detected TOC entry includes confidence score
- Format-specific detection accuracy
- Multi-pattern cross-validation
- Adjustable detection thresholds

## Integration Examples

### Extract TOC for Analysis
```python
from scripts.extract_toc import extract_pdf_toc, toc_to_json

# Extract existing bookmarks
toc_data = extract_pdf_toc("report.pdf")

# Detect TOC pages (if no bookmarks exist)
toc_data = extract_pdf_toc("document.pdf", auto_detect_toc=True, toc_page_threshold=0.6)

# Convert to JSON
json_format = toc_to_json(toc_data, pretty=True)
print(json_format)
```

### Command Line Options

**Basic Options**:
- `pdf_file`: Path to the PDF file (required argument)
- `--json / -j`: Output as JSON instead of text
- `--pretty / -p`: Pretty-print JSON output

**TOC Page Detection Options**:
- `--detect-toc / -d`: Enable TOC page detection for PDFs without bookmarks
- `--toc-threshold / -t`: Set detection confidence threshold (0.0-1.0, default 0.6)
  - Lower values (0.3-0.6): More inclusive detection
  - Higher values (0.7-0.9): More selective detection
- `--quiet / -q`: Suppress progress messages

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
- `pdfplumber>=0.9.0`: For precise text extraction from PDF pages
- `pandas>=1.3.0`: For data processing and analysis

All dependencies are listed in `scripts/requirements.txt`.

### Performance and Limitations

**Performance**:
- Typically analyzes first 10 pages for efficiency
- Multi-pattern matching for accuracy and speed
- Memory-efficient processing for large documents

**Limitations**:
- Works best with traditional TOC layouts
- Scanned PDFs require OCR preprocessing
- Complex or non-standard formats may need preprocessing
- First 10 pages approach may miss TOCs in later pages

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

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources. This skill includes demo and test files to demonstrate functionality. Useful test utilities and examples can be kept. Run the demo script for a tour of features: `python demo_auto_generation.py`