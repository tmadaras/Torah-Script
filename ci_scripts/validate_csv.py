
# Fallback validator that mirrors the pack's validator behavior.
import sys, json, csv
from jsonschema import Draft202012Validator
def main(csv_path, schema_path):
    with open(schema_path,'r',encoding='utf-8') as f: schema=json.load(f)
    val = Draft202012Validator(schema)
    bad=0; total=0
    with open(csv_path, newline='', encoding='utf-8') as f:
        r=csv.DictReader(f)
        for i,row in enumerate(r,start=2):
            total+=1
            errs=list(val.iter_errors(row))
            if errs:
                bad+=1
                print(f"Row {i}: INVALID")
                for e in errs: print(" -",e.message,"at",list(e.path))
    if bad:
        print(f"FAILED: {bad}/{total} invalid"); sys.exit(1)
    print(f"OK: {total} valid")
if __name__=='__main__':
    if len(sys.argv)<3: print("Usage: python validate_csv.py <csv> <schema.json>"); sys.exit(2)
    main(sys.argv[1], sys.argv[2])
