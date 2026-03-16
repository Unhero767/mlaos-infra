import pandas as pd
import psycopg2
from scipy import stats
from typing import Tuple, Dict

class SkewAuditor:
    """Rule #37: Measure Training/Serving Skew"""
    
    def __init__(self, db_conn_string: str):
        self.db_conn_string = db_conn_string
    
    def measure_skew(self, training_data: pd.DataFrame, serving_data: pd.DataFrame, 
                     feature_name: str, threshold: float = 0.05) -> Dict:
        train_values = training_data[feature_name].dropna()
        serve_values = serving_data[feature_name].dropna()
        
        ks_statistic, p_value = stats.ks_2samp(train_values, serve_values)
        
        return {
            'feature_name': feature_name,
            'ks_statistic': ks_statistic,
            'p_value': p_value,
            'skew_detected': p_value < threshold,
            'train_mean': train_values.mean(),
            'serve_mean': serve_values.mean(),
            'mean_difference': abs(train_values.mean() - serve_values.mean())
        }
    
    def audit_all_features(self, threshold: float = 0.05):
        """Rule #37: Audit all features for skew"""
        conn = psycopg2.connect(self.db_conn_string)
        train_query = "SELECT * FROM training_data"
        train_df = pd.read_sql_query(train_query, conn)
        
        serve_query = "SELECT * FROM serving_logs WHERE served_at > NOW() - INTERVAL '7 days'"
        serve_df = pd.read_sql_query(serve_query, conn)
        conn.close()
        
        results = []
        for feature_name in train_df.columns:
            if feature_name in serve_df.columns:
                result = self.measure_skew(train_df, serve_df, feature_name, threshold)
                results.append(result)
        
        return results
