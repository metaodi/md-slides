"""Command-line interface for md-docs."""

import argparse
import sys

from md_slides import __version__
from md_slides.doc_converter import convert_doc
from md_slides.parser import parse_markdown_doc


def main():
    """Entry point for the md-docs CLI."""
    parser = argparse.ArgumentParser(
        prog="md-docs",
        description="Convert a Markdown file into a Word document.",
    )
    parser.add_argument("input", help="Path to the input Markdown (.md) file.")
    parser.add_argument(
        "-o",
        "--output",
        default="output.docx",
        help="Path for the output .docx file (default: output.docx).",
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Path to a custom .docx template file (default: bundled template).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Read markdown input
    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        print(f"Error: input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading '{args.input}': {exc}", file=sys.stderr)
        sys.exit(1)

    # Parse markdown into document elements
    elements = parse_markdown_doc(content)
    if not elements:
        print("Warning: no content found in the input file.", file=sys.stderr)

    # Convert to DOCX
    try:
        output_path = convert_doc(elements, args.output, template_path=args.template)
    except Exception as exc:  # noqa: BLE001
        print(f"Error generating document: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Document saved to '{output_path}'.")


if __name__ == "__main__":
    main()
