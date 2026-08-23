import os
import re
import math
import shutil
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gate_1000_questions.csv")
BACKUP_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gate_1000_questions_raw_backup.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "gate_nlp_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

ENGINEERING_TERMS = {
    'eigenvalue', 'eigenvector', 'determinant', 'jacobian', 'gradient', 'divergence', 'curl',
    'mohr-coulomb', 'rmr', 'bieniwaski', 'barton', 'tributary', 'unconfined', 'poisson',
    'young', 'viscosity', 'reynolds', 'navier-stokes', 'atkinson', 'equivalent', 'orifice',
    'kriging', 'semivariogram', 'nugget', 'sill', 'variance', 'koepe', 'catenary', 'powder',
    'subsidence', 'stope', 'depillaring', 'anisotropy', 'deviatoric', 'piezometric'
}

UNITS_PATTERN = re.compile(
    r'\b(m\/s|m3\/s|m³\/s|pa|kpa|mpa|gpa|n\/m2|n\/m²|kn|mn|ns2\/m8|ns²\/m⁸|kg\/m3|kg\/m³|rpm|kw|mw|rad\/s|tonne|tonnes|deg|°)\b',
    re.IGNORECASE
)

class AdvancedGATEComplexityExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def _count_syllables(self, word):
        word = word.lower()
        if len(word) <= 3:
            return 1
        count = len(re.findall(r'[aeiouy]+', word))
        if word.endswith('e') and not word.endswith('le') and count > 1:
            count -= 1
        return max(1, count)

    def transform(self, X):
        features = []
        for text in X:
            t = str(text)
            words = re.findall(r'\b[a-zA-Z]+\b', t)
            sentences = [s for s in re.split(r'[.!?]+', t) if s.strip()]
            
            char_count = len(t)
            word_count = max(1, len(words))
            sentence_count = max(1, len(sentences))
            
            avg_word_length = char_count / word_count
            avg_sentence_length = word_count / sentence_count
            
            syllable_count = sum(self._count_syllables(w) for w in words)
            complex_words = sum(1 for w in words if self._count_syllables(w) >= 3)
            pct_complex_words = (complex_words / word_count) * 100.0
            
            gunning_fog = 0.4 * (avg_sentence_length + pct_complex_words)
            flesch_kincaid = 0.39 * avg_sentence_length + 11.8 * (syllable_count / word_count) - 15.59
            
            math_operators = len(re.findall(r'[=+\-*/^√%∫λσωΔθμσπ∂∑∏≤≥≠≈∞]', t))
            num_quantities = len(re.findall(r'\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b', t))
            num_units = len(UNITS_PATTERN.findall(t))
            
            domain_term_density = sum(1 for w in words if w.lower() in ENGINEERING_TERMS)
            
            word_freqs = {}
            for w in words:
                w_lower = w.lower()
                word_freqs[w_lower] = word_freqs.get(w_lower, 0) + 1
            entropy = -sum((c / word_count) * math.log2(c / word_count) for c in word_freqs.values())
            
            features.append([
                char_count,
                word_count,
                avg_word_length,
                avg_sentence_length,
                pct_complex_words,
                gunning_fog,
                flesch_kincaid,
                math_operators,
                num_quantities,
                num_units,
                domain_term_density,
                entropy
            ])
        return np.array(features)

def run_advanced_nlp_classification():
    if not os.path.exists(CSV_PATH):
        print(f"File not found: {CSV_PATH}")
        return

    shutil.copyfile(CSV_PATH, BACKUP_PATH)
    print(f"Safety backup created at: {BACKUP_PATH}")

    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} questions for feature extraction and training.")

    for col in ['question', 'option_a', 'option_b', 'option_c', 'option_d']:
        df[col] = df[col].fillna('')

    df['stem_corpus'] = df['question']
    df['full_corpus'] = (
        df['question'] + " " +
        df['option_a'] + " " +
        df['option_b'] + " " +
        df['option_c'] + " " +
        df['option_d']
    )

    feature_union = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=3000,
            sublinear_tf=True,
            stop_words='english'
        )),
        ("char_tfidf", TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(3, 5),
            max_features=2000,
            sublinear_tf=True
        )),
        ("readability_and_math", AdvancedGATEComplexityExtractor())
    ])

    X_raw = feature_union.fit_transform(df['full_corpus'])
    scaler = RobustScaler(with_centering=False)
    X = scaler.fit_transform(X_raw)

    y = df['difficulty'].values.astype(float)

    regressor = GradientBoostingRegressor(
        n_estimators=180,
        learning_rate=0.04,
        max_depth=4,
        subsample=0.85,
        random_state=42
    )
    regressor.fit(X, y)
    print("Ensemble Gradient Boosting regressor fitted successfully.")

    continuous_predictions = regressor.predict(X)
    df['predicted_score'] = continuous_predictions

    df['difficulty'] = pd.qcut(
        df['predicted_score'].rank(method='first'),
        q=15,
        labels=range(1, 16)
    ).astype(int)

    pipeline_payload = {
        "feature_union": feature_union,
        "scaler": scaler,
        "regressor": regressor
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline_payload, f)
    print(f"Saved serialization bundle to '{MODEL_PATH}'.")

    df = df.sort_values(by=['difficulty', 'subject']).reset_index(drop=True)
    df['id'] = range(1, len(df) + 1)

    output_cols = ["id", "subject", "topic", "difficulty", "question", "option_a", "option_b", "option_c", "option_d", "correct"]
    df = df[[c for c in output_cols if c in df.columns]]
    df.to_csv(CSV_PATH, index=False)

    print(f"Successfully balanced and updated '{CSV_PATH}'.")
    print("\nQuestion Distribution Per Tier (1-15):")
    print(df['difficulty'].value_counts().sort_index())

if __name__ == "__main__":
    run_advanced_nlp_classification()