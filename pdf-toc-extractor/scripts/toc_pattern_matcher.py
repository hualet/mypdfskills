#!/usr/bin/env python3
"""
Sophisticated pattern matching for table of contents extraction.
Handles various TOC formats with enhanced detection capabilities.
"""

import re
from typing import List, Dict, Optional, Tuple
from enum import Enum


class TOCFormat(Enum):
    """Enumeration of supported TOC formats."""
    DOT_LEADER = "dot_leader"
    TAB_BASED = "tab_based"
    SPACE_ALIGNED = "space_aligned"
    ORDINAL_DOTS = "ordinal_dots"
    MARKED_LIST = "marked_list"
    HYPERLINK = "hyperlink"


class TOCPatternMatcher:
    """
    Advanced pattern matching for table of contents detection.
    Supports multiple TOC formats with fuzzy matching capabilities.
    """

    def __init__(self):
        """Initialize with comprehensive pattern configurations."""
        # Enhanced pattern definitions with multiple variations
        self.patterns = {
            # Classic dot leader format
            TOCFormat.DOT_LEADER: {
                'primary': r'^(.*?)\.{3,}\s*(\d+[a-z]*)$',   # Chapter......12
                'variant1': r'^(.*?)\s+\.+\s+(\d+)$',      # Chapter ... 12
                'variant2': r'^(.*?)\u00a0+\.+\s*(\d+)$',      # Chapter(nbsp)....12
                'variant3': r'^(.*?) +\.+\s*(\d+)$',       # Chapter(narrow space)....12
                'description': 'Entries with dot leader formatting'
            },

            # Tab-separated entries
            TOCFormat.TAB_BASED: {
                'primary': r'^(.*?)\t+(\d+[a-z]*)$',         # Chapter	12
                'variant1': r'^(.*?)\t+\s*(\d+)$',          # Chapter	 12
                'variant2': r'^(.*?)\s+\t+(\d+)$',          # Chapter 	12
                'description': 'Tab-separated titles and page numbers'
            },

            # Space-aligned entries
            TOCFormat.SPACE_ALIGNED: {
                'primary': r'^(.*?)\s{4,}(\d+[a-z]*)$',     # Chapter      12
                'variant1': r'^(.*?)\s+\s{3,}(\d+)$'        # Chapter     12
            },

            # Numbered entries with dots
            TOCFormat.ORDINAL_DOTS: {
                'primary': r'^(\d+\.\d*)\s+(.*?)\s+\.*\s*(\d+[a-z]*)$',   # 1.1 Title  12
                'variant1': r'^(\d+)\.?\s+(.*?)\s+\.*\s*(\d+)$',         # 1 Title  12
                'variant2': r'^(\d+\.\d+\.\d*)\s+(.*?)\s+\.*\s*(\d+)$'    # 1.1.2 Title  12
            },

            # Markdown-style lists
            TOCFormat.MARKED_LIST: {
                'primary': r'^[-*+]\s+(.*?)\s+\.*\s*(\d+[a-z]*)$',        # - Title  12
                'variant1': r'^\d+\.\s+(.*?)\s+\.*\s*(\d+)$'              # 1. Title  12
            },

            # PDF hyperlink hints
            TOCFormat.HYPERLINK: {
                'primary': r'^(.*?)\s+\.*\s*(\d+)(?:\s+goto)?$',           # Title  12
                'description': 'Page numbers that look like links'
            }
        }

        # Compile all patterns for performance
        self.compiled_patterns = {}
        for format_type, variants in self.patterns.items():
            self.compiled_patterns[format_type] = {}
            for name, pattern in variants.items():
                if name.startswith('variant') or name == 'primary':
                    self.compiled_patterns[format_type][name] = re.compile(pattern)

    def find_toc_pattern(self, text: str) -> Optional[Tuple[TOCFormat, Dict]]:
        """
        Find the dominant TOC pattern in the given text.

        Args:
            text: Page content to analyze

        Returns:
            Tuple of (format_type, pattern_info) if found, None otherwise
        """
        lines = text.split('\n')
        results = {}

        # Try each pattern on each line
        for format_type, patterns in self.compiled_patterns.items():
            matches = []
            match_counts = {}

            for variant_name, compiled_pattern in patterns.items():
                count = 0
                valid_matches = []

                for line_num, line in enumerate(lines, 1):
                    match = compiled_pattern.match(line.strip())
                    if match:
                        count += 1
                        valid_matches.append((line_num, match))

                match_counts[variant_name] = (count, valid_matches)
                matches.extend(valid_matches)

            if len(matches) >= 2:  # At least 2 matches needed
                results[format_type] = {
                    'matches': sum(cnt for cnt, _ in match_counts.values()),
                    'patterns': match_counts,
                    'total_lines': len(lines),
                    'match_ratio': sum(cnt for cnt, _ in match_counts.values()) / len(lines)
                }

        # Select best pattern based on ratio
        if results:
            best_format = max(results.keys(), key=lambda x: results[x]['match_ratio'])
            return (best_format, results[best_format])

        return None

    def extract_entries(self, text: str, format_type: TOCFormat) -> List[Dict]:
        """Extract TOC entries using the detected format."""
        lines = text.split('\n')
        entries = []

        patterns = self.compiled_patterns[format_type]

        # Try each variant in order
        for variant_name in ['primary', 'variant1', 'variant2', 'variant3', 'variant4']:
            if variant_name not in patterns:
                continue

            compiled_pattern = patterns[variant_name]
            variant_entries = []

            for line_num, line in enumerate(lines, 1):
                match = compiled_pattern.match(line.strip())
                if match:
                    entry = self._parse_match(match, format_type, line, line_num)
                    if entry and entry['confidence'] > 0.3:
                        variant_entries.append(entry)

            # Use this variant if it found valid entries
            if variant_entries:
                entries.extend(variant_entries)

        return entries

    def _parse_match(self, match, format_type: TOCFormat, line: str, line_num: int) -> Optional[Dict]:
        """Parse a successful regex match into a TOC entry."""
        groups = match.groups()

        # Extract title and page number based on format
        if format_type == TOCFormat.ORDINAL_DOTS and len(groups) >= 3:
            number = groups[0]
            title = groups[1]
            page_num = groups[2]
        elif format_type == TOCFormat.ORDINAL_DOTS and len(groups) == 2:
            number = groups[0]
            title = groups[1]
            page_num = "1"  # Use 1 as fallback
        elif format_type == TOCFormat.HYPERLINK and groups:
            title = groups[0]
            page_num = groups[1]
        elif groups:
            title = groups[0]
            page_num = groups[1]
        else:
            return None

        # Clean up title
        title = self._clean_title(title)

        # Try to convert page number to int
        page = self._page_to_int(page_num)
        if not page:
            return None

        # Determine level
        level = self._determine_level(title, line)

        # Calculate confidence
        confidence = self._calculate_entry_confidence(title, page_num, line, format_type)

        return {
            'title': title,
            'pageNumber': int(page),
            'level': level,
            'confidence': confidence,
            'raw_line': line,
            'format_type': format_type.value,
            'detected_pattern': match.re.pattern
        }

    def _clean_title(self, title: str) -> str:
        """Clean extracted title."""
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title).strip()

        # Remove leading/trailing numbers if they exist
        title = re.sub(r'^\d+\.?\s*', '', title)
        title = re.sub(r'\s*\d+\.?\s*$', '', title)

        # Remove dots at end
        title = re.sub(r'\.+$', '', title).strip()

        return title

    def _page_to_int(self, page_num: str) -> Optional[int]:
        """Convert page number string to integer."""
        # Handle Roman numerals (i-v):
        roman_to_int = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5}
        page_num = page_num.lower()

        # Check if it's a regular number
        try:
            return int(page_num)
        except (ValueError, TypeError):
            pass

        # Check if it's a Roman numeral
        if page_num in roman_to_int:
            return roman_to_int[page_num]

        # Some docs have lettered pages (A-1, B-123)
        if '-' in page_num:
            parts = page_num.split('-', 1)
            try:
                return int(parts[1]) if len(parts) == 2 else None
            except (ValueError, IndexError):
                pass

        return None

    def _determine_level(self, title: str, line: str) -> int:
        """Determine entry nesting level."""
        level = 0

        # Check for indentation
        indent = 0
        if line != line.strip():
            indent = len(line) - len(line.strip())
            level = min(indent // 4, 3)  # Cap at level 3

        # Analyze title for level indicators
        title_match = re.match(r'^(\d+(?:\.\d+)*)\s*(.*)$', title)
        if title_match:
            numbers = title_match.group(1).split('.')
            number_level = len(numbers) - 1
            level = max(level, number_level)

        # Check for Roman numeral prefixes
        if re.match(r'^[IVX]+\s', title):
            level += 1

        return min(level, 3)  # Cap at level 3

    def _calculate_entry_confidence(self, title: str, page_num: str, line: str, format_type: TOCFormat) -> float:
        """Calculate confidence score for entry."""
        confidence = 0.6  # Base confidence

        # Title quality
        if 3 <= len(title) <= 120:  # Reasonable length
            confidence += 0.1
        if len(title) < 3:
            confidence -= 0.2
        if len(title) > 150:
            confidence -= 0.1

        # Structure indicators
        if re.search(r'\d+\.\d+', title):  # Chapter/section numbering
            confidence += 0.2
        if title.lower() in ['introduction', 'conclusion', 'references', 'appendix']:
            confidence += 0.1

        # Format-specific bonuses
        if format_type == TOCFormat.DOT_LEADER:
            confidence += 0.1  # Classic TOC format
        elif format_type == TOCFormat.ORDINAL_DOTS:
            confidence += 0.15  # Numbered subsections

        return min(max(confidence, 0.0), 1.0)

    def validate_toc_structures(self, entries: List[Dict]) -> Dict:
        """Analyze TOC structure for consistency."""
        if not entries:
            return {'valid': False, 'issues': ['No entries found']}

        issues = []

        # Check for sequential page numbers
        pages = [e['pageNumber'] for e in entries if e['pageNumber'] > 0]
        if len(pages) > 1:
            sorted_pages = sorted(pages)
            expected_count = len(pages)
            for i in range(len(sorted_pages) - 1):
                if sorted_pages[i + 1] - sorted_pages[i] > 1:
                    # Non-sequential is okay if there's a gap
                    continue

            # Rarely consecutive in real TOCs
            consecutive_count = sum(1 for i in range(1, len(sorted_pages))
                                  if sorted_pages[i] == sorted_pages[i-1] + 1)
            if consecutive_count >= len(pages) // 2:
                # Too many consecutive pages might indicate false positive
                pass

        # Check for hierarchy consistency
        if len(entries) > 3:
            parent_ratio = sum(1 for e in entries if e['level'] == 0) / len(entries)
            if parent_ratio < 0.1:  # Too few top-level entries
                issues.append('Too few main sections')
            elif parent_ratio > 0.7:  # Too many top-level entries
                issues.append('Possible flat structure')

        # Check confidence distribution
        avg_conf = sum(e['confidence'] for e in entries) / len(entries)
        if avg_conf < 0.6:
            issues.append(f'Low average confidence: {avg_conf:.2f}')

        return {
            'valid': len([i for i in issues if 'low' not in i.lower()]) <= 1,
            'issues': issues,
            'statistics': {
                'total_entries': len(entries),
                'avg_confidence': avg_conf,
                'uniqueness_percentage': len(set(e['title'] for e in entries)) / len(entries),
                'level_distribution': self._get_level_distribution(entries)
            }
        }

    def _get_level_distribution(self, entries: List[Dict]) -> Dict:
        """Get distribution of entry levels."""
        levels = {'0': 0, '1': 0, '2': 0, '3': 0}
        for e in entries:
            level = min(e['level'], 3)
            levels[str(level)] += 1
        return levels

    def extract_entries_advanced(self, content_blocks: List[str]) -> List[Dict]:
        """Advanced multi-block TOC detection for complex formats."""
        all_entries = []

        for block_num, block in enumerate(content_blocks):
            # Try standard patterns
            format_info = self.find_toc_pattern(block)
            if format_info:
                entries = self.extract_entries(block, format_info[0])
                # Add block context
                for entry in entries:
                    entry['block_number'] = block_num
                all_entries.extend(entries)
            else:
                # Try special handling for common cases
                special_entries = self._try_special_patterns(block, block_num)
                if special_entries:
                    all_entries.extend(special_entries)

        # Remove duplicates and merge overlapping sections
        return self._merge_overlapping_entries(all_entries)

    def _try_special_patterns(self, text: str, block_num: int) -> List[Dict]:
        """Try special TOC pattern detection for edge cases."""
        # Academic paper style: Abstract, Introduction, Methods, Results...
        academic_patterns = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']

        entries = []
        content = text.lower()

        for i, pattern in enumerate(academic_patterns):
            matches = list(re.finditer(rf'\b{pattern}\b', content, re.IGNORECASE))
            for match in matches:
                # Try to find adjacent page number
                context = text[max(0, match.start()-20):match.end()+20]
                page_match = re.search(r'(\d+)', context)
                if page_match:
                    entries.append({
                        'title': pattern.title(),
                        'pageNumber': int(page_match.group(1)),
                        'level': 1 if i < 2 else 2,
                        'confidence': 0.8,
                        'block_number': block_num,
                        'detection_method': 'academic_sections'
                    })
                    break

        return entries

    def _merge_overlapping_entries(self, entries: List[Dict]) -> List[Dict]:
        """Merge similar or overlapping entries."""
        if not entries:
            return entries

        # Group by similar titles (within same logical area)
        unique_entries = []
        seen_titles = set()

        for entry in entries:
            # Normalize title for comparison
            norm_title = re.sub(r'\W+', '', entry['title'].lower())

            # Skip if too similar to existing
            should_skip = False
            for seen in seen_titles:
                if (norm_title in seen or seen in norm_title) and len(norm_title) > 5:
                    should_skip = True
                    break

            if not should_skip and norm_title:
                unique_entries.append(entry)
                seen_titles.add(norm_title)

        return unique_entries

    def format_detections(self, entries: List[Dict]) -> str:
        """Human-readable format of detected entries."""
        if not entries:
            return "No TOC entries detected"

        lines = []
        for entry in entries:
            indent = "  " * entry['level']
            page = entry['pageNumber']
            confidence = entry['confidence']
            method = entry.get('format_type', 'unknown')

            lines.append(f"{indent}- {entry['title']} (p.{page}) [{confidence:.2f}, {method}]")

        return '\n'.join(lines)