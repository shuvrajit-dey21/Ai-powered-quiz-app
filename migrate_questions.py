import json
import os
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('QuizApp')

def migrate_questions():
    """Migrate questions from the main questions.json file to category-specific files."""
    # Setup paths
    base_path = os.path.dirname(__file__)
    questions_file = os.path.join(base_path, 'data', 'questions.json')
    
    # Check if questions file exists
    if not os.path.exists(questions_file):
        logger.info("No questions.json file found. Nothing to migrate.")
        return
    
    # Load existing questions
    try:
        with open(questions_file, 'r') as f:
            questions = json.load(f)
        logger.info(f"Loaded {len(questions)} questions from questions.json")
    except Exception as e:
        logger.error(f"Error loading questions: {str(e)}")
        return
    
    # Group questions by category
    questions_by_category = {}
    for question in questions:
        category = question.get('category')
        if not category:
            logger.warning(f"Question missing category: {question}")
            continue
        
        if category not in questions_by_category:
            questions_by_category[category] = {
                "easy": [],
                "medium": [],
                "hard": []
            }
        
        difficulty = question.get('difficulty', 'medium').lower()
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"
        
        questions_by_category[category][difficulty].append(question)
    
    # Save each category to its own file
    for category, difficulties in questions_by_category.items():
        category_file = os.path.join(
            base_path, 
            'data', 
            f'{category.lower().replace(" ", "_")}_questions.json'
        )
        
        try:
            with open(category_file, 'w') as f:
                json.dump(difficulties, f, indent=4)
            
            total_questions = sum(len(questions) for questions in difficulties.values())
            logger.info(f"Saved {total_questions} questions for category {category}")
        except Exception as e:
            logger.error(f"Error saving questions for category {category}: {str(e)}")
    
    logger.info("Migration complete!")

if __name__ == "__main__":
    migrate_questions()
