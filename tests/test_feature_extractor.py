"""
Test Suite: FeatureExtractor (Rule #32: Re-use code train/serve)
Author: Kenneth Dallmier | kennydallmier@gmail.com
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from mlaos_features.feature_extractor import FeatureExtractor
    IMPORT_OK = True
except ImportError:
    IMPORT_OK = False


@unittest.skipUnless(IMPORT_OK, "FeatureExtractor not importable")
class TestFeatureExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = FeatureExtractor()

    def test_version_is_consistent(self):
        """Rule #32: Training and serving must use identical versions."""
        extractor_a = FeatureExtractor()
        extractor_b = FeatureExtractor()
        self.assertEqual(
            extractor_a.get_version(),
            extractor_b.get_version(),
            "Extractor versions must be identical across instances"
        )

    def test_feature_extraction_deterministic(self):
        """Same input MUST produce same output every time."""
        raw_data = {
            'resonance_raw': 0.75,
            'light_intensity': 0.8,
            'dark_intensity': 0.2,
            'memory_vector': [0.5, 0.5, 0.5]
        }
        outputs = [self.extractor.extract_features(raw_data) for _ in range(10)]
        for i in range(1, len(outputs)):
            self.assertEqual(
                outputs[0], outputs[i],
                f"Feature extraction was non-deterministic on run {i}"
            )

    def test_resonance_score_clipped(self):
        """resonance_score must be clipped to [0.0, 1.0]."""
        over_raw = {'resonance_raw': 1.5}
        under_raw = {'resonance_raw': -0.5}
        over_features = self.extractor.extract_features(over_raw)
        under_features = self.extractor.extract_features(under_raw)
        self.assertLessEqual(over_features['resonance_score'], 1.0)
        self.assertGreaterEqual(under_features['resonance_score'], 0.0)

    def test_chiaroscuro_index_range(self):
        """chiaroscuro_index must be between 0 and 1."""
        raw = {'light_intensity': 0.8, 'dark_intensity': 0.2}
        features = self.extractor.extract_features(raw)
        self.assertGreaterEqual(features['chiaroscuro_index'], 0.0)
        self.assertLessEqual(features['chiaroscuro_index'], 1.0)

    def test_memory_vector_normalized(self):
        """memory_vector must be unit-normalized."""
        raw = {'memory_vector': [3.0, 4.0, 0.0]}
        features = self.extractor.extract_features(raw)
        vec = features['memory_vector']
        magnitude = sum(v ** 2 for v in vec) ** 0.5
        self.assertAlmostEqual(magnitude, 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
