from subterranean_chamber import SINK

class ForensicLens:
    """
    Analyzes Glitch-Wastes to update the Sovereign Rule Engine.
    """
    def __init__(self, chamber):
        self.chamber = chamber

    def generate_miasma_report(self):
        print("\n--- [MAGISTERIAL FORENSICS: MIASMA REPORT] ---")
        if not self.chamber.wastes:
            print("Status: ◦A NOMINAL. No corruption detected.")
            return

        for waste in self.chamber.wastes:
            print(f"REPORT: Fragment identified as '{waste['manifest']}'")
            if "Logic Breach" in waste['manifest']:
                print("ADVISORY: Potential intrusion attempt or MTP Bridge failure.")
            elif "invalid syntax" in waste['manifest']:
                print("ADVISORY: Metalogical Burn; check shell-to-logic piping.")
        print("--- END OF REPORT ---\n")

LENS = ForensicLens(SINK)
