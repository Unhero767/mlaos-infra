"""
Skew Auditor Module (Rule #37: Measure training/serving skew)
Author: Kenneth Dallmier | kennydallmier@gmail.com
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SkewReport:
    feature_name: str
    training_mean: float
    serving_mean: float
    skew_pct: float
    alert: bool
    threshold: float = 10.0

    @property
    def status(self) -> str:
        return 'ALERT' if self.alert else 'OK'


class SkewAuditor:
    """
    Detects training-serving skew for all features (Rule #37).
    Compares training distribution vs recent serving logs.
    """

    def __init__(self, db_conn_string: str, model_version: str,
                 skew_threshold_pct: float = 10.0):
        self.db_conn_string = db_conn_string
        self.model_version = model_version
        self.skew_threshold_pct = skew_threshold_pct

    def run_audit(self, training_stats: Dict[str, Dict]) -> List[SkewReport]:
        """
        Run skew audit comparing training stats vs serving logs.

        Args:
            training_stats: {feature_name: {'mean': float, 'std': float}}

        Returns:
            List of SkewReport for each feature
        """
        serving_stats = self._get_serving_stats()
        reports = []

        for feature_name, train_stat in training_stats.items():
            serving_stat = serving_stats.get(feature_name)
            if serving_stat is None:
                logger.warning(f"No serving data for feature: {feature_name}")
                continue

            train_mean = train_stat.get('mean', 0)
            serving_mean = serving_stat.get('mean', 0)

            if train_mean == 0:
                skew_pct = 0.0
            else:
                skew_pct = abs(serving_mean - train_mean) / abs(train_mean) * 100

            report = SkewReport(
                feature_name=feature_name,
                training_mean=train_mean,
                serving_mean=serving_mean,
                skew_pct=skew_pct,
                alert=skew_pct > self.skew_threshold_pct,
                threshold=self.skew_threshold_pct
            )
            reports.append(report)

            if report.alert:
                logger.warning(
                    f"SKEW ALERT: {feature_name} "
                    f"train={train_mean:.4f} serve={serving_mean:.4f} "
                    f"skew={skew_pct:.1f}%"
                )

        return reports

    def _get_serving_stats(self) -> Dict[str, Dict]:
        """Query serving_logs for recent feature statistics."""
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_conn_string)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT feature_name,
                           AVG((feature_value->>'value')::FLOAT) as mean,
                           STDDEV((feature_value->>'value')::FLOAT) as std
                    FROM serving_logs
                    WHERE model_version = %s
                      AND logged_at > NOW() - INTERVAL '7 days'
                    GROUP BY feature_name
                """, (self.model_version,))
                rows = cur.fetchall()
            conn.close()
            return {row[0]: {'mean': row[1], 'std': row[2]} for row in rows}
        except Exception as e:
            logger.error(f"SkewAuditor: Failed to get serving stats: {e}")
            return {}
