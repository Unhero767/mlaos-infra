#!/usr/bin/env python3
import os
import re
import sys
import json
import argparse
from datetime import datetime

# Protocol Parameters (adjust if your layout differs)
REGISTRY_PATH = "sql/001_feature_registry.sql"
SOURCE_DIR = "src/mlaos_infra/"
FID_PATTERN = re.compile(r"FID:\s*([A-Za-z0-9_]+)")
SQL_PATTERN = re.compile(
    r"INSERT\s+INTO\s+feature_registry\s*$$.*?feature_id\s*,\s*.*?$$\s*VALUES\s*\(\s*['\"](.*?)['\"]",
    re.IGNORECASE | re.DOTALL,
)

def extract_registered_ids(path=REGISTRY_PATH):
    """Extracts all authorized Feature IDs from the SQL ledger."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return set(), f"Registry file not found: {path}"
    ids = set(SQL_PATTERN.findall(content))
    return ids, None

def extract_manifested_ids(source_dir=SOURCE_DIR):
    """Scans src/ for all active logic identifiers (FID tags)."""
    found_ids = set()
    missing_files = []
    if not os.path.isdir(source_dir):
        return found_ids, f"Source directory not found: {source_dir}"
    for root, _, files in os.walk(source_dir):
        for fname in files:
            if fname.endswith(".py"):
                full = os.path.join(root, fname)
                try:
                    with open(full, 'r', encoding='utf-8') as fh:
                        text = fh.read()
                    found_ids.update(FID_PATTERN.findall(text))
                except Exception as e:
                    missing_files.append({"file": full, "error": str(e)})
    return found_ids, missing_files if missing_files else None

from datetime import datetime, timezone

def make_report(registered, manifested, unregistered, errors):

    return {
       "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "registered_count": len(registered),
        "manifested_count": len(manifested),
        "unregistered": sorted(list(unregistered)),
        "errors": errors,
    }

def save_report(report, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

def audit_consistency(output_path=None):
    registered, reg_err = extract_registered_ids()
    manifested, src_err = extract_manifested_ids()

    errors = {}
    if reg_err:
        errors["registry_error"] = reg_err
    if src_err:
        errors["source_errors"] = src_err

    unregistered = set(manifested) - set(registered)

    report = make_report(registered, manifested, unregistered, errors)

    if output_path:
        save_report(report, output_path)

    # Human output
    if reg_err:
        print(f"ERROR: {reg_err}", file=sys.stderr)
    if src_err:
        print(f"WARNING: source scanning issues: {src_err}", file=sys.stderr)

    if unregistered:
        print(f"Metalogical Fault: Ghost Logic detected. Unregistered FIDs: {sorted(list(unregistered))}", file=sys.stderr)
        print(f"Audit report written to: {output_path}" if output_path else "No output file specified.")
        sys.exit(1)

    print(f"◦A Verified: All {len(manifested)} manifested logic strands are anchored to the Registry.")
    if output_path:
        print(f"Audit report written to: {output_path}")
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify code FIDs are registered in the feature registry.")
    parser.add_argument("--output", "-o", default="artifacts/audit_report.json", help="Path to write JSON audit report.")
    parser.add_argument("--registry", "-r", default=REGISTRY_PATH, help="Path to feature registry SQL file.")
    parser.add_argument("--src", "-s", default=SOURCE_DIR, help="Source directory to scan.")
    args = parser.parse_args()

    # allow overrides via args
    REGISTRY_PATH = args.registry
    SOURCE_DIR = args.src

    audit_consistency(output_path=args.output)
