import json
import os
import logging
from typing import List, Dict, Set, Optional
from datetime import datetime

logger = logging.getLogger('QuizApp')

class UserHistory:
    """Class to track user question history to prevent repetition."""
    
    def __init__(self, username: str):
        """Initialize user history tracker.
        
        Args:
            username: The username to track history for
        """
        self.username = username
        self.seen_questions: Dict[str, Set[str]] = {}  # category -> set of question hashes
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.history_file = os.path.join(self.base_path, 'data', f'user_history_{username}.json')
        
        # Load existing history
        self.load_history()
    
    def load_history(self) -> None:
        """Load question history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    # Convert lists back to sets
                    self.seen_questions = {
                        category: set(question_hashes)
                        for category, question_hashes in data.items()
                    }
                logger.info(f"Loaded question history for user {self.username}")
            else:
                logger.info(f"No existing history file for user {self.username}")
                self.seen_questions = {}
        except Exception as e:
            logger.error(f"Error loading question history: {str(e)}")
            self.seen_questions = {}
    
    def save_history(self) -> None:
        """Save question history to file."""
        try:
            # Convert sets to lists for JSON serialization
            data = {
                category: list(question_hashes)
                for category, question_hashes in self.seen_questions.items()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # Save to file
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved question history for user {self.username}")
        except Exception as e:
            logger.error(f"Error saving question history: {str(e)}")
    
    def add_seen_questions(self, category: str, questions: List[Dict]) -> None:
        """Add questions to the seen list.
        
        Args:
            category: The category of the questions
            questions: List of question dictionaries
        """
        # Initialize category if not exists
        if category not in self.seen_questions:
            self.seen_questions[category] = set()
        
        # Add question hashes to the set
        for question in questions:
            question_hash = self._hash_question(question)
            self.seen_questions[category].add(question_hash)
        
        # Save updated history
        self.save_history()
    
    def filter_unseen_questions(self, category: str, questions: List[Dict]) -> List[Dict]:
        """Filter out questions the user has already seen.
        
        Args:
            category: The category of the questions
            questions: List of question dictionaries
            
        Returns:
            List of questions the user hasn't seen yet
        """
        if category not in self.seen_questions:
            # User hasn't seen any questions in this category
            return questions
        
        # Filter out seen questions
        unseen_questions = []
        for question in questions:
            question_hash = self._hash_question(question)
            if question_hash not in self.seen_questions[category]:
                unseen_questions.append(question)
        
        return unseen_questions
    
    def _hash_question(self, question: Dict) -> str:
        """Create a hash for a question to track uniqueness.
        
        Args:
            question: Question dictionary
            
        Returns:
            String hash of the question
        """
        # Use the question text as the hash
        # This is simple but effective for most cases
        return question.get("question", "").strip().lower()
    
    def clear_history(self, category: Optional[str] = None) -> None:
        """Clear user history for a category or all categories.
        
        Args:
            category: Optional category to clear. If None, clears all history.
        """
        if category:
            if category in self.seen_questions:
                self.seen_questions[category] = set()
                logger.info(f"Cleared history for category {category} for user {self.username}")
        else:
            self.seen_questions = {}
            logger.info(f"Cleared all history for user {self.username}")
        
        # Save updated history
        self.save_history()
