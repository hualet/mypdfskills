#!/usr/bin/env python3
"""
PDF structure analyzer for table of contents generation.
Extracts text with position and formatting information.
"""

import pdfplumber
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import statistics


class PDFAnalyzer:
    """
    Analyzes PDF structure and extracts text with position information.
    """

    def __init__(self):
        """
        Initialize PDF analyzer.
        """
        self.pages = []
        self.text_elements = []
        self.regions = {}

    def analyze_pdf(self, pdf_path: str) -> Dict:
        """
        Analyze PDF structure and extract text with formatting information.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing:
            - 'text_elements': List of text elements with metadata
            - 'font_statistics': Font usage analysis
            - 'layout_regions': Identified page regions
            - 'heading_candidates': Potential heading elements
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text elements from all pages
                self.text_elements = self._extract_text_elements(pdf)

                # Analyze layout and identify regions
                layout_regions = self._identify_layout_regions()

                # Analyze font usage
                font_stats = self._analyze_font_usage()

                # Filter out headers and footers
                filtered_elements = self._filter_pages_headers_footers()

                return {
                    'text_elements': filtered_elements,
                    'font_statistics': font_stats,
                    'layout_regions': layout_regions,
                    'total_pages': len(pdf.pages),
                    'page_dimensions': self._get_page_dimensions()
                }

        except Exception as e:
            raise Exception(f"Error analyzing PDF: {str(e)}")

    def _extract_text_elements(self, pdf) -> List[Dict]:
        """
        Extract all text elements with position and formatting.
        """
        text_elements = []

        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract characters if available (more detailed)
            if hasattr(page, 'chars') and page.chars:
                elements = self._extract_from_chars(page.chars, page_num)
            else:
                # Fallback to word extraction
                elements = self._extract_from_words(page.extract_words(), page_num)

            text_elements.extend(elements)

        return text_elements

    def _extract_from_chars(self, chars: List[Dict], page_num: int) -> List[Dict]:
        """
        Extract text from character-level data.
        """
        # Group characters into lines based on Y position
        lines = defaultdict(list)
        for char in chars:
            if char.get('text', '').strip():
                y_pos = round(char['y'], 1)  # Round for grouping
                lines[y_pos].append(char)

        elements = []

        for y_pos in sorted(lines.keys()):
            line_chars = sorted(lines[y_pos], key=lambda c: c['x'])

            # Extract line text and properties
            text = ''.join(c['text'] for c in line_chars)

            # Get font properties (most common)
            fonts = defaultdict(int)
            font_sizes = defaultdict(float)
            font_weights = defaultdict(list)

            for char in line_chars:
                font_name = char.get('fontname', 'Unknown')
                font_size = char.get('size', 12)
                font_weight = char.get('weight', 0)

                fonts[font_name] += 1
                font_sizes[font_name] = font_size  # Assume same size within line
                font_weights[font_name].append(font_weight)

            # Use most common font
            primary_font = max(fonts.items(), key=lambda x: x[1])[0]

            element = {
                'text': text.strip(),
                'page': page_num,
                'x': min(c['x'] for c in line_chars),
                'y': y_pos,
                'width': max(c['x'] + c['width'] for c in line_chars) - min(c['x'] for c in line_chars),
                'font_name': primary_font,
                'font_size': font_sizes[primary_font],
                'font_weight': statistics.mean(font_weights[primary_font]) if font_weights[primary_font] else 'normal'
            }

            elements.append(element)

        return elements

    def _extract_from_words(self, words: List[Dict], page_num: int) -> List[Dict]:
        """
        Fallback extraction from word-level data.
        """
        elements = []

        for word in words:
            element = {
                'text': word['text'],
                'page': page_num,
                'x': word['x'],
                'y': word['y'],
                'width': word['width'] if 'width' in word else 0,
                'font_name': word.get('fontname', 'Unknown'),
                'font_size': word.get('size', 12),
                'font_weight': 'normal'
            }
            elements.append(element)

        return elements

    def _identify_layout_regions(self) -> Dict:
        """
        Identify page regions (header, body, footer, margins).
        """
        if not self.text_elements:
            return {}

        # Group elements by page
        pages = defaultdict(list)
        for elem in self.text_elements:
            pages[elem['page']].append(elem)

        regions = {}

        for page_num, elements in pages.items():
            if not elements:
                continue

            # Sort by Y position
            elements = sorted(elements, key=lambda e: -e['y'])  # Top to bottom

            # Calculate percentiles for region identification
            y_positions = [e['y'] for e in elements]
            min_y = min(y_positions)
            max_y = max(y_positions)
            height = max_y - min_y

            # Define regions (adjust thresholds as needed)
            header_threshold = min_y + 0.15 * height  # Top 15%
            footer_threshold = max_y - 0.15 * height  # Bottom 15%

            page_regions = {
                'header': {'y_start': min_y, 'y_end': header_threshold},
                'body': {'y_start': header_threshold, 'y_end': footer_threshold},
                'footer': {'y_start': footer_threshold, 'y_end': max_y}
            }

            regions[page_num] = page_regions

        return regions

    def _analyze_font_usage(self) -> Dict:
        """
        Analyze font usage across the document.
        """
        if not self.text_elements:
            return {}

        font_analysis = {
            'fonts': defaultdict(int),
            'font_sizes': defaultdict(int),
            'size_distribution': defaultdict(int),
            'heading_candidates': []
        }

        for element in self.text_elements:
            font_analysis['fonts'][element['font_name']] += 1
            font_analysis['font_sizes'][element['font_size']] += 1
            font_analysis['size_distribution'][element['font_size']] += 1

        # Identify unique sizes for heading detection
        sizes = sorted(font_analysis['size_distribution'].keys(), reverse=True)
        if sizes:
            font_analysis['largest_sizes'] = sizes[:5]  # Top 5 sizes
            font_analysis['median_size'] = statistics.median(font_analysis['size_distribution'].keys())

            # Identify potential heading sizes
            font_analysis['heading_sizes'] = [s for s in sizes if s > font_analysis['median_size']]

        return dict(font_analysis)

    def _filter_pages_headers_footers(self) -> List[Dict]:
        """
        Filter out headers, footers, and page numbers.
        """
        filtered = []
        regions = self._identify_layout_regions()

        for element in self.text_elements:
            page_num = element['page']
            if page_num in regions:
                # Check if element is in header or footer region
                y_pos = element['y']
                if (y_pos >= regions[page_num]['header']['y_start'] and
                    y_pos <= regions[page_num]['header']['y_end']):
                    continue
                if (y_pos >= regions[page_num]['footer']['y_start'] and
                    y_pos <= regions[page_num]['footer']['y_end']):
                    continue

            filtered.append(element)

        return filtered

    def _get_page_dimensions(self) -> Dict:
        """
        Get dimensions of document pages.
        """
        # This would need to be populated during extraction
        # For now, return empty dict
        return {}

    def analyze_heading_patterns(self, elements: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Analyze elements and identify heading patterns.

        Returns:
            Tuple of (headings, pattern_statistics)
        """
        if not elements:
            return [], {}

        # Group consecutive elements with same formatting
        groups = self._group_by_formatting(elements)

        pattern_stats = {
            'numbering_patterns': defaultdict(int),
            'formatting_patterns': defaultdict(int),
            'position_patterns': defaultdict(int)
        }

        headings = []

        for group in groups:
            if len(group) == 0:
                continue

            # Analyze group for heading characteristics
            analysis = self._analyze_group_pattern(group)
            pattern_stats['formatting_patterns'][analysis['format']] += 1

            if analysis.get('is_heading', False):
                # Combine elements into single heading
                combined = self._combine_group_elements(group)
                combined['pattern_type'] = analysis['pattern_type']
                headings.append(combined)

        return headings, dict(pattern_stats)

    def _group_by_formatting(self, elements: List[Dict]) -> List[List[Dict]]:
        """
        Group elements by shared formatting characteristics.
        """
        if not elements:
            return []

        # Sort by position
        elements = sorted(elements, key=lambda e: (-e['page'], -e['y'], e['x']))

        groups = []
        current_group = []
        prev_format = None

        for elem in elements:
            current_format = {
                'font_size': elem['font_size'],
                'font_name': elem['font_name'],
                'font_weight': elem['font_weight']
            }

            # Check if format is similar to previous
            if prev_format is None or self._formats_similar(current_format, prev_format):
                current_group.append(elem)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [elem]

            prev_format = current_format

        if current_group:
            groups.append(current_group)

        return groups

    def _formats_similar(self, fmt1: Dict, fmt2: Dict) -> bool:
        """
        Check if two formats are similar enough to group together.
        """
        # Simple comparison - could be enhanced
        return (fmt1['font_size'] == fmt2['font_size'] and
                fmt1['font_name'] == fmt2['font_name'])

    def _analyze_group_pattern(self, group: List[Dict]) -> Dict:
        """
        Analyze a group of elements for heading patterns.
        """
        if not group:
            return {'format': 'empty', 'is_heading': False}

        # Check first element for common heading patterns
        first_elem = group[0]
        text = first_elem['text']

        patterns = {
            'number_pattern': self._has_number_pattern(text),
            'chapter_pattern': self._has_chapter_pattern(text),
            'short_uppercase': self._is_short_uppercase(text),
            'bold_format': self._is_bold_format(first_elem)
        }

        # Determine if group represents a heading
        pattern_count = sum(1 for v in patterns.values() if v)
        is_heading = pattern_count >= 1 or first_elem['font_size']  > 14

        return {
            'format': f"{first_elem['font_size']}_{first_elem['font_name']}",
            'is_heading': is_heading,
            'pattern_type': '|'.join([k for k, v in patterns.items() if v]) or 'size_based',
            'confidence': min(0.5 + pattern_count * 0.15, 0.95),
            'first_text': text
        }

    def _has_number_pattern(self, text: str) -> bool:
        """Check if text starts with numbering pattern."""
        import re
        return bool(re.match(r'^\d+(\.\d+)*\s+', text))

    def _has_chapter_pattern(self, text: str) -> bool:
        """Check if text contains chapter/section indicators."""
        import re
        return bool(re.match(r'^(chapter|chap|ch\.|section|sect\.)', text, re.IGNORECASE))

    def _is_short_uppercase(self, text: str) -> bool:
        """Check if text is short and in uppercase."""
        words = text.split()
        return len(words) <= 5 and text.isupper()

    def _is_bold_format(self, element: Dict) -> bool:
        """Check if element is in bold format."""
        font_name = element.get('font_name', '').lower()
        weight = str(element.get('font_weight', '')).lower()
        return 'bold' in font_name or 'bold' in weight or 'heavy' in font_name

    def _combine_group_elements(self, group: List[Dict]) -> Dict:
        """
        Combine group elements into single heading representation.
        """
        if len(group) == 1:
            return group[0]

        # Combine text
        texts = [elem['text'] for elem in group]
        combined_text = ' '.join(texts).strip()

        # Use properties from first element
        first = group[0]

        return {
            'text': combined_text,
            'page': first['page'],
            'x': first['x'],
            'y': first['y'],
            'font_name': first['font_name'],
            'font_size': first['font_size'],
            'font_weight': first['font_weight'],
            'width': sum(elem.get('width', 0) for elem in group),
            'group_size': len(group)
        }