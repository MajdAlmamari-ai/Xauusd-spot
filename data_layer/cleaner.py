# data_layer/cleaner.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    """تنظيف البيانات"""
    
    @staticmethod
    def clean(df):
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        if 'time' in df.columns:
            df = df.drop_duplicates(subset=['time'])
        
        df = df.fillna(method='ffill')
        
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                df = df[(df[col] >= mean - 3*std) & (df[col] <= mean + 3*std)]
        
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            df = df.sort_values('time')
        
        return df
