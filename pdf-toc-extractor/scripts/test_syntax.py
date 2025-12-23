#!/usr/bin/env python3
"""Test that the extraction script has correct syntax without running it."""

import ast
import sys
def test_syntax():
    try:
        with open('/tmp/pdf-toc-extractor/scripts/extract_toc.py', 'r') as f:
            source = f.read()

        # Parse the script to check syntax
        ast.parse(source)
        print("✓ Syntax is valid!")

        # Check for key functions
        tree = ast.parse(source)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        expected_functions = ['extract_pdf_toc', 'process_outline_items', 'get_page_number', 'toc_to_text', 'toc_to_json']

        for func in expected_functions:
            if func in functions:
                print(f"✓ Function '{func}' found")
            else:
                print(f"✗ Function '{func}' missing")

        return True

    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_syntax()
    sys.exit(0 if success else 1)