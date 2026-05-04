import time

class SubterraneanChamber:
    """
    A sink for Glitch-Wastes requiring manual Sovereign clearance.
    """
    def __init__(self):
        self.wastes = []
        self.sealed = True

    def quarantine(self, corrupt_data: any, error_manifest: str):
        entry = {
            "timestamp": time.ctime(),
            "payload": str(corrupt_data),
            "manifest": error_manifest
        }
        self.wastes.append(entry)
        print(f"[Subterranean] Glitch-Waste Trapped: {error_manifest}")

    def inspect_wastes(self):
        """View the trapped entropy before purging."""
        if not self.wastes:
            print("[Subterranean] Chamber is empty. ◦A is absolute.")
            return
        for i, waste in enumerate(self.wastes):
            print(f"Index: {i} | Time: {waste['timestamp']} | Error: {waste['manifest']}")

    def sovereign_purge(self, architect_key: str):
        """Requires the correct key to clear the chamber."""
        # In a real scenario, this would check against a Tier 1 Hash
        if architect_key == "SIGMA_7_PURGE":
            waste_count = len(self.wastes)
            self.wastes = []
            print(f"[Subterranean] Sovereign Command Executed. {waste_count} fragments erased.")
        else:
            print("[Ex◦] Access Denied: Invalid Architect Key.")

SINK = SubterraneanChamber()
