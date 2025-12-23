#!/usr/bin/env python3
"""
Heading detection for PDF documents.
Analyzes typography, patterns, and layout to identify section headings.
"""

import re
from typing import List, Dict, Optional, Tuple
import pandas as pd
from statistics import median, stdev


class HeadingDetector:
    """
    Detects headings in PDF text based on typography and pattern analysis.
    """

    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize detector with confidence threshold.

        Args:
            confidence_threshold: Minimum confidence score for accepting a heading (0-1)
        """
        self.confidence_threshold = confidence_threshold

        # Common heading patterns
        self.heading_patterns = [
            # Number patterns: 1, 1.1, 1.1.1, etc.
            r'^\d+(\.\d+)*\s+',
            # Chapter patterns: Chapter 1, Chapter One, Chapitre, etc.
            r'^(chapter|chap|ch\.|section|sect\.|§\s*\d+)',
            # Common section words
            r'^(introduction|overview|summary|conclusion|appendix|references?|bibliography)',
            # Roman numerals
            r'^[IVXLCDM]+\s+',
            # Letters with dots
            r'^[A-Z]\.[\s\n]+',
        ]

        self.pattern_regexes = [re.compile(p, re.IGNORECASE) for p in self.heading_patterns]

    def detect_headings(self, text_data: List[Dict]) -> List[Dict]:
        """
        Detect headings from text data with font and position information.

        Args:
            text_data: List of text elements with font and position info
                      Each dict should contain:
                      - 'text': Text content
                      - 'font_name': Font name
                      - 'font_size': Font size
                      - 'x': X position
                      - 'y': Y position
                      - 'page': Page number

        Returns:
            List of detected headings with confidence scores
        """
        if not text_data:
            return []

        # Build font statistics
        font_stats = self._analyze_font_statistics(text_data)

        # Detect potential headings
        headings = []
        for element in text_data:
            confidence = self._calculate_heading_confidence(element, font_stats)

            if confidence >= self.confidence_threshold:
                heading = {
                    'title': element['text'].strip(),
                    'page': element['page'],
                    'confidence': confidence,
                    'detection_method': self._get_detection_method(element, font_stats),
                    'font_size': element['font_size'],
                    'position': {'x': element['x'], 'y': element['y']}
                }
                headings.append(heading)

        return sorted(headings, key=lambda h: (h['page'], h['position']['y'], h['position']['x']))

    def _analyze_font_statistics(self, text_data: List[Dict]) -> Dict:
        """
        Analyze font statistics to identify heading candidates.

        Returns:
            Dictionary with font analysis results
        """
        df = pd.DataFrame(text_data)

        # Calculate font size statistics
        font_sizes = df['font_size'].dropna()
        if len(font_sizes) == 0:
            return {}

        stats = {
            'median_size': median(font_sizes),
            'std_size': stdev(font_sizes) if len(font_sizes) > 1 else 0,
            'max_size': max(font_sizes),
            'min_size': min(font_sizes),
            'size_distribution': self._get_size_distribution(font_sizes)
        }

        # Identify potential heading font sizes
        if stats['std_size'] > 0:
            # Heading fonts are typically larger than median
            stats['heading_threshold'] = stats['median_size'] + stats['std_size']
            # Also consider very large fonts regardless of variation
            stats['large_threshold'] = stats['max_size'] * 0.85
        else:
            stats['heading_threshold'] = stats['median_size']
            stats['large_threshold'] = stats['median_size']

        return stats

    def _get_size_distribution(self, font_sizes: pd.Series) -> Dict:
        """
        Get distribution of font sizes for clustering analysis.
        """
        size_counts = font_sizes.value_counts().to_dict()
        return size_counts

    def _calculate_heading_confidence(self, element: Dict, font_stats: Dict) -> float:
        """
        Calculate confidence score that an element is a heading.

        Args:
            element: Text element with properties
            font_stats: Font analysis statistics

        Returns:
            Confidence score (0-1)
        """
        confidence_factors = []

        # Factor 1: Font size analysis
        font_size_score = self._score_font_size(element, font_stats)
        confidence_factors.append(font_size_score)

        # Factor 2: Text pattern matching
        pattern_score = self._score_text_pattern(element)
        confidence_factors.append(pattern_score)

        # Factor 3: Text structure analysis
        structure_score = self._score_text_structure(element, font_stats)
        confidence_factors.append(structure_score)

        # Factor 4: Position/layout analysis
        position_score = self._score_position(element)
        confidence_factors.append(position_score)

        # Calculate weighted average
        weights = [0.35, 0.35, 0.2, 0.1]  # Font and pattern are most important
        confidence = sum(score * weight for score, weight in zip(confidence_factors, weights))

        return min(confidence, 1.0)

    def _score_font_size(self, element: Dict, font_stats: Dict) -> float:
        """
        Score based on font size compared to median.
        """
        if not font_stats or 'font_size' not in element:
            return 0.0

        font_size = element['font_size']

        # Check if it's larger than the heading threshold
        if 'heading_threshold' in font_stats:
            if font_size >= font_stats['heading_threshold']:
                # Linear scale from threshold to max size
                if font_stats['max_size'] > font_stats['heading_threshold']:
                    score = (font_size - font_stats['heading_threshold']) / \
                           (font_stats['max_size'] - font_stats['heading_threshold'])
                    return min(0.5 + score * 0.5, 1.0)  # 0.5 to 1.0 range
                return 0.8

        return 0.0

    def _score_text_pattern(self, element: Dict) -> float:
        """
        Score based on text pattern matching.
        """
        text = element.get('text', '').strip()

        if not text:
            return 0.0

        # Check pattern matches
        for regex in self.pattern_regexes:
            if regex.search(text):
                return 0.9  # High confidence for pattern matches

        # Additional heuristics
        # Short texts in ALL CAPS are often headings
        if len(text.split()) <= 5 and text.isupper():
            return 0.7

        # Short texts with title case
        if len(text.split()) <= 4 and text.istitle():
            return 0.6

        return 0.0

    def _score_text_structure(self, element: Dict, font_stats: Dict) -> float:
        """
        Score based on text structure characteristics.
        """
        text = element.get('text', '').strip()

        if not text:
            return 0.0

        score = 0.0

        # Length characteristics
        words = text.split()

        # Headings typically have 1-10 words
        if 1 <= len(words) <= 10:
            score += 0.2

        # Punctuation characteristics
        if not text.endswith(('.', '?', '!', ':', ';', ',')):
            score += 0.2

        # Doesn't have multiple sentences
        if text.count('.') <= 1:
            score += 0.1

        return score

    def _score_position(self, element: Dict) -> float:
        """
        Score based on position indicators.
        """
        # New pages often start with headings
        if element.get('position', {}).get('y', 0) < 100:  # Top of page
            return 0.3

        return 0.0

    def _get_detection_method(self, element: Dict, font_stats: Dict) -> str:
        """
        Get the primary detection method used for this element.
        """
        methods = []

        if self._score_font_size(element, font_stats) > 0.3:
            methods.append('font_size')

        if self._score_text_pattern(element) > 0.5:
            methods.append('text_pattern')

        if self._score_text_structure(element, font_stats) > 0.3:
            methods.append('text_structure')

        if self._score_position(element) > 0.2:
            methods.append('position')

        return '|'.join(methods) if methods else 'unknown'


# Example usage patterns for different document types
DOCUMENT_PRESETS = {
    'academic_paper': {
        'confidence_threshold': 0.7,
        'enable_number_detection': True,
        'enable_section_detection': True,
        'min_font_size_multiplier': 1.1
    },
    'technical_report': {
        'confidence_threshold': 0.65,
        'enable_number_detection': True,
        'enable_section_detection': True,
        'min_font_size_multiplier': 1.0
    },
    'book': {
        'confidence_threshold': 0.8,
        'enable_number_detection': True,
        'enable_section_detection': True,
        'min_font_size_multiplier': 1.2
    },
    'article': {
        'confidence_threshold': 0.75,
        'enable_number_detection': False,
        'enable_section_detection': True,
        'min_font_size_multiplier': 1.1
    }
}