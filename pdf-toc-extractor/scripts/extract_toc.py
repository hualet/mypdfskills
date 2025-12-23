#!/usr/bin/env python3
"""
Extract table of contents from PDF files using TOC page detection.
Focuses on detecting actual table of contents pages and parsing their contents.
"""

import sys
import json
from PyPDF2 import PdfReader
from typing import Dict, List, Optional
from argparse import ArgumentParser

# Import new TOC detection modules
try:
    from toc_page_analyzer import TOCPAGEAnalyzer, TOCPageResult
    from toc_pattern_matcher import TOCPatternMatcher, TOCFormat
    TOC_DETECTION_AVAILABLE = True
except ImportError:
    TOC_DETECTION_AVAILABLE = False


def extract_pdf_toc(pdf_path: str,
                   auto_detect_toc: bool = False,
                   toc_page_threshold: float = 0.6,
                   quiet: bool = False) -> List[Dict]:
    """
    Extract table of contents from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        auto_detect_toc: If True, try to detect TOC pages if no bookmarks found
        toc_page_threshold: Minimum confidence for TOC page detection
        quiet: Suppress warning messages

    Returns:
        List of dictionaries containing TOC entries with title, page number, and level
    """
    try:
        # First try standard bookmark extraction
        toc = extract_bookmarks(pdf_path)

        # If no bookmarks found and auto-detection is enabled, try TOC page detection
        if not toc and auto_detect_toc and TOC_DETECTION_AVAILABLE:
            if not quiet:
                print("No bookmarks found. Attempting to detect table of contents pages...", file=sys.stderr)
            toc = detect_and_parse_toc_pages(pdf_path, toc_page_threshold, quiet)
            if toc and not quiet:
                print(f"Detected TOC on pages and extracted {len(toc)} entries", file=sys.stderr)
        elif not toc and auto_detect_toc and not TOC_DETECTION_AVAILABLE:
            if not quiet:
                print("TOC detection not available (required modules not installed)", file=sys.stderr)

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


def detect_and_parse_toc_pages(pdf_path: str, threshold: float = 0.6, quiet: bool = False) -> List[Dict]:
    """
    Detect TOC pages and parse their contents.

    Args:
        pdf_path: Path to the PDF file
        threshold: Minimum confidence for TOC detection
        quiet: Suppress progress messages

    Returns:
        Extracted TOC entries
    """
    if not TOC_DETECTION_AVAILABLE:
        raise Exception("TOC detection modules not available")

    try:
        # Create analyzer
        analyzer = TOCPAGEAnalyzer()

        if not quiet:
            print("Analyzing pages for table of contents...", file=sys.stderr)

        # Analyze PDF for TOC pages
        results = analyzer.analyze_pdf(pdf_path, max_pages=10)

        # Convert results to standard format
        if results:
            # Apply threshold if specified
            valid_results = [r for r in results if r.confidence >= threshold]

            if valid_results:
                # Combine all results (in case of multi-page TOC)
                all_entries = []
                cumulative_confidence = 0

                for result in valid_results:
                    all_entries.extend(result.entries)
                    cumulative_confidence += result.confidence

                # Generate consistent format
                standard_entries = []
                for entry in all_entries:
                    standard_entry = {
                        'title': entry['title'],
                        'pageNumber': entry['pageNumber'],
                        'level': entry['level'],
                        'confidence': entry['confidence'],
                        'detection_method': entry.get('detection_method', 'unknown')
                    }
                    standard_entries.append(standard_entry)

                # Remove duplicates if any
                seen = set()
                unique_entries = []
                for entry in standard_entries:
                    key = (entry['title'], entry['pageNumber'])
                    if key not in seen:
                        seen.add(key)
                        unique_entries.append(entry)

                # Sort by page number
                unique_entries.sort(key=lambda x: x['pageNumber'])

                return unique_entries

        return []

    except Exception as e:
        raise Exception(f"Error detecting TOC pages: {str(e)}")


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

    # Show generation method info
    has_generated = any('confidence' in item for item in toc)
    if has_generated:
        avg_conf = sum(item.get('confidence', 0.5) for item in toc) / len(toc)
        lines.append(f"Auto-detected TOC (avg confidence: {avg_conf:.2f})")
        lines.append("-" * 50)

    for item in toc:
        indent = "  " * item['level']
        page_str = f"Page {item['pageNumber']}" if item['pageNumber'] else "Unknown page"
        line = f"{indent}{item['title']} - {page_str}"

        # Add confidence if requested and available
        if show_confidence and 'confidence' in item:
            line += f" [{item['confidence']:.2f}]"

        lines.append(line)

        # Add detection method if available
        if show_confidence and 'detection_method' in item:
            lines.append(f"{indent}  (Extracted from TOC page)")

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
    parser = ArgumentParser(description="Extract table of contents from PDF files using pool detection")
    parser.add_argument("pdf_file", help="Path to the PDF file")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")
    parser.add_argument("--pretty", action="store_true",
                       help="Pretty-print JSON output")
    parser.add_argument("--detect-toc", "-d", action="store_true",
                       help="Auto-detect table of contents pages if no bookmarks found")
    parser.add_argument("--toc-threshold", "-t", type=float, default=0.6,
                       help="Minimum confidence for TOC page detection (0-1, default 0.6)")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Suppress messages")

    args = parser.parse_args()

    # Set auto-detect based on user selection
    auto_detect = args.detect_toc

    # Extract TOC
    toc = extract_pdf_toc(
        args.pdf_file,
        auto_detect_toc=auto_detect,
        toc_page_threshold=args.toc_threshold,
        quiet=args.quiet
    )

    # Output results summary
    if args.quiet == False:
        if args.detect_toc and toc and any('confidence' in item for item in toc):
            print(f"Detected {len(toc)} TOC entries from pages")
        elif not auto_detect and toc:
            print(f"Found {len(toc)} bookmarks in this PDF")
        elif toc:
            print(f"Generated {len(toc)} TOC entries")

    # Output result
    if args.json:
        print(toc_to_json(toc, args.pretty))
    else:
        show_confidence = auto_detect and any('confidence' in item for item in toc)
        print(toc_to_text(toc, show_confidence))


if __name__ == "__main__":
    main()