import pandas as pd
import json
import sys
from pathlib import Path

def excel_to_json(excel_path, output_path):
    df = pd.read_excel(excel_path)

    if not {'original', 'transformed'}.issubset(df.columns):
        raise ValueError("Excel must have 'original' and 'transformed' columns")

    data = df.to_dict(orient = 'records')

    if output_path is None:
        output_path = Path(excel_path).with_suffix('.json')

    with open(output_path, 'w', encoding = 'utf-8') as f:
        json.dump(data, f, ensure_ascii = False, indent = 4)

    print(f"JSON saved to: {output_path}")

def semicolon_csv_to_json(input_path, output_path):
    data = []

    with open(input_path, 'r', encoding = 'utf-8') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if ';' not in line:
                continue

            original, transformed = line.split(';', 1)
            data.append({"original": original.strip(), "transformed": transformed.strip()})

    if output_path is None:
        output_path = Path(input_path).with_suffix('.json')

    with open(output_path, 'w', encoding = 'utf-8') as f:
        json.dump(data, f, ensure_ascii = False, indent = 4)

    print(f"Converted {len(data)} entries to JSON: {output_path}")