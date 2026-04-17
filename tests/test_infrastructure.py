"""
Test Suite: Infrastructure Integration (Rule #5)
Author: Kenneth Dallmier | kennydallmier@gmail.com
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestInfrastructureIntegration(unittest.TestCase):

    def test_feature_extractor_importable(self):
        """Rule #5: Verify FeatureExtractor is importable."""
        try:
            from mlaos_features.feature_extractor import FeatureExtractor  # noqa: F401
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"FeatureExtractor not importable: {e}")

    def test_serving_logger_importable(self):
        """Rule #5: Verify ServingLogger is importable."""
        try:
            from mlaos_infra.serving_logger import ServingLogger  # noqa: F401
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"ServingLogger not importable: {e}")

    def test_skew_auditor_importable(self):
        """Rule #5: Verify SkewAuditor is importable."""
        try:
            from mlaos_infra.skew_auditor import SkewAuditor  # noqa: F401
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"SkewAuditor not importable: {e}")

    def test_feature_extractor_has_required_methods(self):
        """Rule #32: FeatureExtractor must have extract_features and get_version."""
        from mlaos_features.feature_extractor import FeatureExtractor
        extractor = FeatureExtractor()
        self.assertTrue(hasattr(extractor, 'extract_features'))
        self.assertTrue(hasattr(extractor, 'get_version'))
        self.assertTrue(hasattr(extractor, 'get_feature_names'))

    def test_serving_logger_has_required_methods(self):
        """Rule #29: ServingLogger must have log_inference method."""
        from mlaos_infra.serving_logger import ServingLogger
        logger_instance = ServingLogger("postgresql://test/db", "v1.0")
        self.assertTrue(hasattr(logger_instance, 'log_inference'))
        self.assertTrue(hasattr(logger_instance, 'close'))


if __name__ == '__main__':
    unittest.main()
