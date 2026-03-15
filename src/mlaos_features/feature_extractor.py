"""
Feature Extractor Module (Rule #32: Re-use code between train and serve)
Author: Kenneth Dallmier | kennydallmier@gmail.com
Project: MLAOS Engine

CRITICAL: This module MUST be used in both training and serving pipelines.
Do NOT duplicate feature extraction logic elsewhere.
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

FEATURE_EXTRACTOR_VERSION = '1.0.0'


class FeatureExtractor:
    """
    Shared feature extraction module (Rule #32).
    Identical code path for training and serving ensures no skew.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._version = FEATURE_EXTRACTOR_VERSION
        self._config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load feature config from YAML file."""
        if config_path is None:
            return self._default_config()
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")
            return self._default_config()

    def _default_config(self) -> Dict:
        return {
            'resonance_clip': (0.0, 1.0),
            'chiaroscuro_clip': (0.0, 1.0),
            'vector_dimensions': 3
        }

    def get_version(self) -> str:
        """Return version string for train/serve consistency checks."""
        return self._version

    def extract_features(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize features from raw input.
        MUST produce identical output for identical input (deterministic).

        Args:
            raw_data: Raw input dict with sensor/model data

        Returns:
            Dict of normalized, ready-to-use features
        """
        features = {}

        # resonance_score (Rule #11: registered in feature_registry)
        if 'resonance_raw' in raw_data:
            clip = self._config.get('resonance_clip', (0.0, 1.0))
            features['resonance_score'] = float(
                max(clip[0], min(clip[1], raw_data['resonance_raw']))
            )

        # chiaroscuro_index
        if 'light_intensity' in raw_data and 'dark_intensity' in raw_data:
            light = float(raw_data['light_intensity'])
            dark = float(raw_data['dark_intensity'])
            total = light + dark
            if total > 0:
                features['chiaroscuro_index'] = round(light / total, 6)
            else:
                features['chiaroscuro_index'] = 0.5

        # memory_vector
        if 'memory_vector' in raw_data:
            vec = raw_data['memory_vector']
            norm = sum(v ** 2 for v in vec) ** 0.5
            if norm > 0:
                features['memory_vector'] = [round(v / norm, 6) for v in vec]
            else:
                features['memory_vector'] = vec

        return features

    def get_feature_names(self) -> List[str]:
        """Return list of all feature names this extractor produces."""
        return ['resonance_score', 'chiaroscuro_index', 'memory_vector',
                'archetype_alignment']
