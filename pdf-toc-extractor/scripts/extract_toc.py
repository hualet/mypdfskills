#!/usr/bin/env python3
"""
Extract table of contents (outline/bookmarks) from PDF files.
"""

import sys
import json
from PyPDF2 import PdfReader
from typing import Dict, List, Optional


def extract_pdf_toc(pdf_path: str) -> List[Dict]:
    """
    Extract table of contents from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of dictionaries containing TOC entries with title, page number, and level
    """
    try:
        reader = PdfReader(pdf_path)

        # Get the outline (bookmarks)
        outline = reader.outline

        if not outline:
            return []

        # Convert outline to a structured list
        toc = []
        process_outline_items(outline, toc)

        return toc

    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        return []


def process_outline_items(items: List, toc: List[Dict], level: int = 0) -> None:
    """
    Recursively process outline items and add them to TOC list.

    Args:
        items: List of outline items
        toc: TOC list to populate
        level: Current nesting level (0 for root)
    """
    for item in items:
        if isinstance(item, dict):
            # This is a destination with a title
            toc_item = {
                'title': item.get('/Title', ''),
                'pageNumber': get_page_number(item),
                'level': level
            }
            toc.append(toc_item)

            # Check if this item has children
            if '/Kids' in item:
                process_outline_items(item['/Kids'], toc, level + 1)

        elif isinstance(item, list):
            # This is a list of items (nested)
            process_outline_items(item, toc, level + 1)


def get_page_number(destination) -> Optional[int]:
    """
    Extract page number from a destination object.

    Args:
        destination: PyPDF2 destination object

    Returns:
        Page number (1-indexed) or None
    """
    try:
        # The destination object has a page reference
        if '/Page' in destination:
            page_ref = destination['/Page']
            # Get the page index and add 1 to make it 1-indexed
            page_num = page_ref.id.num + 1
            return page_num
        return None
    except:
        return None


def toc_to_text(toc: List[Dict]) -> str:
    """
    Convert TOC list to a formatted text representation.

    Args:
        toc: List of TOC entries

    Returns:
        Formatted text representation
    """
    if not toc:
        return "No table of contents found in this PDF."

    lines = ["\nPDF Table of Contents:\n"]
    lines.append("=" * 50)

    for item in toc:
        indent = "  " * item['level']
        page_str = f"Page {item['pageNumber']}" if item['pageNumber'] else "Unknown page"
        line = f"{indent}{item['title']} - {page_str}"
        lines.append(line)

    return "\n".join(lines)


def toc_to_json(toc: List[Dict], pretty: bool = True) -> str:
    """
    Convert TOC list to JSON string.

    Args:
        toc: List of TOC entries
        pretty: Whether to pretty-print the JSON

    Returns:
        JSON string representation
    """
    if pretty:
        return json.dumps(toc, indent=2, ensure_ascii=False)
    return json.dumps(toc, ensure_ascii=False)


def main():
    """
    Main function for CLI usage.
    """
    if len(sys.argv) < 2:
        print("Usage: python extract_toc.py [OPTIONS] <pdf_file>", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  --json    Output as JSON instead of text", file=sys.stderr)
        print("  --pretty  Pretty-print JSON output", file=sys.stderr)
        sys.exit(1)

    # Parse arguments
    pdf_path = sys.argv[-1]
    output_json = '--json' in sys.argv
    pretty_print = '--pretty' in sys.argv

    # Extract TOC
    toc = extract_pdf_toc(pdf_path)

    # Output result
    if output_json:
        print(toc_to_json(toc, pretty_print))
    else:
        print(toc_to_text(toc))


if __name__ == "__main__":
    main()