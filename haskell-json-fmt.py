#!/usr/bin/env python3
"""
JSON formatter with Haskell/Elm-style leading comma and brace formatting.

Output style:
{ "key":
  { "nested": "value"
  , "another": "value"
  }
, "list":
  [ "item1"
  , "item2"
  ]
}
"""

import random
import json
import yaml
import sys
import argparse
from typing import Any, TextIO


def format_value(value: Any, indent: int, indent_str: str = "  ") -> list[str]:
    """
    Format a JSON value with Haskell-style formatting.
    Returns a list of lines (without base indentation - caller handles that).
    """
    if value is None:
        return ["null"]
    elif isinstance(value, bool):
        return ["true" if value else "false"]
    elif isinstance(value, str):
        return [json.dumps(value)]
    elif isinstance(value, (int, float)):
        return [json.dumps(value)]
    elif isinstance(value, list):
        return format_array(value, indent, indent_str)
    elif isinstance(value, dict):
        return format_object(value, indent, indent_str)
    else:
        return [json.dumps(value)]


def format_array(arr: list, indent: int, indent_str: str = "  ") -> list[str]:
    """Format a JSON array with leading brackets and commas."""
    if not arr:
        return ["[]"]
    
    all_simple = all(not isinstance(item, (dict, list)) for item in arr)
    
    if all_simple and len(arr) <= 3:
        simple_repr = "[ " + ", ".join(format_value(item, indent, indent_str)[0] for item in arr) + " ]"
        if len(simple_repr) <= 60:
            return [simple_repr]
    
    lines = []
    
    for i, item in enumerate(arr):
        formatted_lines = format_value(item, indent + 1, indent_str)
        
        if i == 0:
            lines.append(f"[ {formatted_lines[0]}")
            for extra_line in formatted_lines[1:]:
                lines.append(f"{indent_str}{extra_line}")
        else:
            lines.append(f", {formatted_lines[0]}")
            for extra_line in formatted_lines[1:]:
                lines.append(f"{indent_str}{extra_line}")
    
    lines.append("]")
    return lines


def format_object(obj: dict, indent: int, indent_str: str = "  ") -> list[str]:
    """Format a JSON object with leading braces and commas."""
    if not obj:
        return ["{}"]
    
    lines = []
    items = list(obj.items())
    
    for i, (key, value) in enumerate(items):
        key_str = json.dumps(key)
        formatted_lines = format_value(value, indent + 1, indent_str)
        
        is_container = isinstance(value, (dict, list)) and len(formatted_lines) > 1
        
        if i == 0:
            if is_container:
                lines.append(f"{{ {key_str}:")
                lines.append(f"{indent_str}{formatted_lines[0]}")
                for extra_line in formatted_lines[1:]:
                    lines.append(f"{indent_str}{extra_line}")
            else:
                lines.append(f"{{ {key_str}: {formatted_lines[0]}")
        else:
            if is_container:
                lines.append(f", {key_str}:")
                lines.append(f"{indent_str}{formatted_lines[0]}")
                for extra_line in formatted_lines[1:]:
                    lines.append(f"{indent_str}{extra_line}")
            else:
                lines.append(f", {key_str}: {formatted_lines[0]}")
    
    lines.append("}")
    return lines


def format_json(data: Any, indent_str: str = "  ") -> str:
    """Format JSON data with Haskell-style formatting."""
    lines = format_value(data, 0, indent_str)
    return "\n".join(lines)

def process(inp, out, allow_yaml):
    if allow_yaml:
        data = yaml.safe_load(inp)
    else:
        data = json.load(inp)
    print(format_json(data, "  "), file=out)

def main():
    parser = argparse.ArgumentParser(
        description="Format JSON with Haskell/Elm-style leading commas and braces.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s < input.json              # Read from stdin, write to stdout
  %(prog)s input.json                # Read file, write to stdout
  %(prog)s -i input.json             # Format file in-place
  %(prog)s -i *.json                 # Format multiple files in-place
"""
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Input JSON file(s). If not provided, reads from stdin."
    )
    parser.add_argument(
        "-i", "--in-place",
        action="store_true",
        help="Edit file(s) in place."
    )
    parser.add_argument(
        "--yaml",
        action="store_true",
        help="Allow inputting YAML (to be destructively reinterpreted as JSON)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file (only valid with single input file, not with -i)"
    )
    
    args = parser.parse_args()

    if args.in_place and args.output:
        parser.error("Cannot use both -i/--in-place and -o/--output")
    
    if args.output and len(args.files) > 1:
        parser.error("-o/--output can only be used with a single input file")
    
    try:
        if not args.files:
            process(sys.stdin, sys.stdout, args.yaml)
            return
        if args.output:
            with open(args.files[0], "r", encoding="utf-8") as f:
                with open(args.output, "w", encoding="utf-8") as o:
                    process(f, o, args.yaml)
            print(f"Formatted {args.files[0]} to {args.output}", file=sys.stderr)
            return
        for filepath in args.files:
            if args.in_place:
                outfilepath = filepath + ".formatted" + random.randint(0, 1000000)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        with open(outfilepath, "w", encoding="utf-8") as o:
                            process(f, o, args.yaml)
                except:
                    os.remove(outfilepath)
                    raise
                os.rename(outfilepath, filepath)
                print(f"Formatted {filepath} in-place", file=sys.stderr)
            else:
                with open(filepath, "r", encoding="utf-8") as f:
                    process(f, sys.stdout, process.yaml)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
