#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import argparse

def print_help():
    """Display detailed help message"""
    help_text = """
Excel to CSV Converter

DESCRIPTION:
    Converts an Excel file (.xls, .xlsx, .xlsm) to CSV format while
    preserving data integrity and formatting.

USAGE:
    python excel_to_csv.py <input_file> [output_file] [options]

ARGUMENTS:
    input_file         Path to the Excel file to convert
    output_file       (Optional) Path for the output CSV file
                     If not provided, will use the same name with .csv extension

OPTIONS:
    -h, --help        Show this help message

EXAMPLES:
    # Basic usage (output will be input_file.csv)
    python excel_to_csv.py input.xlsx

    # Specify output file
    python excel_to_csv.py input.xlsx output.csv

NOTE:
    The input file must be a valid Excel file (.xls, .xlsx, or .xlsm)
    The output will be encoded in UTF-8
    """
    print(help_text)

def excel_to_csv(excel_path, output_path=None):
    """
    Convert an Excel file to CSV.
    
    Args:
        excel_path (str): Path to the Excel file
        output_path (str, optional): Output path for the CSV file
        
    Returns:
        str: Path of the created CSV file
        
    Raises:
        ValueError: If the input file is not an Excel file
        FileNotFoundError: If the Excel file doesn't exist
        OSError: If the output directory doesn't exist
    """
    # Check if file exists
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"File not found: '{excel_path}'")
    
    # Check if it's an Excel file
    valid_extensions = ['.xlsx', '.xls', '.xlsm']
    if not any(excel_path.lower().endswith(ext) for ext in valid_extensions):
        raise ValueError(f"File must be an Excel file {valid_extensions}")
    
    # Set default output path if none provided
    if output_path is None:
        output_path = os.path.splitext(excel_path)[0] + '.csv'
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            raise OSError(f"Cannot create output directory: {str(e)}")
    
    # Read Excel file
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {str(e)}")
    
    # Save to CSV
    try:
        df.to_csv(output_path, index=False, encoding='utf-8')
        return output_path
    except Exception as e:
        raise OSError(f"Error saving CSV file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description='Convert Excel file to CSV',
        add_help=False
    )
    parser.add_argument('input_file', nargs='?',
                       help='Path to the Excel file to convert')
    parser.add_argument('output_file', nargs='?',
                       help='Path for the output CSV file')
    parser.add_argument('-h', '--help', action='store_true',
                       help='Show this help message')
    
    try:
        args = parser.parse_args()
        
        # Show help if requested or if no input file
        if args.help or not args.input_file:
            print_help()
            sys.exit(0)
        
        # Convert the file
        output_path = excel_to_csv(args.input_file, args.output_file)
        print(f"Conversion successful! CSV file created: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        print("\nFor more information about usage:", file=sys.stderr)
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
