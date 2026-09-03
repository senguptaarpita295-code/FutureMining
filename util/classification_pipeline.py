import os
import re
import math
import joblib
import numpy as np
import pandas as pd

from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


INPUT_FILE = "GATE_800_Questions_Raw.csv"
OUTPUT_FILE = "GATE_800_Questions_Difficulty_1_15.csv"
MODEL_FILE = "gate_difficulty_model.pkl"


df = pd.read_csv(INPUT_FILE)

df["_original_order"] = np.arange(len(df))

df["_original_difficulty"] = pd.to_numeric(
    df["difficulty"],
    errors="coerce"
)


text_columns = [
    "subject",
    "topic",
    "question",
    "option_a",
    "option_b",
    "option_c",
    "option_d"
]

for column in text_columns:
    if column in df.columns:
        df[column] = df[column].fillna("").astype(str)


df["stem_text"] = (
    df["subject"] + " " +
    df["topic"] + " " +
    df["question"]
)

df["full_text"] = (
    df["subject"] + " " +
    df["topic"] + " " +
    df["question"] + " " +
    df["option_a"] + " " +
    df["option_b"] + " " +
    df["option_c"] + " " +
    df["option_d"]
)


def count_syllables(text):
    words = re.findall(
        r"[A-Za-z]+",
        text.lower()
    )

    total = 0

    for word in words:
        word = re.sub(
            r"[^a-z]",
            "",
            word
        )

        if not word:
            continue

        vowels = re.findall(
            r"[aeiouy]+",
            word
        )

        count = len(vowels)

        if word.endswith("e") and count > 1:
            count -= 1

        if count == 0:
            count = 1

        total += count

    return total


mining_engineering_terms = [
    "mining",
    "mine",
    "mineral",
    "minerals",
    "ore",
    "ores",
    "gangue",
    "deposit",
    "orebody",
    "ore body",
    "seam",
    "coal",
    "lignite",
    "overburden",
    "waste rock",
    "waste",
    "stripping",
    "stripping ratio",
    "bench",
    "benches",
    "pit",
    "open pit",
    "open cast",
    "opencast",
    "underground mining",
    "surface mining",
    "room and pillar",
    "longwall",
    "bord and pillar",
    "stope",
    "stoping",
    "sublevel",
    "cut and fill",
    "shrinkage stoping",
    "block caving",
    "sublevel caving",
    "caving",
    "shaft",
    "sinking",
    "winze",
    "raise",
    "decline",
    "adit",
    "drift",
    "tunnel",
    "gallery",
    "crosscut",
    "level",
    "mine development",
    "mine planning",
    "mine design",
    "mine surveying",
    "surveying",
    "drilling",
    "blast hole",
    "blast holes",
    "blasting",
    "explosive",
    "explosives",
    "detonator",
    "stemming",
    "burden",
    "spacing",
    "powder factor",
    "fragmentation",
    "rock fragmentation",
    "rock breakage",
    "excavation",
    "excavator",
    "dumper",
    "haulage",
    "conveyor",
    "belt conveyor",
    "mine haulage",
    "material handling",
    "mucking",
    "loading",
    "transportation",
    "ore handling",
    "coal handling",
    "beneficiation",
    "mineral processing",
    "ore dressing",
    "ore concentration",
    "concentration",
    "crushing",
    "crusher",
    "grinding",
    "mill",
    "milling",
    "screening",
    "sieving",
    "classification",
    "hydrocyclone",
    "cyclone",
    "flotation",
    "froth flotation",
    "gravity separation",
    "magnetic separation",
    "electrostatic separation",
    "dense medium separation",
    "jig",
    "jigging",
    "spiral",
    "thickener",
    "filter",
    "tailings",
    "slurry",
    "recovery",
    "grade",
    "cut-off grade",
    "cutoff grade",
    "ore grade",
    "liberation",
    "liberation size",
    "rock mechanics",
    "rock mass",
    "rock strength",
    "rock quality",
    "rock quality designation",
    "rqd",
    "uniaxial compressive strength",
    "ucs",
    "compressive strength",
    "tensile strength",
    "shear strength",
    "cohesion",
    "friction angle",
    "angle of friction",
    "young's modulus",
    "poisson's ratio",
    "elastic modulus",
    "stress",
    "strain",
    "deformation",
    "displacement",
    "failure",
    "rock failure",
    "ground control",
    "roof control",
    "roof fall",
    "roof support",
    "support system",
    "rock bolt",
    "rock bolts",
    "roof bolt",
    "roof bolts",
    "shotcrete",
    "steel support",
    "timber support",
    "strata control",
    "strata",
    "roof",
    "floor",
    "hanging wall",
    "footwall",
    "fault",
    "faults",
    "joint",
    "joints",
    "fracture",
    "fractures",
    "discontinuity",
    "discontinuities",
    "dip",
    "strike",
    "inclination",
    "geology",
    "geological",
    "geotechnical",
    "hydrogeology",
    "groundwater",
    "mine water",
    "water inflow",
    "dewatering",
    "drainage",
    "pumping",
    "mine ventilation",
    "ventilation",
    "airflow",
    "air quantity",
    "air velocity",
    "ventilation pressure",
    "pressure drop",
    "fan",
    "auxiliary fan",
    "main fan",
    "ventilation network",
    "methane",
    "gas",
    "mine gases",
    "gas monitoring",
    "gas detection",
    "dust",
    "coal dust",
    "respirable dust",
    "dust suppression",
    "mine safety",
    "mining safety",
    "mine accident",
    "mine rescue",
    "fire",
    "mine fire",
    "spontaneous heating",
    "spontaneous combustion",
    "explosion",
    "coal dust explosion",
    "methane explosion",
    "hazard",
    "risk",
    "safety factor",
    "subsidence",
    "land subsidence",
    "environmental impact",
    "mine environment",
    "mine closure",
    "reclamation",
    "land reclamation",
    "environmental management",
    "coal mining",
    "metal mining",
    "underground mine",
    "surface mine",
    "opencast mine",
    "mineral economics",
    "reserve",
    "resources",
    "mineral reserve",
    "mineral resource",
    "prospecting",
    "exploration",
    "mineral exploration",
    "sampling",
    "drill core",
    "core drilling",
    "borehole",
    "boreholes",
    "logging",
    "core recovery",
    "ore reserve",
    "reserve estimation",
    "resource estimation",
    "geostatistics",
    "variogram",
    "kriging",
    "mine economics",
    "royalty",
    "mineral royalty",
    "production",
    "mine production",
    "productivity",
    "mine capacity"
]


engineering_pattern = (
    r"(?<!\w)(?:"
    + "|".join(
        re.escape(term)
        for term in sorted(
            mining_engineering_terms,
            key=len,
            reverse=True
        )
    )
    + r")(?!\w)"
)


def calculate_complexity(text):
    text = str(text)

    characters = len(text)

    words = re.findall(
        r"\b[\w]+\b",
        text
    )

    word_count = len(words)

    sentences = re.split(
        r"[.!?]+",
        text
    )

    sentence_count = max(
        1,
        len([
            s for s in sentences
            if s.strip()
        ])
    )

    avg_word_length = (
        np.mean([
            len(word)
            for word in words
        ])
        if words
        else 0
    )

    avg_sentence_length = (
        word_count /
        sentence_count
    )

    syllables = count_syllables(
        text
    )

    words_per_sentence = (
        word_count /
        sentence_count
    )

    syllables_per_word = (
        syllables /
        word_count
        if word_count
        else 0
    )

    gunning_fog = (
        0.4 * (
            words_per_sentence +
            100 * (
                syllables_per_word - 1
            )
        )
    )

    flesch_kincaid = (
        0.39 *
        words_per_sentence
        +
        11.8 *
        syllables_per_word
        -
        15.59
    )

    math_operators = len(
        re.findall(
            r"[=+\-*/^<>≤≥≈≠∑∫√]",
            text
        )
    )

    numeric_quantities = len(
        re.findall(
            r"\b\d+(?:\.\d+)?\b",
            text
        )
    )

    units = len(
        re.findall(
            r"\b(?:Hz|kHz|MHz|GHz|V|A|W|kW|MW|Ω|ohm|"
            r"m|cm|mm|km|s|ms|μs|ns|kg|g|N|J|Pa|"
            r"MPa|bit|byte|KB|MB|GB|TB)\b",
            text,
            flags=re.IGNORECASE
        )
    )

    engineering_terms = len(
        re.findall(
            engineering_pattern,
            text,
            flags=re.IGNORECASE
        )
    )

    characters_no_spaces = len(
        re.sub(
            r"\s+",
            "",
            text
        )
    )

    if characters_no_spaces > 0:

        entropy_counts = {}

        for char in text.lower():

            if not char.isspace():

                entropy_counts[char] = (
                    entropy_counts.get(
                        char,
                        0
                    ) + 1
                )

        total_chars = sum(
            entropy_counts.values()
        )

        entropy = 0

        if total_chars:

            for count in (
                entropy_counts.values()
            ):

                probability = (
                    count /
                    total_chars
                )

                entropy -= (
                    probability *
                    math.log2(
                        probability
                    )
                )

    else:
        entropy = 0

    return [
        characters,
        word_count,
        avg_word_length,
        avg_sentence_length,
        syllables,
        gunning_fog,
        flesch_kincaid,
        math_operators,
        numeric_quantities,
        units,
        engineering_terms,
        entropy
    ]


complexity_array = np.array([
    calculate_complexity(text)
    for text in df["full_text"]
])


word_vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=1,
    max_features=30000,
    sublinear_tf=True
)


char_vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5),
    min_df=1,
    max_features=30000,
    sublinear_tf=True
)


word_features = (
    word_vectorizer.fit_transform(
        df["stem_text"]
    )
)


char_features = (
    char_vectorizer.fit_transform(
        df["full_text"]
    )
)


scaler = StandardScaler()

complexity_scaled = (
    scaler.fit_transform(
        complexity_array
    )
)


X_all = hstack([
    word_features,
    char_features,
    csr_matrix(complexity_scaled)
]).tocsr()


labeled_mask = (
    df["_original_difficulty"].notna()
)


train_idx = np.where(
    labeled_mask.values
)[0]


X_train = X_all[
    train_idx
]


y_train = df.loc[
    labeled_mask,
    "_original_difficulty"
].astype(float).values


model = Ridge(
    alpha=5.0
)


model.fit(
    X_train,
    y_train
)


model_prediction = model.predict(
    X_all
)


complexity_score = (
      0.08 * np.log1p(
          complexity_array[:, 0]
      )
    + 0.07 * np.log1p(
          complexity_array[:, 1]
      )
    + 0.12 * np.log1p(
          complexity_array[:, 2]
      )
    + 0.10 * np.log1p(
          complexity_array[:, 3]
      )
    + 0.12 * np.log1p(
          complexity_array[:, 4]
      )
    + 0.07 * np.log1p(
          complexity_array[:, 5]
      )
    + 0.08 * np.log1p(
          complexity_array[:, 6]
      )
    + 0.08 * np.log1p(
          complexity_array[:, 7]
      )
    + 0.08 * np.log1p(
          complexity_array[:, 8]
      )
    + 0.18 * np.log1p(
          complexity_array[:, 10]
      )
)


def normalize(values):

    values = np.asarray(
        values,
        dtype=float
    )

    minimum = np.min(values)
    maximum = np.max(values)

    if maximum == minimum:

        return np.zeros(
            len(values)
        )

    return (
        (values - minimum) /
        (maximum - minimum)
    )


model_score = normalize(
    model_prediction
)


complexity_score = normalize(
    complexity_score
)


final_score = (
    0.65 * model_score +
    0.35 * complexity_score
)


old_difficulty = (
    df["_original_difficulty"].values
)


old_normalized = np.zeros(
    len(df)
)


old_normalized[
    labeled_mask.values
] = (
    old_difficulty[
        labeled_mask.values
    ] - 1
) / 2


final_score[
    labeled_mask.values
] = (
    0.55 *
    final_score[
        labeled_mask.values
    ]
    +
    0.45 *
    old_normalized[
        labeled_mask.values
    ]
)


TARGET_DISTRIBUTION = {
    1: 25,
    2: 30,
    3: 40,
    4: 50,
    5: 60,
    6: 70,
    7: 75,
    8: 75,
    9: 75,
    10: 70,
    11: 60,
    12: 55,
    13: 50,
    14: 40,
    15: 25
}


assert sum(
    TARGET_DISTRIBUTION.values()
) == len(df)


ranked_indices = np.argsort(
    final_score,
    kind="mergesort"
)


final_difficulty = np.zeros(
    len(df),
    dtype=int
)


position = 0


for difficulty_level in range(1, 16):

    number_of_questions = (
        TARGET_DISTRIBUTION[
            difficulty_level
        ]
    )

    selected_indices = (
        ranked_indices[
            position:
            position +
            number_of_questions
        ]
    )

    final_difficulty[
        selected_indices
    ] = difficulty_level

    position += number_of_questions


assert position == len(df)

assert final_difficulty.min() == 1

assert final_difficulty.max() == 15


for level in range(1, 16):

    assert (
        np.sum(
            final_difficulty == level
        )
        ==
        TARGET_DISTRIBUTION[level]
    )


df["difficulty"] = (
    final_difficulty
)


df = df.sort_values(
    "_original_order"
)


df = df.drop(
    columns=[
        "_original_order",
        "_original_difficulty",
        "stem_text",
        "full_text"
    ],
    errors="ignore"
)


df.to_csv(
    OUTPUT_FILE,
    index=False
)


joblib.dump(
    {
        "model": model,
        "word_vectorizer":
            word_vectorizer,
        "char_vectorizer":
            char_vectorizer,
        "scaler": scaler,
        "target_distribution":
            TARGET_DISTRIBUTION,
        "mining_engineering_terms":
            mining_engineering_terms
    },
    MODEL_FILE
)


print(
    "\nDifficulty distribution:"
)

print(
    df["difficulty"]
    .value_counts()
    .sort_index()
    .to_string()
)


print(
    "\nTotal questions:",
    len(df)
)


print(
    "\nAlready classified questions used for training:",
    labeled_mask.sum()
)


print(
    "\nMining Engineering terms:",
    len(mining_engineering_terms)
)


print(
    "\nSaved:",
    OUTPUT_FILE
)


print(
    "Model saved:",
    MODEL_FILE
)