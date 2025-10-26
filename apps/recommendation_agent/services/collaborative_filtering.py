import numpy as np
import pickle
import pandas as pd
from pathlib import Path
import logging
import tempfile
import os
import warnings

# Suppress specific warnings from RecBole/PyTorch dependencies
warnings.filterwarnings('ignore', category=UserWarning, module='triton')
warnings.filterwarnings('ignore', category=DeprecationWarning, message='.*SwigPy.*')
warnings.filterwarnings('ignore', category=DeprecationWarning, message='.*swigvarlink.*')

from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.model.general_recommender import BPR
from recbole.trainer import Trainer
from recbole.utils import init_seed, init_logger
from django.core.cache import cache
from typing import Dict, Optional

from ..models import JobFeedback

logger = logging.getLogger(__name__)

# Model storage path
MODEL_DIR = Path(__file__).parent.parent / "trained_models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / "recbole_model.pth"
MAPPINGS_PATH = MODEL_DIR / "recbole_mappings.pkl"
DATA_DIR = MODEL_DIR / "recbole_data"
DATA_DIR.mkdir(exist_ok=True)


class CollaborativeFilteringService:
    """
    RecBole-based Collaborative Filtering for Job Recommendations

    Uses RecBole framework with BPR (Bayesian Personalized Ranking):
    - Easy to install (no C++ compiler needed)
    - Supports 70+ recommendation algorithms
    - Built-in evaluation metrics
    - Production-ready framework

    Workflow:
    1. Train model on user-job interactions (likes, saves, applies)
    2. Generate user and job embeddings
    3. Use embeddings to predict job relevance for users
    4. Cache embeddings in Redis for fast lookup
    """

    def __init__(self):
        self.model = None
        self.config = None
        self.dataset = None
        self.user_id_map: Dict[int, int] = {}  # Django user_id -> RecBole internal id
        self.job_id_map: Dict[int, int] = {}   # Django job_id -> RecBole internal id
        self.reverse_user_map: Dict[int, int] = {}  # RecBole id -> Django user_id
        self.reverse_job_map: Dict[int, int] = {}   # RecBole id -> Django job_id

    def prepare_recbole_data(self) -> str:
        """
        Prepare data in RecBole format (.inter file)

        Format: user_id:token item_id:token rating:float

        Returns:
            dataset_name: Name of the dataset
        """
        # Get all feedback data (exclude dislikes for implicit feedback)
        feedbacks = JobFeedback.objects.using('postgres').select_related(
            'candidate', 'job'
        ).exclude(feedback_type='dislike').all()

        if not feedbacks.exists():
            raise ValueError("No feedback data available. Please collect user interactions first.")

        # Score mapping (implicit feedback - higher is better)
        score_map = {
            'apply': 5.0,
            'save': 3.0,
            'like': 1.0,
        }

        # Prepare data
        data = []
        for fb in feedbacks:
            score = score_map.get(fb.feedback_type, fb.score)
            data.append({
                'user_id': str(fb.candidate.candidate_id),
                'item_id': str(fb.job.id),
                'rating': score,
                'timestamp': int(fb.created_at.timestamp()) if fb.created_at else 0
            })

        # Create DataFrame
        df = pd.DataFrame(data)

        # Validate sufficient data for collaborative filtering
        unique_users = df['user_id'].unique()
        unique_items = df['item_id'].unique()

        if len(unique_users) < 2:
            raise ValueError(
                f"Collaborative filtering requires at least 2 users, but only {len(unique_users)} user(s) found. "
                f"Please add more candidates and their job interactions before training the model."
            )

        if len(unique_items) < 2:
            raise ValueError(
                f"Collaborative filtering requires at least 2 jobs, but only {len(unique_items)} job(s) found. "
                f"Please add more job postings and interactions before training the model."
            )

        if len(df) < 10:
            logger.warning(
                f"Only {len(df)} interactions found. Collaborative filtering works best with more data. "
                f"Recommendations may not be accurate with limited training data."
            )

        self.user_id_map = {int(uid): idx for idx, uid in enumerate(unique_users)}
        self.job_id_map = {int(iid): idx for idx, iid in enumerate(unique_items)}
        self.reverse_user_map = {idx: int(uid) for uid, idx in self.user_id_map.items()}
        self.reverse_job_map = {idx: int(iid) for iid, idx in self.job_id_map.items()}

        # Save to .inter file (RecBole format)
        dataset_name = 'job_rec'
        inter_file = DATA_DIR / f"{dataset_name}.inter"

        # Write with RecBole format
        with open(inter_file, 'w') as f:
            # Header
            f.write("user_id:token\titem_id:token\trating:float\ttimestamp:float\n")
            # Data
            for _, row in df.iterrows():
                f.write(f"{row['user_id']}\t{row['item_id']}\t{row['rating']}\t{row['timestamp']}\n")

        logger.info(f"Prepared RecBole data: {len(df)} interactions")
        logger.info(f"Users: {len(unique_users)}, Jobs: {len(unique_items)}")

        return dataset_name

    def train_model(
        self,
        embedding_size: int = 64,
        learning_rate: float = 0.001,
        epochs: int = 30,
        model_type: str = 'BPR'
    ) -> Dict:
        """
        Train RecBole model on user-job interactions

        Args:
            embedding_size: Embedding dimension (default 64)
            learning_rate: Learning rate (default 0.001)
            epochs: Number of training epochs (default 30)
            model_type: Model type ('BPR' recommended for implicit feedback)

        Returns:
            Training statistics
        """
        logger.info(f"Starting RecBole {model_type} training...")

        # Prepare data
        dataset_name = self.prepare_recbole_data()

        # RecBole configuration
        config_dict = {
            'data_path': str(DATA_DIR),
            'dataset': dataset_name,
            'USER_ID_FIELD': 'user_id',
            'ITEM_ID_FIELD': 'item_id',
            'RATING_FIELD': 'rating',
            'TIME_FIELD': 'timestamp',
            'load_col': {
                'inter': ['user_id', 'item_id', 'rating', 'timestamp']
            },
            'user_inter_num_interval': "[0,inf)",
            'item_inter_num_interval': "[0,inf)",

            # Model parameters
            'embedding_size': embedding_size,
            'learning_rate': learning_rate,
            'epochs': epochs,
            'train_batch_size': 2048,
            'eval_batch_size': 4096,

            # Training settings
            'neg_sampling': None,  # BPR handles this internally
            'eval_args': {
                'split': {'RS': [0.8, 0.1, 0.1]},
                'mode': 'full',
            },
            'metrics': ['Recall', 'NDCG'],
            'topk': [10, 20],
            'valid_metric': 'NDCG@10',

            # Other settings
            'gpu_id': None,  # CPU only (set to 0 for GPU)
            'checkpoint_dir': str(MODEL_DIR),
            'show_progress': True,
        }

        # Initialize seed for reproducibility
        init_seed(42, reproducibility=True)

        # Create config
        self.config = Config(model=model_type, config_dict=config_dict)

        # Create dataset
        self.dataset = create_dataset(self.config)

        # Data preparation
        train_data, valid_data, test_data = data_preparation(self.config, self.dataset)

        # Initialize model
        if model_type.upper() == 'BPR':
            from recbole.model.general_recommender import BPR
            self.model = BPR(self.config, train_data.dataset).to(self.config['device'])
        else:
            # You can add more models here (NeuMF, LightGCN, etc.)
            raise ValueError(f"Model type {model_type} not supported yet. Use 'BPR'.")

        # Initialize trainer
        trainer = Trainer(self.config, self.model)

        # Train model
        logger.info("Training model...")
        best_valid_score, best_valid_result = trainer.fit(
            train_data, valid_data, show_progress=True
        )

        # Test model
        test_result = trainer.evaluate(test_data, show_progress=True)

        # Save model and mappings
        self.save_model()

        # Clear cached embeddings
        try:
            cache.delete_pattern("cf_user_*")
            cache.delete_pattern("cf_job_*")
        except AttributeError:
            for uid in self.user_id_map.keys():
                cache.delete(f"cf_user_{uid}")
            for jid in self.job_id_map.keys():
                cache.delete(f"cf_job_{jid}")

        logger.info("Training completed and model saved!")

        return {
            "num_users": len(self.user_id_map),
            "num_jobs": len(self.job_id_map),
            "num_interactions": len(train_data.dataset),
            "embedding_size": embedding_size,
            "epochs": epochs,
            "model_type": model_type,
            "learning_rate": learning_rate,
            "best_valid_score": float(best_valid_score),
            "test_results": {k: float(v) for k, v in test_result.items()}
        }

    def save_model(self):
        """Save trained model and mappings to disk"""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")

        # Save model state dict
        import torch
        torch.save(self.model.state_dict(), MODEL_PATH)

        # Save mappings and config
        mappings = {
            'user_id_map': self.user_id_map,
            'job_id_map': self.job_id_map,
            'reverse_user_map': self.reverse_user_map,
            'reverse_job_map': self.reverse_job_map,
            'config_dict': self.config.final_config_dict if self.config else None
        }
        with open(MAPPINGS_PATH, 'wb') as f:
            pickle.dump(mappings, f)

        logger.info(f"Model saved to {MODEL_PATH}")

    def load_model(self) -> bool:
        """Load trained model and mappings from disk"""
        if not MODEL_PATH.exists() or not MAPPINGS_PATH.exists():
            logger.debug("No trained model found. Please train the model first.")
            return False

        # Load mappings
        with open(MAPPINGS_PATH, 'rb') as f:
            mappings = pickle.load(f)
            self.user_id_map = mappings['user_id_map']
            self.job_id_map = mappings['job_id_map']
            self.reverse_user_map = mappings['reverse_user_map']
            self.reverse_job_map = mappings['reverse_job_map']
            config_dict = mappings.get('config_dict')

        if config_dict:
            # Recreate config
            self.config = Config(model='BPR', config_dict=config_dict)

            # Recreate dataset (needed for model initialization)
            dataset_name = self.prepare_recbole_data()
            self.dataset = create_dataset(self.config)

            # Initialize model
            from recbole.model.general_recommender import BPR
            self.model = BPR(self.config, self.dataset).to(self.config['device'])

            # Load model weights
            import torch
            self.model.load_state_dict(torch.load(MODEL_PATH, map_location=self.config['device']))
            self.model.eval()

        logger.info(f"Model loaded: {len(self.user_id_map)} users, {len(self.job_id_map)} jobs")
        return True

    def get_user_embedding(self, candidate_id: int) -> Optional[np.ndarray]:
        """
        Get user embedding vector from trained model

        Args:
            candidate_id: Django candidate ID

        Returns:
            User embedding vector or None if user not in training set
        """
        # Check cache first
        cache_key = f"cf_user_{candidate_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return np.array(cached)

        # Load model if not loaded
        if self.model is None:
            if not self.load_model():
                return None

        # Get internal user ID
        if candidate_id not in self.user_id_map:
            logger.warning(f"User {candidate_id} not in training set (cold start)")
            return None

        # Get user embedding from model
        import torch
        user_token = str(candidate_id)

        try:
            # Get user embedding
            with torch.no_grad():
                user_e = self.model.user_embedding.weight[
                    self.dataset.token2id(self.dataset.uid_field, user_token)
                ]
                embedding = user_e.cpu().numpy()
        except:
            logger.warning(f"Failed to get embedding for user {candidate_id}")
            return None

        # Cache for 1 hour
        cache.set(cache_key, embedding.tolist(), timeout=3600)

        return embedding

    def get_job_embedding(self, job_id: int) -> Optional[np.ndarray]:
        """
        Get job embedding vector from trained model

        Args:
            job_id: Django job ID

        Returns:
            Job embedding vector or None if job not in training set
        """
        # Check cache first
        cache_key = f"cf_job_{job_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return np.array(cached)

        # Load model if not loaded
        if self.model is None:
            if not self.load_model():
                return None

        # Get internal job ID
        if job_id not in self.job_id_map:
            logger.warning(f"Job {job_id} not in training set")
            return None

        # Get job embedding from model
        import torch
        item_token = str(job_id)

        try:
            # Get item embedding
            with torch.no_grad():
                item_e = self.model.item_embedding.weight[
                    self.dataset.token2id(self.dataset.iid_field, item_token)
                ]
                embedding = item_e.cpu().numpy()
        except:
            logger.warning(f"Failed to get embedding for job {job_id}")
            return None

        # Cache for 1 hour
        cache.set(cache_key, embedding.tolist(), timeout=3600)

        return embedding

    def predict_for_user(self, candidate_id: int, top_k: int = 10) -> list:
        """
        Get top-k job recommendations for a user using pure CF

        Args:
            candidate_id: Django candidate ID
            top_k: Number of recommendations

        Returns:
            List of (job_id, score) tuples
        """
        # Load model if needed
        if self.model is None:
            if not self.load_model():
                return []

        # Check if user exists
        if candidate_id not in self.user_id_map:
            logger.warning(f"User {candidate_id} not in training set")
            return []

        import torch

        try:
            # Get user token
            user_token = str(candidate_id)
            user_id = self.dataset.token2id(self.dataset.uid_field, user_token)

            # Get all item IDs
            all_item_ids = list(range(self.dataset.item_num))

            # Predict scores for all items
            with torch.no_grad():
                user_tensor = torch.LongTensor([user_id] * len(all_item_ids)).to(self.config['device'])
                item_tensor = torch.LongTensor(all_item_ids).to(self.config['device'])

                scores = self.model.predict(user_tensor, item_tensor)
                scores = scores.cpu().numpy()

            # Get top-k
            top_indices = np.argsort(-scores)[:top_k]

            # Convert to Django job IDs
            results = []
            for idx in top_indices:
                item_token = self.dataset.id2token(self.dataset.iid_field, int(all_item_ids[idx]))
                job_id = int(item_token)

                # Only include jobs that are in our mapping
                if job_id in self.reverse_job_map.values():
                    results.append((job_id, float(scores[idx])))

            return results[:top_k]

        except Exception as e:
            logger.error(f"Error predicting for user {candidate_id}: {e}")
            return []

    def get_model_stats(self) -> Dict:
        """Get statistics about the trained model"""
        if self.model is None:
            if not self.load_model():
                return {"error": "No trained model available"}

        # Get interaction counts
        feedbacks = JobFeedback.objects.using('postgres')
        total_interactions = feedbacks.count()

        feedback_counts = {}
        for fb_type in ['like', 'dislike', 'save', 'apply']:
            feedback_counts[fb_type] = feedbacks.filter(feedback_type=fb_type).count()

        return {
            "num_users": len(self.user_id_map),
            "num_jobs": len(self.job_id_map),
            "total_interactions": total_interactions,
            "feedback_breakdown": feedback_counts,
            "embedding_size": self.config['embedding_size'] if self.config else 64,
            "model_type": "BPR (RecBole)",
            "model_path": str(MODEL_PATH),
            "model_exists": MODEL_PATH.exists()
        }


# Global service instance
cf_service = CollaborativeFilteringService()
