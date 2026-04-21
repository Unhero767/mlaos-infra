from giza_module import GizaReactor
from subterranean_chamber import SINK

class IntegratedGiza(GizaReactor):
    def secure_allocate(self, magnitude: any, intent: str):
        try:
            # Attempting to force magnitude into an integer (Logic Bridge)
            m = int(magnitude)
            return self.allocate_resource(m, intent)
        except Exception as e:
            # If the Logic Bridge breaks, divert to the Subterranean Chamber
            SINK.quarantine(magnitude, str(e))
            return False

if __name__ == "__main__":
    giza = IntegratedGiza(500)
    # Success case
    giza.secure_allocate(200, "Core Lighting")
    # Glitch case: Passing a string where an int should be
    giza.secure_allocate("CORRUPTION_VECTOR", "External Breach Attempt")
