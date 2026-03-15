"""
Pruning Automation (Rule #22: Clean up unused features)
Identifies and flags features that haven't been used recently.
Author: Kenneth Dallmier | kennydallmier@gmail.com
"""

import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('pruning_automation')

PRUNING_THRESHOLD_DAYS = int(os.environ.get('PRUNING_THRESHOLD_DAYS', '30'))


def get_unused_features(db_conn_string: str,
                        threshold_days: int = PRUNING_THRESHOLD_DAYS) -> List[Dict]:
    """
    Identify features in registry not seen in serving logs recently.
    Rule #22: Remove features that are no longer being used.
    """
    try:
        import psycopg2
        conn = psycopg2.connect(db_conn_string)
        cutoff = datetime.now(timezone.utc) - timedelta(days=threshold_days)

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    fr.feature_name,
                    fr.owner_email,
                    fr.last_used_at,
                    fr.status,
                    COALESCE(sl.last_served, 'never') as last_served
                FROM feature_registry fr
                LEFT JOIN (
                    SELECT feature_name, MAX(logged_at) as last_served
                    FROM serving_logs
                    GROUP BY feature_name
                ) sl ON fr.feature_name = sl.feature_name
                WHERE fr.status = 'ACTIVE'
                  AND (sl.last_served IS NULL OR sl.last_served < %s)
                ORDER BY sl.last_served ASC NULLS FIRST
            """, (cutoff,))
            rows = cur.fetchall()
        conn.close()

        return [
            {
                'feature_name': row[0],
                'owner_email': row[1],
                'last_used_at': row[2],
                'status': row[3],
                'last_served': row[4]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Failed to get unused features: {e}")
        return []


def run_pruning_report():
    """Generate pruning report for owner review."""
    db_conn = os.environ.get('DATABASE_URL', '')
    if not db_conn:
        logger.error("DATABASE_URL not set.")
        sys.exit(1)

    unused = get_unused_features(db_conn)

    print(f"\n{'='*60}")
    print(f"PRUNING REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Features unused for >{PRUNING_THRESHOLD_DAYS} days")
    print(f"{'='*60}")

    if not unused:
        print("No features flagged for pruning. All features are active!")
        return

    for feature in unused:
        print(f"\n  Feature: {feature['feature_name']}")
        print(f"  Owner:   {feature['owner_email']}")
        print(f"  Last Served: {feature['last_served']}")
        print(f"  Action: Contact owner to deprecate or reactivate")

    print(f"\n{'='*60}")
    print(f"Total flagged: {len(unused)} feature(s)")
    print("NOTE: This is a REPORT only. No features were automatically deleted.")
    print("Owner approval required before marking DEPRECATED.")


if __name__ == '__main__':
    run_pruning_report()
