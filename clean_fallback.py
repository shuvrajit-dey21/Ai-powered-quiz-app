import json
import re

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
