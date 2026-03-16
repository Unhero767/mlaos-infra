def log_inference(self, request_id, memory_id, features):
    try:
        conn = psycopg2.connect(self.db_url)
    except Exception as e:
        logger.warning("ServingLogger: DB connection failed: %s", e)
        return None  # <–– add/ensure this
    ...
