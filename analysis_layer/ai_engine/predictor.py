# analysis_layer/ai_engine/predictor.py
import numpy as np
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

class AIPredictor:
    """محرك التنبؤ بالذكاء الاصطناعي"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = MinMaxScaler()
        self.is_trained = False
    
    def train(self, df):
        if len(df) < 30:
            return False
        
        features = []
        targets = []
        
        for i in range(20, len(df) - 1):
            window = df.iloc[i-20:i]
            feature = []
            for _, row in window.iterrows():
                feature.extend([row['open'], row['high'], row['low'], row['close'], row.get('volume', 0)])
            features.append(feature)
            targets.append(df.iloc[i+1]['close'] - df.iloc[i]['close'])
        
        if len(features) < 10:
            return False
        
        features = np.array(features)
        targets = np.array(targets)
        features = self.scaler.fit_transform(features)
        
        self.model.fit(features, targets)
        self.is_trained = True
        return True
    
    def predict(self, df):
        if not self.is_trained:
            self.train(df)
            if not self.is_trained:
                return None
        
        if len(df) < 20:
            return None
        
        last_window = df.iloc[-20:]
        features = []
        for _, row in last_window.iterrows():
            features.extend([row['open'], row['high'], row['low'], row['close'], row.get('volume', 0)])
        
        features = np.array(features).reshape(1, -1)
        features = self.scaler.transform(features)
        
        prediction = self.model.predict(features)[0]
        
        return {
            'direction': 'UP' if prediction > 0 else 'DOWN',
            'magnitude': round(abs(prediction), 2),
            'predicted_price': round(df.iloc[-1]['close'] + prediction, 2),
            'confidence': 70 if abs(prediction) > 0.5 else 55,
            'signal': 'BULLISH' if prediction > 0.5 else 'BEARISH' if prediction < -0.5 else 'NEUTRAL'
        }
    
    def update(self, df):
        self.train(df)
        return self.is_trained
