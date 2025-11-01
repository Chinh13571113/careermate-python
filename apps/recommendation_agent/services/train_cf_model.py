# apps/recommendations/services/train_cf_model.py
import pandas as pd
import joblib
import os
import django
import sys
from surprise import SVD, Dataset, Reader
from sqlalchemy import create_engine

# Setup Django if running standalone
django_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(django_base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

from django.conf import settings

MODEL_PATH = "cf_model.pkl"

def get_sqlalchemy_engine():
    """Create SQLAlchemy engine from Django database settings"""
    db_settings = settings.DATABASES['default']
    engine = db_settings.get('ENGINE', '')

    if 'postgresql' in engine:
        db_url = f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings.get('PORT', 5432)}/{db_settings['NAME']}"
    elif 'mysql' in engine:
        db_url = f"mysql+pymysql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings.get('PORT', 3306)}/{db_settings['NAME']}"
    else:
        # SQLite or other
        db_url = f"sqlite:///{db_settings['NAME']}"

    return create_engine(db_url)

def train_cf_model():
    """Train collaborative filtering model từ bảng job_feedback"""
    query = "SELECT candidate_id, job_id, score FROM job_feedback;"
    engine = get_sqlalchemy_engine()

    try:
        df = pd.read_sql(query, engine)

        if df.empty:
            print("⚠️ No feedback data found in database.")
            return None

        if len(df["candidate_id"].unique()) < 2:
            print(f"⚠️ Not enough unique candidates ({len(df['candidate_id'].unique())}). Need at least 2.")
            return None

        print(f"📊 Training data: {len(df)} feedback records")
        print(f"👥 Unique candidates: {len(df['candidate_id'].unique())}")
        print(f"💼 Unique jobs: {len(df['job_id'].unique())}")

        reader = Reader(rating_scale=(0, 1))
        data = Dataset.load_from_df(df[["candidate_id", "job_id", "score"]], reader)
        trainset = data.build_full_trainset()

        print("\n🤖 Training SVD model...")
        model = SVD(n_factors=10, lr_all=0.005, reg_all=0.02)  # Reduced n_factors for small dataset
        model.fit(trainset)

        joblib.dump(model, MODEL_PATH)
        print(f"✅ CF model retrained and saved to {MODEL_PATH}")
        return model
    except Exception as e:
        print(f"❌ Error training model: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("🚀 Training Collaborative Filtering Model...")
    print("=" * 80)
    model = train_cf_model()
    if model:
        print("\n✅ Model training completed successfully!")
        print(f"📁 Model saved to: {os.path.abspath(MODEL_PATH)}")
    else:
        print("\n❌ Model training failed - insufficient data or error occurred.")
