"""
Test Suite: ServingLogger (Rule #5: Test infrastructure independently)
Author: Kenneth Dallmier | kennydallmier@gmail.com
"""

import unittest
import uuid


class TestServingLogger(unittest.TestCase):

    def test_logger_fails_silently_on_bad_connection(self):
        """Rule #5 & #10: Logger must not crash inference on DB failure."""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            from mlaos_infra.serving_logger import ServingLogger
        except ImportError:
            self.skipTest("ServingLogger not importable in this environment")

        bad_logger = ServingLogger(
            "postgresql://invalid:invalid@localhost:9999/nonexistent",
            "TEST-v0.1"
        )

        # This should NOT raise an exception (fail silently)
        try:
            result = bad_logger.log_inference(
                str(uuid.uuid4()), "test_mem_001", {'score': 0.5}
            )
            # Should return False, not raise
            self.assertFalse(result)
        except Exception as e:
            self.fail(f"ServingLogger raised an exception instead of failing silently: {e}")

    def test_logger_initializes_with_correct_params(self):
        """Test that ServingLogger stores constructor params correctly."""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            from mlaos_infra.serving_logger import ServingLogger
        except ImportError:
            self.skipTest("ServingLogger not importable in this environment")

        logger = ServingLogger("postgresql://test/db", "AURELIA-v2.3", "staging")
        self.assertEqual(logger.model_version, "AURELIA-v2.3")
        self.assertEqual(logger.environment, "staging")


if __name__ == '__main__':
    unittest.main()
