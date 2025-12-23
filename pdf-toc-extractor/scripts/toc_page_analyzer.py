#!/usr/bin/env python3
"""
Table of Contents page detection and extraction for PDF documents.
Analyzes first 10 pages to find actual TOC pages and extracts entries.
"""

import re
import pdfplumber
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TOCPageResult:
    """Result of TOC page analysis."""
    page_number: int
    confidence: float
    entries: List[Dict]
    format_type: str
    method_used: str


class TOCPAGEAnalyzer:
    """
    Analyzes PDF pages to detect and extract table of contents.
    Focuses on first 10 pages looking for typical TOC formats.
    """

    def __init__(self):
        """Initialize analyzer with pattern definitions."""
        # Common TOC patterns
        self.patterns = {
            'dot_leader': {
                'regex': r'^(.*?)\.{3,}\s*(\d+[a-z]*)\s*$',
                'description': 'Text followed by dots then page number',
                'example': 'Chapter 1 Introduction.........................12'
            },
            'tab_based': {
                'regex': r'^(.*?)\t+(\d+[a-z]*)\s*$',
                'description': 'Text-tab-page number format',
                'example': 'Chapter 1 Introduction\t12'
            },
            'dot_leader_variant': {
                'regex': r'^(.*?)\s*\.+\s*(\d+[a-z]*)\s*$',
                'description': 'Text followed by spaces then dots',
                'example': 'Chapter 1 Introduction ...... 12'
            },
            'space_aligned': {
                'regex': r'^(.*?)\s{2,}(\d+[a-z]*)\s*$',
                'description': 'Multiple spaces between text and number',
                'example': 'Chapter 1 Introduction    12'
            },
            'numbered_item': {
                'regex': r'^(\d+\.\d*)\s+(.*?)\s{2,}(\d+[a-z]*)\s*$',
                'description': 'Numbered entries with wider spacing',
                'example': '1.2 Introduction        15'
            },
            'roman_numeral': {
                'regex': r'^(i[vx]|v|x)\s+(.*?)\s{2,}(\d+[a-z]*)\s*$',
                'description': 'Roman numeral prefixes',
                'example': 'i Introduction        15'
            }
        }

        # Compile regex patterns
        self.compiled_patterns = {name: re.compile(pattern['regex'], re.IGNORECASE)
                                 for name, pattern in self.patterns.items()}

    def analyze_pdf(self, pdf_path: str, max_pages: int = 10) -> List[TOCPageResult]:
        """
        Analyze PDF for table of contents pages.

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to analyze (default 10)

        Returns:
            List of TOC page results
        """
        results = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Limit analysis to first max_pages
                pages_to_check = min(max_pages, len(pdf.pages))

                # Check each page
                for page_num in range(1, pages_to_check + 1):
                    page = pdf.pages[page_num - 1]  # pdfplumber uses 0-index
                    result = self._analyze_page_content(page, page_num)

                    if result and result.confidence > 0.0:
                        results.append(result)

                # If no clear TOC found, try combined page analysis
                if not results:
                    result = self._analyze_combined_pages(pdf, pages_to_check)
                    if result:
                        results = [result]

        except Exception as e:
            print(f"Error analyzing PDF: {e}")

        return self._prioritize_results(results)

    def _analyze_page_content(self, page, page_num: int) -> Optional[TOCPageResult]:
        """Analyze single page for TOC characteristics."""
        try:
            # Extract text with positions
            text = page.extract_text()
            if not text:
                return None

            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]

            # Check basic requirements
            if len(lines) < 3:  # Need at least 3 lines
                return None

            # Try different parsing strategies
            for method_name, pattern in self.compiled_patterns.items():
                entries = []
                method_confidence = 0.0

                for line in lines:
                    match = pattern.match(line)
                    if match:
                        entry = {
                            'title': self._normalize_title(match.group(1) if pattern.pattern.count('(') == 1 else match.group(0)).strip(),
                            'pageNumber': self._extract_page_number(match),
                            'level': self._determine_level(line, len(match.groups())),
                            'confidence': 0.8,
                            'detection_method': method_name,
                            'raw_line': line
                        }

                        # Adjust confidence based on match quality
                        entry['confidence'] = self._calculate_entry_confidence(entry, match, method_name)

                        if entry['pageNumber'] and entry['confidence'] > 0.5:
                            entries.append(entry)
                            method_confidence = max(method_confidence, entry['confidence'])

                if len(entries) >= 2:  # Need at least 2 valid entries
                    page_confidence = self._calculate_page_confidence(entries, len(lines))

                    return TOCPageResult(
                        page_number=page_num,
                        confidence=page_confidence,
                        entries=entries,
                        format_type=method_name,
                        method_used="page_analysis"
                    )

            # Basic heuristic check
            basic_entries = self._basic_toc_detection(lines)
            if len(basic_entries) >= 3:
                return TOCPageResult(
                    page_number=page_num,
                    confidence=0.6,
                    entries=basic_entries,
                    format_type="basic_heuristic",
                    method_used="page_analysis"
                )

        except Exception as e:
            print(f"Error analyzing page {page_num}: {e}")

        return None

    def _basic_toc_detection(self, lines: List[str]) -> List[Dict]:
        """Fallback detection for non-standard TOC formats."""
        entries = []

        # Look for lines ending with numbers
        for line in lines:
            # Extract potential page number at end
            match = re.search(r'(\d+)$', line.strip())
            if match:
                page_num = int(match.group(1))
                title = line[:match.start()].strip()

                # Basic validation
                if title and len(title) > 3 and page_num > 0 and page_num < 1000:
                    entries.append({
                        'title': title,
                        'pageNumber': page_num,
                        'level': 0,
                        'confidence': 0.5,
                        'detection_method': 'basic_heuristic'
                    })

        return entries

    def _normalize_title(self, title: str) -> str:
        """Clean and normalize extracted titles."""
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title).strip()

        # Remove leading numbers from title if they're already in TOC number
        title = re.sub(r'^\d+(?:\.\d*)*\s+', '', title)

        return title

    def _extract_page_number(self, match) -> Optional[int]:
        """Extract page number from regex match."""
        # Find all numbers in the match
        numbers = re.findall(r'\d+', match.group(0))

        # Return the last number (most likely the page number)
        if numbers:
            return int(numbers[-1])

        return None

    def _determine_level(self, line: str, group_count: int) -> int:
        """Determine entry nesting level."""
        # Based on indentation (approximate)
        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)

        # Estimate level based on indentation
        level = leading_spaces // 4

        # Also consider patterns like 1.1, 1.2.3 etc.
        if re.match(r'^\d+(\.\d+)*\s+', line):
            parts = line.split('.', 1)[0].split('.')
            return len(parts) - 1

        return min(level, 3)  # Cap at level 3

    def _calculate_entry_confidence(self, entry: Dict, match, pattern_name: str) -> float:
        """Calculate confidence score for individual entry."""
        base = 0.6

        # Title quality checks
        title = entry['title']
        if len(title) > 10:  # Reasonable title length
            base += 0.1
        if len(title) < 3:
            base -= 0.2

        if re.match(r'^[A-Z]', title):  # Starts with capital letter
            base += 0.1

        if re.match(r'^\d+', title):  # Starts with number (common in TOC)
            base += 0.2

        # Consistency with pattern
        if pattern_name in ['dot_leader', 'tab_based']:
            base += 0.2

        # Length penalty for excessive whitespace
        if len(entry['raw_line']) < len(title) + 3:
            base -= 0.1

        return min(max(base, 0.0), 1.0)

    def _calculate_page_confidence(self, entries: List[Dict], total_lines: int) -> float:
        """Calculate confidence that this page contains TOC."""
        if not entries:
            return 0.0

        # Base confidence on ratio of TOC-like lines
        hit_ratio = len(entries) / max(total_lines, 1)
        confidence = min(hit_ratio * 2, 1.0)

        # Bonus for sequential page numbers
        page_nums = [e['pageNumber'] for e in entries if e['pageNumber']]
        if len(page_nums) > 1:
            sorted_nums = sorted(page_nums)
            sequential = sum(1 for i in range(1, len(sorted_nums))
                           if sorted_nums[i] == sorted_nums[i-1] + 1)
            if sequential > len(page_nums) // 2:
                confidence += 0.1

        # Bonus for pattern consistency
        methods = set(e['detection_method'] for e in entries)
        if len(methods) == 1:  # All same method
            confidence += 0.05

        return min(confidence, 1.0)

    def _analyze_combined_pages(self, pdf, num_pages: int) -> Optional[TOCPageResult]:
        """Analyzing pages combined for multi-page TOC."""
        all_entries = []
        start_page = 1

        # Look for TOC spanning multiple pages
        for page_num in range(1, num_pages + 1):
            page = pdf.pages[page_num - 1]
            result = self._analyze_page_content(page, page_num)

            if result and result.confidence > 0.3:
                all_entries.extend(result.entries)
                if not start_page:  # Track first TOC page
                    start_page = page_num

        if len(all_entries) >= 5:  # At least 5 entries across pages
            return TOCPageResult(
                page_number=0,  # Multi-page TOC
                confidence=0.7,
                entries=all_entries,
                format_type="multi_page",
                method_used="combined_analysis"
            )

        return None

    def _prioritize_results(self, results: List[TOCPageResult]) -> List[TOCPageResult]:
        """Sort and prioritize multiple TOC page results."""
        if not results:
            return results

        # Sort by confidence (descending), then by number of entries
        results.sort(key=lambda x: (x.confidence, len(x.entries)), reverse=True)

        # Return only high-confidence results
        return [r for r in results if r.confidence > 0.5]

    def convert_to_standard_format(self, results: List[TOCPageResult]) -> List[Dict]:
        """Convert analysis results to standard TOC format."""
        if not results:
            return []

        # Use the highest confidence result
        best_result = results[0]

        # Convert entries to standard format
        standard_entries = []
        for i, entry in enumerate(best_result.entries):
            standard_entry = {
                'title': entry['title'],
                'pageNumber': entry['pageNumber'],
                'level': entry['level'],
                'confidence': entry['confidence'],
                'detection_method': entry.get('detection_method', 'unknown')
            }
            standard_entries.append(standard_entry)

        return standard_entries