#!/usr/bin/env python3
"""
Extract table of contents (outline/bookmarks) from PDF files.
Includes automatic generation for PDFs without embedded bookmarks.
"""

import sys
import json
from PyPDF2 import PdfReader
from typing import Dict, List, Optional
from argparse import ArgumentParser

# Import modules locally for TOC generation
try:
    from heading_detector import HeadingDetector
    from pdf_analyzer import PDFAnalyzer
    from toc_generator import TOCGenerator
    AUTO_GENERATE_AVAILABLE = True
except ImportError:
    AUTO_GENERATE_AVAILABLE = False


def extract_pdf_toc(pdf_path: str, auto_generate: bool = False,
                   confidence_threshold: float = 0.7, quiet: bool = False) -> List[Dict]:
    """
    Extract table of contents from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        auto_generate: If True, attempt to generate TOC for PDFs without bookmarks
        confidence_threshold: Minimum confidence for generated TOC entries (0-1)
        quiet: Suppress warning messages

    Returns:
        List of dictionaries containing TOC entries with title, page number, and level
    """
    try:
        # First try standard bookmark extraction
        toc = extract_bookmarks(pdf_path)

        # If no bookmarks found and auto-generation is enabled, try that
        if not toc and auto_generate and AUTO_GENERATE_AVAILABLE:
            if not quiet:
                print("No bookmarks found. Attempting to generate table of contents...", file=sys.stderr)
            toc = generate_toc_from_content(pdf_path, confidence_threshold)
            if toc and not quiet:
                print(f"Generated {len(toc)} TOC entries with confidence threshold {confidence_threshold}", file=sys.stderr)
        elif not toc and auto_generate and not AUTO_GENERATE_AVAILABLE:
            if not quiet:
                print("Auto-generation not available (required modules not installed)", file=sys.stderr)

        return toc

    except Exception as e:
        if not quiet:
            print(f"Error reading PDF: {e}", file=sys.stderr)
        return []


def extract_bookmarks(pdf_path: str, quiet: bool = False) -> List[Dict]:
    """
    Extract bookmarks from PDF using PyPDF2.

    Args:
        pdf_path: Path to the PDF file
        quiet: Suppress warnings

    Returns:
        List of bookmarks
    """
    try:
        reader = PdfReader(pdf_path)
        outline = reader.outline

        if not outline:
            return []

        # Convert outline to a structured list
        toc = []
        process_outline_items(outline, toc)
        return toc

    except Exception as e:
        if not quiet:
            print(f"Error reading bookmarks: {e}", file=sys.stderr)
        return []


def generate_toc_from_content(pdf_path: str, confidence_threshold: float = 0.7) -> List[Dict]:
    """
    Generate TOC by analyzing PDF content structure.

    Args:
        pdf_path: Path to the PDF file
        confidence_threshold: Minimum confidence for TOC entries

    Returns:
        Generated TOC list
    """
    if not AUTO_GENERATE_AVAILABLE:
        raise Exception("TOC generation modules not available")

    try:
        # Analyze PDF structure
        analyzer = PDFAnalyzer()
        pdf_data = analyzer.analyze_pdf(pdf_path)

        if not pdf_data.get('text_elements'):
            return []

        # Detect headings
        detector = HeadingDetector(confidence_threshold)
        headings = detector.detect_headings(pdf_data['text_elements'])

        if not headings:
            return []

        # Generate TOC
        generator = TOCGenerator(confidence_threshold)
        toc = generator.generate_toc(headings)

        # Convert to standard format
        formatted_toc = []
        for entry in toc:
            # Ensure consistent format with PyPDF2 bookmarks
            formatted_entry = {
                'title': entry['title'],
                'pageNumber': entry['pageNumber'],
                'level': entry['level'],
                'confidence': entry['confidence'],
                'detection_method': entry.get('detection_method', 'unknown')
            }
            formatted_toc.append(formatted_entry)

        return formatted_toc

    except Exception as e:
        raise Exception(f"Error generating TOC: {str(e)}")


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


def toc_to_text(toc: List[Dict], show_confidence: bool = False) -> str:
    """
    Convert TOC list to a formatted text representation.

    Args:
        toc: List of TOC entries
        show_confidence: Whether to include confidence scores for generated entries

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

        # Add confidence if requested and available
        if show_confidence and 'confidence' in item:
            line += f" [{item['confidence']:.2f}]"

        lines.append(line)

        # Add detection method if available
        if 'detection_method' in item and item['detection_method'] != 'unknown':
            lines.append(f"{indent}  (Detected via: {item['detection_method']})")

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
    parser = ArgumentParser(description="Extract or generate table of contents from PDF files")
    parser.add_argument("pdf_file", help="Path to the PDF file")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON instead of text")
    parser.add_argument("--pretty", action="store_true",
                       help="Pretty-print JSON output")
    parser.add_argument("--generate-if-missing", "-g", action="store_true",
                       help="Generate TOC for PDFs without bookmarks")
    parser.add_argument("--confidence-threshold", "-c", type=float, default=0.7,
                       help="Minimum confidence for generated TOC entries (0-1, default: 0.7)")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Suppress warning messages")

    args = parser.parse_args()

    # Extract TOC
    auto_generate = args.generate_if_missing or args.confidence_threshold != 0.7
    toc = extract_pdf_toc(
        args.pdf_file,
        auto_generate=auto_generate,
        confidence_threshold=args.confidence_threshold,
        quiet=args.quiet
    )

    # Output result
    if args.json:
        print(toc_to_json(toc, args.pretty))
    else:
        show_confidence = auto_generate and any('confidence' in item for item in toc)

        # Add information about generation method
        if auto_generate and toc:
            print(f"Generated {len(toc)} TOC entries with confidence threshold {args.confidence_threshold}")
        elif not auto_generate and not toc:
            print("No bookmarks found in this PDF.")
        elif toc:
            print(f"Found {len(toc)} bookmarks in this PDF.")

        out = toc_to_text(toc, show_confidence)
        print(out)


if __name__ == "__main__":
    main()