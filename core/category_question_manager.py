import json
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger('QuizApp')

class CategoryQuestionManager:
    """Manages questions for a specific category."""
    
    def __init__(self, category: str):
        """Initialize the category question manager.
        
        Args:
            category: The category name
        """
        self.category = category
        self.questions_by_difficulty = {
            "easy": [],
            "medium": [],
            "hard": []
        }
        
        # Setup path for this category's JSON file
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.category_file = os.path.join(
            self.base_path, 
            'data', 
            f'{category.lower().replace(" ", "_")}_questions.json'
        )
        
        # Load existing questions for this category
        self.load_questions()
    
    def load_questions(self) -> None:
        """Load questions from the category-specific JSON file."""
        try:
            if os.path.exists(self.category_file):
                with open(self.category_file, 'r') as f:
                    self.questions_by_difficulty = json.load(f)
                
                total_questions = sum(len(questions) for questions in self.questions_by_difficulty.values())
                logger.info(f"Loaded {total_questions} questions for category {self.category}")
            else:
                logger.info(f"No existing questions file found for category {self.category}")
        except Exception as e:
            logger.error(f"Error loading questions for category {self.category}: {str(e)}")
            # Initialize with empty lists if there was an error
            self.questions_by_difficulty = {
                "easy": [],
                "medium": [],
                "hard": []
            }
    
    def save_questions(self) -> None:
        """Save questions to the category-specific JSON file."""
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(self.category_file), exist_ok=True)
            
            # Save current questions
            with open(self.category_file, 'w') as f:
                json.dump(self.questions_by_difficulty, f, indent=4)
            
            total_questions = sum(len(questions) for questions in self.questions_by_difficulty.values())
            logger.info(f"Saved {total_questions} questions for category {self.category}")
        except Exception as e:
            logger.error(f"Error saving questions for category {self.category}: {str(e)}")
            raise
    
    def get_questions(self, difficulty: str, count: int) -> List[Dict]:
        """Get a specific number of questions for this category and difficulty.
        
        Args:
            difficulty: The difficulty level (easy, medium, hard)
            count: Number of questions to retrieve
            
        Returns:
            List of question dictionaries
        """
        # Get questions for the specified difficulty
        available_questions = self.questions_by_difficulty.get(difficulty, [])
        
        # If we have enough questions, return a random selection
        import random
        if len(available_questions) >= count:
            # Make a copy to avoid modifying the original list
            questions_copy = available_questions.copy()
            random.shuffle(questions_copy)
            return questions_copy[:count]
        
        # Otherwise, return all available questions
        return available_questions
    
    def add_questions(self, questions: List[Dict]) -> None:
        """Add questions to this category.
        
        Args:
            questions: List of question dictionaries
        """
        # Group questions by difficulty
        for question in questions:
            difficulty = question.get('difficulty', 'medium').lower()
            
            # Ensure the difficulty is valid
            if difficulty not in self.questions_by_difficulty:
                difficulty = 'medium'
            
            # Add the question to the appropriate difficulty
            self.questions_by_difficulty[difficulty].append(question)
        
        # Save the updated questions
        self.save_questions()
    
    def get_question_count(self) -> Dict[str, int]:
        """Get the count of questions by difficulty.
        
        Returns:
            Dictionary with counts by difficulty
        """
        return {
            difficulty: len(questions)
            for difficulty, questions in self.questions_by_difficulty.items()
        }
    
    def get_total_question_count(self) -> int:
        """Get the total count of questions for this category.
        
        Returns:
            Total number of questions
        """
        return sum(len(questions) for questions in self.questions_by_difficulty.values())
