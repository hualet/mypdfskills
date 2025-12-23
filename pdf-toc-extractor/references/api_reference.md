# PDF TOC Extractor API Reference

This document provides detailed API documentation for the PDF Table of Contents extraction functionality.

## Functions

### extract_pdf_toc(pdf_path: str, auto_generate: bool = False, confidence_threshold: float = 0.7, quiet: bool = False)

Extracts the table of contents from a PDF file. Can also generate TOC for PDFs without bookmarks by analyzing document structure, typography, and content patterns.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `auto_generate` (bool): If True, generate TOC for PDFs without bookmarks (default: False)
- `confidence_threshold` (float): Minimum confidence score for generated entries, range 0-1 (default: 0.7)
- `quiet` (bool): Suppress warning messages (default: False)

**Returns:**
- List[Dict]: Array of TOC entries with the following structure:
  ```python
  # For extracted bookmarks
  {
      'title': str,        # Bookmark/Chapter title
      'pageNumber': int,   # Page number (1-indexed)
      'level': int         # Nesting level (0 for root items)
  }

  # For auto-generated entries (includes additional metadata)
  {
      'title': str,            # Heading title
      'pageNumber': int,       # Page number (1-indexed)
      'level': int,            # Nesting level (0 for root items)
      'confidence': float,     # Confidence score (0.0 - 1.0)
      'detection_method': str  # Method used for detection (e.g., 'font_size|text_pattern')
  }
  ```

**Example:**
```python
from scripts.extract_toc import extract_pdf_toc

toc_data = extract_pdf_toc("document.pdf")
for item in toc_data:
    print(f"{'  ' * item['level']}- {item['title']} (Page {item['pageNumber']})")
```

**Error Handling:**
- Returns empty list if PDF has no bookmarks
- Handles various PDF encoding schemes
- Handles corrupted or protected PDFs (returns empty list)

---

### toc_to_text(toc: List[Dict])

Converts TOC data to a formatted text representation.

**Parameters:**
- `toc` (List[Dict]): TOC data from extract_pdf_toc()

**Returns:**
- str: Formatted text outline

**Example:**
```python
from scripts.extract_toc import extract_pdf_toc, toc_to_text

toc_data = extract_pdf_toc("document.pdf")
text_output = toc_to_text(toc_data)
print(text_output)
```

---

### toc_to_json(toc: List[Dict], pretty: bool = True)

Converts TOC data to JSON format.

**Parameters:**
- `toc` (List[Dict]): TOC data from extract_pdf_toc()
- `pretty` (bool): Whether to pretty-print the JSON (default: True)

**Returns:**
- str: JSON string representation of TOC

**Example:**
```python
from scripts.extract_toc import extract_pdf_toc, toc_to_json

toc_data = extract_pdf_toc("document.pdf")
json_output = toc_to_json(toc_data, pretty=True)
print(json_output)
```

## Troubleshooting

### Common Issues

**"No table of contents found in this PDF"**
- The PDF may not have bookmarks/outlines
- Some PDFs embed TOC in the document text rather than as bookmarks
- Try examining the document visually for any embedded TOC

**Page numbers showing as "Unknown page"**
- Certain PDF formats don't properly store page references
- PDF may be corrupted or use non-standard encoding
- Some PDF creators don't properly link bookmarks to pages

**Unicode errors in titles**
- The script handles UTF-8 encoding by default
- If characters appear garbled, the PDF may use a special encoding

**Auto-Generation Example:**
```python
from scripts.extract_toc import extract_pdf_toc

# Auto-generate TOC for PDFs without bookmarks
toc_data = extract_pdf_toc("document.pdf", auto_generate=True, confidence_threshold=0.7)

# Check confidence scores for generated entries
for item in toc_data:
    print(f"{item['title']}: {item.get('confidence', 1.0):.2f} confidence")
    print(f"  Detected via: {item.get('detection_method', 'bookmark')}")
```

---

### toc_to_text(toc: List[Dict], show_confidence: bool = False)

Converts TOC data to a formatted text representation.

**Parameters:**
- `toc` (List[Dict]): TOC data from extract_pdf_toc()
- `show_confidence` (bool): Whether to show confidence scores for generated entries (default: False)

**Returns:**
- str: Formatted text outline

**Example:**
```python
from scripts.extract_toc import extract_pdf_toc, toc_to_text

# Basic text output
toc_data = extract_pdf_toc("document.pdf")
text_output = toc_to_text(toc_data)
print(text_output)

# Show confidence scores for auto-generated TOC
toc_data = extract_pdf_toc("document.pdf", auto_generate=True)
text_output = toc_to_text(toc_data, show_confidence=True)
print(text_output)
```

**Formatting**
```python
toc_data = extract_pdf_toc("document.pdf")
# Get only top-level chapters
chapters = [item for item in toc_data if item['level'] == 0]
```

**Creating a Navigation Map**
```python
import json

toc_data = extract_pdf_toc("document.pdf")
# Create a hierarchical dictionary
navigation = {'chapters': []}
current_chapter = None

for item in toc_data:
    if item['level'] == 0:
        current_chapter = {'title': item['title'], 'sections': []}
        navigation['chapters'].append(current_chapter)
    elif item['level'] == 1 and current_chapter:
        current_chapter['sections'].append(item['title'])

print(json.dumps(navigation, indent=2))
```

**Handling Large PDFs**
For PDFs with extensive TOCs (1000+ items):
- Consider processing in chunks if needed
- The script has been tested with files containing thousands of bookmarks
- For very large PDFs, there may be a slight delay during extraction

## Troubleshooting

### Common Issues

**"No table of contents found in this PDF"**
- The PDF may not have bookmarks/outlines
- Some PDFs embed TOC in the document text rather than as bookmarks
- Try using `--generate-if-missing` to analyze document content
- Try examining the document visually for any embedded TOC

**"Auto-generation not available (required modules not installed)"**
- Ensure `pdfplumber` and `pandas` are installed: `pip install -r scripts/requirements.txt`
- Check Python version compatibility (3.6+)

**"Low confidence scores in generated TOC"**
- Increase confidence threshold: `--confidence-threshold 0.8`
- PDF may have unusual formatting; try manual examination
- Reduce threshold for more inclusive results: `--confidence-threshold 0.5`

**Page numbers showing as "Unknown page"**
- Generated TOC doesn't have exact page references
- PDF may be corrupted or use non-standard encoding
- Some PDF creators don't properly store page references

**Unicode errors in titles**
- The script handles UTF-8 encoding by default
- If characters appear garbled, the PDF may use a special encoding