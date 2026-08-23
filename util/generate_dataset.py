import os
import json
import time
import urllib.request
import pandas as pd

OUTPUT_CSV = "data/gate_1000_questions.csv"
TARGET_TOTAL_QUESTIONS = 1000
BATCH_SIZE = 1  
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"

os.makedirs("data", exist_ok=True)

SYLLABUS_MODULES = [
    {
        "subject": "General Aptitude & Reasoning",
        "topics": "Logical deduction, syllogisms, spatial reasoning, speed-time-distance, percentages, and data interpretation"
    },
    {
        "subject": "Engineering Mathematics",
        "topics": "Matrix eigenvalues, Cayley-Hamilton theorem, first/second-order ODEs, Simpson's 1/3 rule, Poisson distribution"
    },
    {
        "subject": "Geomechanics & Ground Control",
        "topics": "Mohr-Coulomb failure, Bieniawski RMR, Barton Q-system, tributary area pillar stress, rock bolt capacity"
    },
    {
        "subject": "Mine Ventilation & Environment",
        "topics": "Atkinson's friction law, fan characteristic curves, natural ventilation pressure, Coward flammability triangle"
    },
    {
        "subject": "Mine Surveying & Geomatics",
        "topics": "Bowditch rule traverse closing error, missing line computation, leveling sensitivity, EDM corrections"
    },
    {
        "subject": "Surface & Underground Mining Methods",
        "topics": "Bord and Pillar depillaring, Longwall powered support resistance, stripping ratios, blast powder factor"
    },
    {
        "subject": "Mining Machinery & Materials Handling",
        "topics": "Koepe winder slip criteria, wire rope static factor of safety, belt conveyor power, shovel-dumper match index"
    },
    {
        "subject": "Mine Planning, Geostatistics & Economics",
        "topics": "Net Present Value, Internal Rate of Return, spherical semivariogram sill/nugget, Ordinary Kriging estimation variance"
    }
]

DIFFICULTY_TIERS = [
    {"target_level": 2, "desc": "Tier 1: 1-mark GATE conceptual, statutory definitions, and basic formula applications."},
    {"target_level": 6, "desc": "Tier 2: 1-mark numericals and standard single-step calculations."},
    {"target_level": 10, "desc": "Tier 3: 2-mark GATE multi-step engineering calculations with multiple dependent parameters."},
    {"target_level": 14, "desc": "Tier 4: Advanced 2-mark comprehensive numerical problems with multi-variable parameters."}
]

def generate_single_question(subject, topics, tier_info):
    prompt = f"""You are an IIT professor creating an authentic GATE Mining Engineering (MN) question bank.

Generate exactly 1 distinct multiple choice question.
- Subject: {subject}
- Focus Concepts: {topics}
- Difficulty: {tier_info['desc']} (Assign base difficulty = {tier_info['target_level']})

Requirements:
1. Base the question on authentic GATE MN examination patterns.
2. Include accurate engineering units (MPa, kN, m³/s, Ns²/m⁸, etc.) where applicable.
3. 'correct' must be an integer index (0 for Option A, 1 for Option B, 2 for Option C, 3 for Option D).
4. Do NOT include any explanations or solutions.

Return ONLY a valid JSON object matching this structure:
{{
  "subject": "{subject}",
  "topic": "{topics.split(',')[0]}",
  "difficulty": {tier_info['target_level']},
  "question": "Full problem statement text",
  "option_a": "Option A text",
  "option_b": "Option B text",
  "option_c": "Option C text",
  "option_d": "Option D text",
  "correct": 0
}}"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a JSON-only response engine. Output raw JSON objects only."},
            {"role": "user", "content": prompt}
        ],
        "format": "json",
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": 0.4,
            "num_predict": 512,  # Compact token limit for instant generation
            "num_ctx": 2048
        }
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        content = res_data.get("message", {}).get("content", "{}")
        return json.loads(content)

def main():
    if os.path.exists(OUTPUT_CSV):
        existing_df = pd.read_csv(OUTPUT_CSV)
        all_questions = existing_df.to_dict('records')
        print(f" Checkpoint found: Resuming with {len(all_questions)}/{TARGET_TOTAL_QUESTIONS} questions.")
    else:
        all_questions = []

    print(f" Starting offline fast generation (1 Q/call) via local Ollama ({MODEL_NAME})...")

    counter = len(all_questions)
    while len(all_questions) < TARGET_TOTAL_QUESTIONS:
        for module in SYLLABUS_MODULES:
            for tier in DIFFICULTY_TIERS:
                if len(all_questions) >= TARGET_TOTAL_QUESTIONS:
                    break

                counter += 1
                print(f" Q#{counter} | [{module['subject'][:22]}] Tier {tier['target_level']}...", end=" ", flush=True)
                start_t = time.time()

                try:
                    q_data = generate_single_question(
                        subject=module["subject"],
                        topics=module["topics"],
                        tier_info=tier
                    )

                    # Extract question dictionary
                    if isinstance(q_data, dict):
                        if "question" in q_data:
                            item = q_data
                        elif "questions" in q_data and len(q_data["questions"]) > 0:
                            item = q_data["questions"][0]
                        else:
                            item = list(q_data.values())[0] if q_data else None
                    else:
                        item = None

                    if item and isinstance(item, dict) and "question" in item:
                        # Ensure explanation key is excluded
                        item.pop("explanation", None)
                        all_questions.append(item)

                        # Write checkpoint
                        temp_df = pd.DataFrame(all_questions)
                        temp_df.to_csv(OUTPUT_CSV, index=False)
                        
                        elapsed = round(time.time() - start_t, 2)
                        print(f" ({elapsed}s) -> Total: {len(all_questions)}/{TARGET_TOTAL_QUESTIONS}")
                    else:
                        print(" Skipping invalid JSON format...")

                except Exception as e:
                    print(f" Error ({e}). Retrying...")
                    time.sleep(0.5)
                    continue

    final_questions = all_questions[:TARGET_TOTAL_QUESTIONS]
    for idx, q in enumerate(final_questions, start=1):
        q["id"] = idx

    df = pd.DataFrame(final_questions)
    cols = ["id", "subject", "topic", "difficulty", "question", "option_a", "option_b", "option_c", "option_d", "correct"]
    df = df[[c for c in cols if c in df.columns]]
    df.to_csv(OUTPUT_CSV, index=False)
    print(f" Finished! Compiled {len(df)} authentic questions to '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    main()