"""
Skew Analysis Runner (Rule #37: Measure training/serving skew)
Run weekly to detect distribution drift.
Author: Kenneth Dallmier | kennydallmier@gmail.com
"""

import os
import sys
import logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('skew_analysis')

# Example training statistics (replace with actual training pipeline output)
TRAINING_STATS = {
    'resonance_score': {'mean': 0.72, 'std': 0.15},
    'chiaroscuro_index': {'mean': 0.54, 'std': 0.22},
    'archetype_alignment': {'mean': 0.68, 'std': 0.18},
}


def run_skew_analysis():
    """Run full skew audit and print report."""
    db_conn = os.environ.get('DATABASE_URL', '')
    model_version = os.environ.get('MODEL_VERSION', 'AURELIA-v2.3')

    if not db_conn:
        logger.error("DATABASE_URL environment variable not set.")
        sys.exit(1)

    try:
        from mlaos_infra.skew_auditor import SkewAuditor
    except ImportError as e:
        logger.error(f"Could not import SkewAuditor: {e}")
        sys.exit(1)

    auditor = SkewAuditor(
        db_conn_string=db_conn,
        model_version=model_version,
        skew_threshold_pct=10.0
    )

    logger.info(f"Running skew audit for model version: {model_version}")
    reports = auditor.run_audit(TRAINING_STATS)

    print(f"\n{'='*60}")
    print(f"SKEW AUDIT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model Version: {model_version}")
    print(f"{'='*60}")
    print(f"{'Feature':<30} {'Train Mean':>10} {'Serve Mean':>10} {'Skew %':>8} {'Status':>8}")
    print(f"{'-'*60}")

    alerts = 0
    for report in reports:
        status = '⚠️ ALERT' if report.alert else '✅ OK'
        print(f"{report.feature_name:<30} {report.training_mean:>10.4f} "
              f"{report.serving_mean:>10.4f} {report.skew_pct:>7.1f}% {status:>8}")
        if report.alert:
            alerts += 1

    print(f"{'='*60}")
    print(f"Total features: {len(reports)} | Alerts: {alerts}")

    if alerts > 0:
        logger.warning(f"{alerts} feature(s) have skew above threshold. Review immediately.")
        sys.exit(1)
    else:
        logger.info("All features within acceptable skew thresholds.")


if __name__ == '__main__':
    run_skew_analysis()
