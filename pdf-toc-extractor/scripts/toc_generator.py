#!/usr/bin/env python3
"""
Table of Contents generator from detected headings.
Builds hierarchical structure based on font size, position, and content patterns.
"""

from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import statistics
import re


class TOCGenerator:
    """
    Generates hierarchical table of contents from detected headings.
    """

    def __init__(self, min_confidence: float = 0.7, max_level: int = 4):
        """
        Initialize TOC generator.

        Args:
            min_confidence: Minimum confidence threshold for including headings
            max_level: Maximum depth of TOC levels
        """
        self.min_confidence = min_confidence
        self.max_level = max_level

        # Pattern matchers for different hierarchy levels
        self.level_patterns = {
            0: [r'^chapter\s+\d+', r'^part\s+\w+', r'^[IVXLCDM]+[\s\.]', r'^\d+[\s\.]', r'^(introduction|preface|foreword)'],
            1: [r'^\d+\.\d+', r'^section\s+\d+', r'^[A-Z]\.[\s\.]', r'^[i]+[\s\.]', r'^(overview|background)'],
            2: [r'^\d+\.\d+\.\d+', r'^\d+\.\s*[a-z]', r'^\([a-z]\)', r'^(subsection|subheading)'],
            3: [r'^\d+\.\d+\.\d+\.\d+', r'-.*-']
        }

        self.level_regex = {}
        for level, patterns in self.level_patterns.items():
            self.level_regex[level] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def generate_toc(self, headings: List[Dict]) -> List[Dict]:
        """
        Generate hierarchical table of contents from detected headings.

        Args:
            headings: List of detected headings with confidence scores

        Returns:
            Hierarchical TOC with levels and page numbers
        """
        if not headings:
            return []

        # Filter by confidence
        filtered = [h for h in headings if h['confidence'] >= self.min_confidence]

        if not filtered:
            return []

        # Sort by page and position
        sorted_headings = sorted(filtered, key=lambda h: (h['page'], h.get('position', {}).get('y', 0)))

        # Determine hierarchy levels
        hierarchy = self._determine_hierarchy(sorted_headings)

        # Build TOC structure
        toc = self._build_toc_hierarchy(hierarchy)

        # Post-process to ensure consistency
        toc = self._post_process_toc(toc)

        return toc

    def _determine_hierarchy(self, headings: List[Dict]) -> List[Dict]:
        """
        Determine hierarchy levels for headings based on multiple cues.
        """
        if len(headings) == 1:
            headings[0]['level'] = 0
            return headings

        # Analyze font sizes for relative hierarchy
        font_analysis = self._analyze_font_sizes(headings)

        # Analyze numbering patterns
        pattern_analysis = self._analyze_numbering_patterns(headings)

        # Analyze position patterns
        position_analysis = self._analyze_position_patterns(headings)

        # Combine all analyses to determine levels
        for i, heading in enumerate(headings):
            level = self._calculate_heading_level(
                heading,
                font_analysis,
                pattern_analysis.get(i, {}),
                position_analysis.get(i, {})
            )
            heading['level'] = level
            heading['level_certainty'] = heading.get('confidence', 0.5)  # Could be refined

        return headings

    def _analyze_font_sizes(self, headings: List[Dict]) -> Dict:
        """
        Analyze font size distribution to determine hierarchy.
        """
        font_sizes = [h['font_size'] for h in headings if 'font_size' in h]

        if not font_sizes:
            return {}

        unique_sizes = sorted(set(font_sizes), reverse=True)  # Largest first
        size_levels = {}

        # Assign levels based on relative size
        for i, size in enumerate(unique_sizes[:self.max_level]):
            size_levels[size] = i

        # Calculate statistics
        stats = {
            'size_levels': size_levels,
            'largest_size': max(font_sizes),
            'smallest_size': min(font_sizes),
            'median_size': statistics.median(font_sizes),
            'unique_sizes': unique_sizes
        }

        return stats

    def _analyze_numbering_patterns(self, headings: List[Dict]) -> Dict:
        """
        Analyze numbering patterns in heading text.
        """
        patterns = {}

        for i, heading in enumerate(headings):
            text = heading.get('text', '').strip()
            pattern_match = self._match_numbering_pattern(text)
            patterns[i] = pattern_match

        return patterns

    def _analyze_position_patterns(self, headings: List[Dict]) -> Dict:
        """
        Analyze position/layout patterns.
        """
        positions = {}

        # Group by page
        page_groups = defaultdict(list)
        for i, heading in enumerate(headings):
            page_groups[heading['page']].append((i, heading))

        # Analyze positioning within pages
        for page_num, page_headings in page_groups.items():
            # Sort by Y position (top to bottom)
            page_headings = sorted(page_headings, key=lambda x: x[1].get('position', {}).get('y', 0))

            # Analyze indentation
            x_positions = [h[1].get('position', {}).get('x', 0) for h in page_headings]
            min_x = min(x_positions)

            for i, (idx, heading) in enumerate(page_headings):
                x_pos = heading.get('position', {}).get('x', 0)
                indent = x_pos - min_x

                positions[idx] = {
                    'indentation': indent,
                    'page_position': i,
                    'total_on_page': len(page_headings)
                }

        return positions

    def _calculate_heading_level(self, heading: Dict, font_analysis: Dict,
                                pattern_match: Dict, position_match: Dict) -> int:
        """
        Calculate heading level based on combined analysis.
        """
        # Start with font size level
        font_size = heading.get('font_size', 12)
        base_level = font_analysis.get('size_levels', {}).get(font_size, 1)

        # Override with pattern analysis if clear match
        if pattern_match and pattern_match.get('matched_level') is not None:
            return pattern_match['matched_level']

        # Adjust based on indentation (sub-sections are often indented)
        if position_match and position_match.get('indentation', 0) > 20:
            base_level = min(base_level + 1, self.max_level - 1)

        # Ensure level is within bounds
        return min(base_level, self.max_level - 1)

    def _match_numbering_pattern(self, text: str) -> Dict:
        """
        Match text against numbering patterns for different levels.
        """
        text_lower = text.lower()

        for level, patterns in self.level_regex.items():
            for regex in patterns:
                if regex.search(text_lower):
                    return {
                        'matched_level': level,
                        'pattern': regex.pattern,
                        'confidence': 0.9
                    }

        return {}

    def _build_toc_hierarchy(self, headings: List[Dict]) -> List[Dict]:
        """
        Build hierarchical TOC structure from leveled headings.
        """
        if not headings:
            return []

        toc = []
        stack = []  # Track parent headings at each level

        # Sort by page and position
        headings = sorted(headings, key=lambda h: (h['page'], h.get('position', {}).get('y', 0)))

        for heading in headings:
            level = heading['level']

            # Remove higher-level elements from stack
            while len(stack) > level:
                stack.pop()

            # Build TOC entry
            entry = {
                'title': heading.get('title', heading.get('text', '')),
                'level': level,
                'pageNumber': heading['page'],
                'confidence': heading['confidence'],
                'detection_method': heading.get('detection_method', 'unknown'),
                'children': []
            }

            # Add to parents if we have them
            if stack:
                if level == 0:
                    toc.append(entry)
                else:
                    parent = stack[-1]
                    if 'children' in parent:
                        parent['children'].append(entry)
                    else:
                        # Convert to hierarchical format
                        index = parent.get('_index', -1)
                        if index >= 0 and index < len(toc):
                            toc[index]['children'] = [entry]
            else:
                toc.append(entry)

            # Update stack
            if level < self.max_level:
                while len(stack) <= level:
                    stack.append(None)
                stack[level] = entry
                entry['_index'] = len(toc) - 1

        return toc

    def _post_process_toc(self, toc: List[Dict]) -> List[Dict]:
        """
        Post-process TOC to fix inconsistencies and add metadata.
        """
        # Flatten hierarchical structure if needed
        return self._flatten_toc(toc, 0)

    def _flatten_toc(self, entries: List[Dict], base_level: int = 0) -> List[Dict]:
        """
        Convert hierarchical structure to flat list with levels.
        """
        flat = []

        for entry in entries:
            flat_entry = {
                'title': entry['title'],
                'pageNumber': entry['pageNumber'],
                'level': entry['level'] + base_level,
                'confidence': entry['confidence'],
                'detection_method': entry.get('detection_method', 'unknown')
            }
            flat.append(flat_entry)

            # Add children recursively
            if 'children' in entry and entry['children']:
                children_flat = self._flatten_toc(entry['children'], base_level)
                flat.extend(children_flat)

        return flat

    def validate_toc_consistency(self, toc: List[Dict]) -> Dict:
        """
        Validate TOC for consistency issues.

        Returns:
            Validation report with issues and suggestions
        """
        if not toc:
            return {'valid': True, 'issues': []}

        issues = []

        # Check page ordering
        prev_page = 0
        prev_level = -1

        for i, entry in enumerate(toc):
            page = entry['pageNumber']
            level = entry['level']

            if page < prev_page:
                issues.append({
                    'type': 'page_order',
                    'severity': 'warning',
                    'message': f"Heading '{entry['title']}' appears before previous heading",
                    'index': i
                })

            # Check level progression
            if level > prev_level + 1:
                issues.append({
                    'type': 'level_gap',
                    'severity': 'info',
                    'message': f"Level jump from {prev_level} to {level}",
                    'index': i
                })

            # Check confidence
            if entry['confidence'] < self.min_confidence:
                issues.append({
                    'type': 'low_confidence',
                    'severity': 'warning',
                    'message': f"Low confidence ({entry['confidence']:.2f}) for '{entry['title']}'",
                    'index': i
                })

            prev_page = page
            prev_level = level

        return {
            'valid': len([i for i in issues if i['severity'] == 'error']) == 0,
            'issues': issues,
            'confidence': statistics.mean([e['confidence'] for e in toc]) if toc else 0
        }

    def format_toc(self, toc: List[Dict], format_type: str = 'text') -> str:
        """
        Format TOC for display.

        Args:
            toc: Table of contents structure
            format_type: 'text', 'json', or 'markdown'

        Returns:
            Formatted string representation
        """
        if format_type == 'text':
            return self._format_as_text(toc)
        elif format_type == 'json':
            import json
            return json.dumps(toc, indent=2, ensure_ascii=False)
        elif format_type == 'markdown':
            return self._format_as_markdown(toc)
        else:
            raise ValueError(f"Unknown format type: {format_type}")

    def _format_as_text(self, toc: List[Dict]) -> str:
        """
        Format TOC as indented text.
        """
        lines = []
        for entry in toc:
            indent = "  " * entry['level']
            page_str = f"Page {entry['pageNumber']}" if entry['pageNumber'] else "Unknown page"
            lines.append(f"{indent}{entry['title']} - {page_str}")
        return "\n".join(lines)

    def _format_as_markdown(self, toc: List[Dict]) -> str:
        """
        Format TOC as markdown list.
        """
        lines = []
        for entry in toc:
            indent = "  " * entry['level']
            lines.append(f"{indent}- {entry['title']} (p. {entry['pageNumber']})")
        return "\n".join(lines)