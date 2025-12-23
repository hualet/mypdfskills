# PDF TOC Extractor API Reference

This document provides detailed API documentation for the PDF Table of Contents extraction functionality.

## Functions

### extract_pdf_toc(pdf_path: str)

Extracts the table of contents from a PDF file.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
- List[Dict]: Array of TOC entries with the following structure:
  ```python
  {
      'title': str,        # Bookmark/Chapter title
      'pageNumber': int,   # Page number (1-indexed)
      'level': int         # Nesting level (0 for root items)
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

### Advanced Usage Patterns

**Filtering by Level**
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