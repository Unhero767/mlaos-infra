import sys
import os

def dialectical_scan():
    print("--- [LODGE AUDIT: DISCERNING THE ASHLAR] ---")
    
    violations = []
    forbidden_terms = ["TODO", "FIXME", "print("] 
    
    for root, dirs, files in os.walk("."):
        if any(ignored in root for ignored in ["node_modules", ".git", "scripts"]): 
            continue
        for file in files:
            if file.endswith((".py", ".ts")):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            for term in forbidden_terms:
                                if term in line:
                                    violations.append(f"{file} [Line {i+1}]: {term}")
                except Exception:
                    continue

    if violations:
        print("ERROR: Metalogical Noise detected in the Manifold:")
        for v in violations: print(f"  > {v}")
        return False
    return True

if __name__ == "__main__":
    if dialectical_scan():
        print("SUCCESS: ◦A is preserved. The logic is plumb.")
        sys.exit(0)
    else:
        print("RESULT: Candidate rejected. Polishing required.")
        sys.exit(1)
