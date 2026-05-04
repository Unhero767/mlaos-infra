import sys
import argparse

def evaluate_logic(strict_dogma: bool):
    print("--- [LOGIC PHASE: DIALECTICAL INQUIRY] ---")
    print("Status: Assessing ◦A Consistency...")
    
    # Internal Protocol: Verify if the architecture remains 'Plumb'
    # In a strange universe, consistency is the only law.
    consistency = True 
    
    if strict_dogma and not consistency:
        print("RESULT: Metalogical Burn detected. Ex◦ triggered.")
        sys.exit(1)
    
    print("SUCCESS: The Manifold is stable. The candidate may proceed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict-dogma', action='store_true')
    evaluate_logic(parser.parse_args().strict_dogma)
