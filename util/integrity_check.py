import os
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "GATE_800_Questions_Classified.csv")

def verify_dataset_integrity():
    if not os.path.exists(CSV_PATH):
        print(f"File not found at '{CSV_PATH}'.")
        return

    df = pd.read_csv(CSV_PATH)
    print(f"Running full integrity audit on '{CSV_PATH}'...\n")
    
    issues_found = 0
    total_rows = len(df)
    print(f"Total Records: {total_rows}")
    
    expected_cols = ["subject", "topic", "difficulty", "question", "option_a", "option_b", "option_c", "option_d", "correct"]
    existing_cols = [col for col in expected_cols if col in df.columns]
    missing_cols = [col for col in expected_cols if col not in df.columns]
    
    if missing_cols:
        print(f"Missing core columns: {missing_cols}")
        issues_found += len(missing_cols)
    else:
        print("Column Schema: All core question and option columns present.")

    if "id" not in df.columns:
        print("Notice: 'id' column not found (will be assigned upon full dataset completion).")

    null_counts = df[existing_cols].isnull().sum()
    has_nulls = False
    for col, count in null_counts.items():
        if count > 0:
            print(f"Column '{col}' contains {count} null/missing values.")
            has_nulls = True
            issues_found += count
    if not has_nulls:
        print("Completeness: Zero null or missing cells across all columns.")

    if 'correct' in df.columns:
        invalid_correct = df[~df['correct'].isin([0, 1, 2, 3, '0', '1', '2', '3'])]
        if len(invalid_correct) > 0:
            print(f"Invalid 'correct' index found in {len(invalid_correct)} rows.")
            issues_found += len(invalid_correct)
        else:
            print("Correct Key Validity: All answer pointers are valid indices (0, 1, 2, 3).")

    if 'question' in df.columns:
        duplicates = df[df.duplicated(subset=['question'], keep=False)]
        if len(duplicates) > 0:
            unique_dup_count = df.duplicated(subset=['question']).sum()
            print(f"Duplicate Questions: {unique_dup_count} duplicate rows detected.")
        else:
            print("Uniqueness: No duplicate question statements found.")

    if 'difficulty' in df.columns:
        diff_counts = df['difficulty'].value_counts().sort_index()
        unique_tiers = sorted(df['difficulty'].unique())
        print(f"\nDifficulty Distribution (Tiers {min(unique_tiers)} to {max(unique_tiers)}):")
        for tier, count in diff_counts.items():
            pct = (count / total_rows) * 100
            print(f"   Tier {tier:>2}: {count:>4} questions ({pct:.1f}%)")

    if 'subject' in df.columns:
        subj_counts = df['subject'].value_counts()
        print("\nSubject Coverage:")
        for subj, count in subj_counts.items():
            pct = (count / total_rows) * 100
            print(f"   {subj[:32]:<32}: {count:>4} questions ({pct:.1f}%)")

    print("\n" + "="*50)
    if issues_found == 0:
        print("INTEGRITY CHECK PASSED: Dataset is clean and valid.")
    else:
        print(f"INTEGRITY CHECK COMPLETED: {issues_found} total issues identified.")
    print("="*50)

if __name__ == "__main__":
    verify_dataset_integrity()