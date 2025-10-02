"""
Machine Learning Anomaly Detection System for Cybersecurity Honeypot
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pickle
import json
import hashlib
from pathlib import Path

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from database.connection import SessionLocal
from database.models import AttackEvent, MLModel

logger = logging.getLogger(__name__)

class Autoencoder(nn.Module):
    """Simple autoencoder for anomaly detection"""
    
    def __init__(self, input_dim: int, hidden_dim: int = 32):
        super(Autoencoder, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2)
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, input_dim)
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
    
    def encode(self, x):
        return self.encoder(x)

class AnomalyDetector:
    """Main anomaly detection system"""
    
    def __init__(self):
        self.isolation_forest = None
        self.autoencoder = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        self.is_trained = False
        
        # Feature extraction parameters
        self.url_patterns = [
            "sql", "union", "select", "insert", "delete", "update", "drop",
            "script", "javascript", "onerror", "onload", "alert",
            "admin", "login", "auth", "password", "user",
            "../", "..\\", "/etc/passwd", "/windows/system32",
            "eval", "exec", "system", "cmd", "shell"
        ]
        
        self.user_agent_patterns = [
            "sqlmap", "nikto", "nmap", "burp", "zap", "scanner",
            "bot", "crawler", "spider", "scraper", "automated"
        ]
    
    async def load_model(self):
        """Load pre-trained models"""
        try:
            logger.info("🧠 Loading ML models...")
            
            # Try to load existing models
            if (self.model_path / "isolation_forest.pkl").exists():
                with open(self.model_path / "isolation_forest.pkl", "rb") as f:
                    self.isolation_forest = pickle.load(f)
                logger.info("✅ Isolation Forest model loaded")
            
            if (self.model_path / "autoencoder.pth").exists():
                self.autoencoder = torch.load(self.model_path / "autoencoder.pth")
                self.autoencoder.eval()
                logger.info("✅ Autoencoder model loaded")
            
            if (self.model_path / "scaler.pkl").exists():
                with open(self.model_path / "scaler.pkl", "rb") as f:
                    self.scaler = pickle.load(f)
                logger.info("✅ Scaler loaded")
            
            if (self.model_path / "feature_config.json").exists():
                with open(self.model_path / "feature_config.json", "r") as f:
                    config = json.load(f)
                    self.feature_columns = config.get("feature_columns", [])
                    self.label_encoders = config.get("label_encoders", {})
                logger.info("✅ Feature configuration loaded")
            
            # If no models exist, train new ones
            if not self.isolation_forest or not self.autoencoder:
                await self.train_models()
            
            self.is_trained = True
            logger.info("🎯 ML models ready for anomaly detection")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            # Train new models if loading fails
            await self.train_models()
    
    async def train_models(self):
        """Train ML models with existing data"""
        try:
            logger.info("🎓 Training ML models...")
            
            # Get training data from database
            training_data = await self._get_training_data()
            
            if len(training_data) < 100:
                logger.warning("⚠️ Insufficient training data, using synthetic data")
                training_data = await self._generate_synthetic_data(1000)
            
            # Extract features
            X = await self._extract_features(training_data)
            
            if X.shape[0] == 0:
                logger.error("❌ No features extracted from training data")
                return
            
            # Split data for training
            X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
            
            # Train Isolation Forest
            logger.info("🌲 Training Isolation Forest...")
            self.isolation_forest = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            self.isolation_forest.fit(X_train)
            
            # Train Autoencoder
            logger.info("🤖 Training Autoencoder...")
            await self._train_autoencoder(X_train)
            
            # Evaluate models
            await self._evaluate_models(X_test)
            
            # Save models
            await self._save_models()
            
            self.is_trained = True
            logger.info("✅ ML models trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Error training models: {e}")
            raise
    
    async def predict_anomaly(self, request_data: Dict[str, Any]) -> float:
        """Predict anomaly score for a request"""
        try:
            if not self.is_trained:
                logger.warning("⚠️ Models not trained, returning default score")
                return 0.5
            
            # Extract features from request
            features = await self._extract_single_features(request_data)
            
            if features is None:
                return 0.0
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Get anomaly scores from both models
            iforest_score = self.isolation_forest.decision_function(features_scaled)[0]
            
            # Convert Isolation Forest score to 0-1 range
            iforest_normalized = 1 / (1 + np.exp(-iforest_score))
            
            # Get autoencoder score
            with torch.no_grad():
                features_tensor = torch.FloatTensor(features_scaled)
                reconstructed = self.autoencoder(features_tensor)
                mse = torch.mean((features_tensor - reconstructed) ** 2).item()
                autoencoder_score = min(mse, 1.0)  # Cap at 1.0
            
            # Combine scores (weighted average)
            combined_score = 0.6 * iforest_normalized + 0.4 * autoencoder_score
            
            return float(combined_score)
            
        except Exception as e:
            logger.error(f"❌ Error predicting anomaly: {e}")
            return 0.0
    
    async def classify_attack_type(self, request_data: Dict[str, Any]) -> Tuple[str, float]:
        """Classify the type of attack"""
        try:
            # Simple rule-based classification (can be enhanced with ML)
            url = request_data.get("url", "").lower()
            user_agent = request_data.get("user_agent", "").lower()
            
            # SQL Injection
            if any(pattern in url for pattern in ["union", "select", "insert", "delete", "update", "drop"]):
                return "sql_injection", 0.9
            
            # XSS
            elif any(pattern in url for pattern in ["<script>", "javascript:", "onerror=", "onload="]):
                return "xss", 0.8
            
            # Directory Traversal
            elif any(pattern in url for pattern in ["../", "..\\", "/etc/passwd", "/windows/system32"]):
                return "directory_traversal", 0.9
            
            # Automated Tools
            elif any(pattern in user_agent for pattern in ["sqlmap", "nikto", "nmap", "burp", "zap"]):
                return "automated_tool", 0.7
            
            # Brute Force (would need session tracking)
            elif "login" in url or "auth" in url:
                return "brute_force", 0.6
            
            # Normal request
            else:
                return "normal", 0.1
                
        except Exception as e:
            logger.error(f"❌ Error classifying attack type: {e}")
            return "unknown", 0.0
    
    async def _get_training_data(self) -> List[Dict[str, Any]]:
        """Get training data from database"""
        try:
            db = SessionLocal()
            try:
                # Get recent attack events
                events = db.query(AttackEvent).filter(
                    AttackEvent.timestamp >= datetime.utcnow() - timedelta(days=30)
                ).limit(10000).all()
                
                training_data = []
                for event in events:
                    training_data.append({
                        "url": event.url or "",
                        "user_agent": event.user_agent or "",
                        "method": event.method or "",
                        "headers": event.headers or {},
                        "query_params": event.query_params or {},
                        "attack_type": event.attack_type or "normal",
                        "is_anomaly": event.is_anomaly or False,
                        "anomaly_score": event.anomaly_score or 0.0
                    })
                
                logger.info(f"📊 Retrieved {len(training_data)} training samples")
                return training_data
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error getting training data: {e}")
            return []
    
    async def _generate_synthetic_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate synthetic training data"""
        logger.info(f"🎭 Generating {count} synthetic training samples...")
        
        synthetic_data = []
        
        # Normal requests
        normal_count = int(count * 0.8)
        for i in range(normal_count):
            synthetic_data.append({
                "url": f"/api/v1/users/{i}",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "method": "GET",
                "headers": {"content-type": "application/json"},
                "query_params": {},
                "attack_type": "normal",
                "is_anomaly": False,
                "anomaly_score": np.random.uniform(0.0, 0.3)
            })
        
        # Attack requests
        attack_count = int(count * 0.2)
        attack_types = ["sql_injection", "xss", "directory_traversal", "automated_tool"]
        
        for i in range(attack_count):
            attack_type = np.random.choice(attack_types)
            
            if attack_type == "sql_injection":
                url = f"/api/users?id=1 UNION SELECT * FROM users WHERE 1=1--"
            elif attack_type == "xss":
                url = f"/api/search?q=<script>alert('xss')</script>"
            elif attack_type == "directory_traversal":
                url = f"/api/files/../../../etc/passwd"
            else:  # automated_tool
                url = f"/api/admin/config"
            
            synthetic_data.append({
                "url": url,
                "user_agent": "sqlmap/1.0" if attack_type == "sql_injection" else "Mozilla/5.0",
                "method": "GET",
                "headers": {"content-type": "application/json"},
                "query_params": {},
                "attack_type": attack_type,
                "is_anomaly": True,
                "anomaly_score": np.random.uniform(0.6, 1.0)
            })
        
        return synthetic_data
    
    async def _extract_features(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features from training data"""
        features_list = []
        
        for item in data:
            features = await self._extract_single_features(item)
            if features is not None:
                features_list.append(features)
        
        if not features_list:
            return np.array([])
        
        # Store feature columns for later use
        self.feature_columns = list(range(len(features_list[0])))
        
        return np.array(features_list)
    
    async def _extract_single_features(self, data: Dict[str, Any]) -> Optional[List[float]]:
        """Extract features from a single request"""
        try:
            features = []
            url = data.get("url", "").lower()
            user_agent = data.get("user_agent", "").lower()
            method = data.get("method", "").upper()
            headers = data.get("headers", {})
            
            # URL-based features
            url_length = len(url)
            features.append(min(url_length / 1000, 1.0))  # Normalized URL length
            
            # Count suspicious patterns in URL
            suspicious_patterns = sum(1 for pattern in self.url_patterns if pattern in url)
            features.append(min(suspicious_patterns / 10, 1.0))  # Normalized pattern count
            
            # Query parameter count
            query_count = len(data.get("query_params", {}))
            features.append(min(query_count / 20, 1.0))  # Normalized query count
            
            # User agent features
            ua_length = len(user_agent)
            features.append(min(ua_length / 500, 1.0))  # Normalized UA length
            
            # Suspicious user agent patterns
            ua_suspicious = sum(1 for pattern in self.user_agent_patterns if pattern in user_agent)
            features.append(min(ua_suspicious / 5, 1.0))  # Normalized UA suspiciousness
            
            # Method encoding
            method_encoding = {"GET": 0, "POST": 1, "PUT": 2, "DELETE": 3, "HEAD": 4, "OPTIONS": 5}.get(method, 6)
            features.append(method_encoding / 6)  # Normalized method
            
            # Header count
            header_count = len(headers)
            features.append(min(header_count / 50, 1.0))  # Normalized header count
            
            # Content type features
            content_type = headers.get("content-type", "").lower()
            has_json = "json" in content_type
            has_form = "form" in content_type
            features.extend([float(has_json), float(has_form)])
            
            # Special headers
            has_auth = "authorization" in headers
            has_xff = "x-forwarded-for" in headers
            features.extend([float(has_auth), float(has_xff)])
            
            # URL structure features
            has_params = "?" in url
            has_fragment = "#" in url
            has_path_traversal = "../" in url or "..\\" in url
            features.extend([float(has_params), float(has_fragment), float(has_path_traversal)])
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting features: {e}")
            return None
    
    async def _train_autoencoder(self, X_train: np.ndarray):
        """Train the autoencoder model"""
        try:
            input_dim = X_train.shape[1]
            hidden_dim = min(32, input_dim // 2)
            
            self.autoencoder = Autoencoder(input_dim, hidden_dim)
            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.autoencoder.parameters(), lr=0.001)
            
            # Convert to tensors
            X_tensor = torch.FloatTensor(X_train)
            dataset = TensorDataset(X_tensor)
            dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
            
            # Training loop
            epochs = 50
            for epoch in range(epochs):
                total_loss = 0
                for batch in dataloader:
                    optimizer.zero_grad()
                    reconstructed = self.autoencoder(batch[0])
                    loss = criterion(reconstructed, batch[0])
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()
                
                if epoch % 10 == 0:
                    logger.info(f"Autoencoder epoch {epoch}, loss: {total_loss/len(dataloader):.4f}")
            
            logger.info("✅ Autoencoder training completed")
            
        except Exception as e:
            logger.error(f"❌ Error training autoencoder: {e}")
            raise
    
    async def _evaluate_models(self, X_test: np.ndarray):
        """Evaluate model performance"""
        try:
            # Isolation Forest evaluation
            iforest_predictions = self.isolation_forest.predict(X_test)
            iforest_scores = self.isolation_forest.decision_function(X_test)
            
            # Autoencoder evaluation
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X_test)
                reconstructed = self.autoencoder(X_tensor)
                mse_scores = torch.mean((X_tensor - reconstructed) ** 2, dim=1).numpy()
            
            logger.info(f"📊 Model evaluation completed:")
            logger.info(f"   Isolation Forest: {np.sum(iforest_predictions == -1)} anomalies detected")
            logger.info(f"   Autoencoder: Mean MSE = {np.mean(mse_scores):.4f}")
            
        except Exception as e:
            logger.error(f"❌ Error evaluating models: {e}")
    
    async def _save_models(self):
        """Save trained models to disk"""
        try:
            # Save Isolation Forest
            with open(self.model_path / "isolation_forest.pkl", "wb") as f:
                pickle.dump(self.isolation_forest, f)
            
            # Save Autoencoder
            torch.save(self.autoencoder, self.model_path / "autoencoder.pth")
            
            # Save Scaler
            with open(self.model_path / "scaler.pkl", "wb") as f:
                pickle.dump(self.scaler, f)
            
            # Save feature configuration
            config = {
                "feature_columns": self.feature_columns,
                "label_encoders": self.label_encoders
            }
            with open(self.model_path / "feature_config.json", "w") as f:
                json.dump(config, f)
            
            # Fit scaler with training data
            self.scaler.fit(np.array([[0] * len(self.feature_columns)]))
            
            logger.info("💾 Models saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Error saving models: {e}")
    
    async def close(self):
        """Close the ML service"""
        logger.info("🛑 Closing ML anomaly detector...")
        # Cleanup resources if needed
        self.isolation_forest = None
        self.autoencoder = None
