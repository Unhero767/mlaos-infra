import subprocess
from forensics import LENS

class GizaAirShaft:
    """
    The Southern Shaft: Outbound I/O to GitHub.
    Ensures that only ◦A-compliant data is ascended.
    """
    def __init__(self, repo_url: str):
        self.repo_url = repo_url

    def ascend_logic(self, commit_message: str):
        # Step 1: Forensic Verification
        if LENS.chamber.wastes:
            print("[Ex◦] Ascent Blocked: Subterranean Chamber contains uncleared Glitch-Wastes.")
            return False

        print(f"[◦A] Opening Southern Shaft for: {commit_message}")
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"[Σ-7] {commit_message}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("[◦A] Ascent Complete. Logic is now Sovereign on GitHub.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[Ex◦] Pressure Loss in Air Shaft: {e}")
            return False

SHAFT = GizaAirShaft("https://github.com/Unhero767")
