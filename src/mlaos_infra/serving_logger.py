"""
ServingLogger: Log inference requests to PostgreSQL
Author: Kenneth Dallmier | kennydallmier@gmail.com
"""

import logging
import psycopg2
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ServingLogger:
    """Logs inference requests and responses to database."""
    
    def __init__(self, db_url, model_version, environment="production"):
        """
        Args:
            db_url: PostgreSQL connection string
            model_version: Model version string (e.g., 'AURELIA-v2.3')
            environment: Deployment environment (dev/staging/production)
        """
        self.db_url = db_url
        self.model_version = model_version
        self.environment = environment
    
    def log_inference(self, request_id, memory_id, features):
        """
        Log an inference request to the database.
        Fails silently on connection errors (Rule #10).
        
        Args:
            request_id: Unique request identifier
            memory_id: Memory identifier
            features: Feature dictionary
            
        Returns:
            True on success, False/None on failure
        """
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO serving_logs (request_id, memory_id, model_version, features, logged_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """
            
            cursor.execute(query, (
                request_id,
                memory_id,
                self.model_version,
                str(features),
                datetime.now(timezone.utc)
            ))
            
            log_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            return log_id
            
        except Exception as e:
            logger.warning("ServingLogger: DB connection failed: %s", e)
            return None  # Fail silently
    
    def close(self):
        """Cleanup method for context manager compatibility."""
        pass
