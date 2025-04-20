import json
import re
import os
import glob

def clean_fallback_questions():
    """Remove sample questions from fallback_questions.json"""
    print("Cleaning fallback_questions.json...")

    # Load the file
    with open('data/fallback_questions.json', 'r') as f:
        data = json.load(f)

    # Count original questions
    original_count = 0
    for category in data:
        for difficulty in data[category]:
            original_count += len(data[category][difficulty])

    # Filter out sample questions
    for category in data:
        for difficulty in data[category]:
            # Keep only non-sample questions
            data[category][difficulty] = [
                q for q in data[category][difficulty]
                if not re.search(r'sample|Sample|treasure hunt', q['question'])
            ]

    # Count remaining questions
    remaining_count = 0
    for category in data:
        for difficulty in data[category]:
            remaining_count += len(data[category][difficulty])

    # Save the cleaned data
    with open('data/fallback_questions.json', 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Removed {original_count - remaining_count} sample questions from fallback_questions.json")
    print(f"Remaining questions: {remaining_count}")

def clean_fallback_questions_backup():
    """Remove sample questions from fallback_questions_backup.json"""
    if os.path.exists('data/fallback_questions_backup.json'):
        print("Cleaning fallback_questions_backup.json...")

        # Load the file
        with open('data/fallback_questions_backup.json', 'r') as f:
            data = json.load(f)

        # Count original questions
        original_count = 0
        for category in data:
            for difficulty in data[category]:
                original_count += len(data[category][difficulty])

        # Filter out sample questions
        for category in data:
            for difficulty in data[category]:
                # Keep only non-sample questions
                data[category][difficulty] = [
                    q for q in data[category][difficulty]
                    if not re.search(r'sample|Sample|treasure hunt', q['question'])
                ]

        # Count remaining questions
        remaining_count = 0
        for category in data:
            for difficulty in data[category]:
                remaining_count += len(data[category][difficulty])

        # Save the cleaned data
        with open('data/fallback_questions_backup.json', 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Removed {original_count - remaining_count} sample questions from fallback_questions_backup.json")
        print(f"Remaining questions: {remaining_count}")
    else:
        print("No fallback_questions_backup.json file found.")

def clean_questions():
    """Remove sample questions from questions.json"""
    print("Cleaning questions.json...")

    # Load the file
    with open('data/questions.json', 'r') as f:
        data = json.load(f)

    # Count original questions
    original_count = len(data)

    # Filter out sample questions
    data = [
        q for q in data
        if not re.search(r'sample|Sample|treasure hunt', q['question'])
    ]

    # Save the cleaned data
    with open('data/questions.json', 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Removed {original_count - len(data)} sample questions from questions.json")
    print(f"Remaining questions: {len(data)}")

def clean_backup_questions():
    """Clean all backup question files in the backup directory"""
    backup_files = glob.glob('data/backup/questions_backup_*.json')

    if backup_files:
        print(f"Cleaning {len(backup_files)} backup files...")

        for backup_file in backup_files:
            try:
                # Load the file
                with open(backup_file, 'r') as f:
                    data = json.load(f)

                # Count original questions
                original_count = len(data)

                # Filter out sample questions
                data = [
                    q for q in data
                    if not re.search(r'sample|Sample|treasure hunt', q['question'])
                ]

                # Save the cleaned data
                with open(backup_file, 'w') as f:
                    json.dump(data, f, indent=4)

                print(f"  Removed {original_count - len(data)} sample questions from {os.path.basename(backup_file)}")
            except Exception as e:
                print(f"  Error cleaning {os.path.basename(backup_file)}: {str(e)}")
    else:
        print("No backup files found.")

if __name__ == "__main__":
    # Make sure the data directory exists
    if not os.path.exists('data'):
        print("Error: data directory not found")
        exit(1)

    # Clean all files
    clean_fallback_questions()
    clean_fallback_questions_backup()
    clean_questions()
    clean_backup_questions()

    print("Done! All sample questions have been removed.")
