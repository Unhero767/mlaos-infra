import unittest
from unittest.mock import patch
import pandas as pd
from src.mlaos_infra.skew_auditor import SkewAuditor


class TestSkewAuditor(unittest.TestCase):

    def setUp(self):
        self.auditor = SkewAuditor("postgresql://fake:fake@localhost/db")

    def test_measure_skew_detects_drift(self):
        """Rule #37: Verify the KS test successfully catches data drift."""
        # Create a clean training distribution
        train_data = pd.DataFrame({'resonance_score': [0.5, 0.52, 0.48, 0.51, 0.49]})
        # Create a heavily skewed serving distribution
        serve_data = pd.DataFrame({'resonance_score': [0.9, 0.95, 0.88, 0.92, 0.91]})

        result = self.auditor.measure_skew(train_data, serve_data, 'resonance_score', threshold=0.05)

        self.assertTrue(result['skew_detected'])
        self.assertEqual(result['feature_name'], 'resonance_score')

    @patch('src.mlaos_infra.skew_auditor.psycopg2.connect')
    @patch('src.mlaos_infra.skew_auditor.pd.read_sql_query')
    def test_audit_all_features_mocked(self, mock_read_sql, mock_connect):
        """Test the full audit loop using mocked database queries."""
        # Feed it fake SQL query results
        mock_read_sql.side_effect = [
            pd.DataFrame({'feat1': [0.1, 0.2], 'feat2': [0.5, 0.6]}),  # training data
            pd.DataFrame({'feat1': [0.1, 0.22], 'feat2': [0.9, 0.95]})  # serving data
        ]

        results = self.auditor.audit_all_features()
        self.assertEqual(len(results), 2)  # Should have audited both features
