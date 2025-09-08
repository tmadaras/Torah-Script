
import os, csv, sys, json
from jsonschema import validate, Draft202012Validator

def load_schema(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_row(row, schema):
    int_fields = ['source_chapter','source_verse','source_word_position','canon_chapter','canon_verse','canon_word_position']
    casted = {}
    for k,v in row.items():
        if k in int_fields:
            try:
                casted[k] = int(v) if v != '' else None
            except ValueError:
                casted[k] = v
        else:
            casted[k] = v
    errors = sorted(Draft202012Validator(schema).iter_errors(casted), key=lambda e: e.path)
    return casted, errors

def main(csv_path, schema_path):
    schema = load_schema(schema_path)
    bad = 0; total = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            total += 1
            casted, errs = validate_row(row, schema)
            if errs:
                bad += 1
                print(f"Row {i}: INVALID")
                for e in errs:
                    print("  -", e.message, "at", list(e.path))
    if bad:
        print(f"\nFAILED: {bad}/{total} rows invalid.")
        sys.exit(1)
    print(f"OK: {total} rows valid.")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python validate_csv.py <mapping.csv> <schema.json>")
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
