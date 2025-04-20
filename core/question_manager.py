import json
import os
import shutil
from datetime import datetime
import logging
from typing import List, Dict, Optional
from .ai_generator import AIGenerator
from .user_history import UserHistory
from .category_question_manager import CategoryQuestionManager

logger = logging.getLogger('QuizApp')

class QuestionManager:
    def __init__(self, ai_generator: AIGenerator):
        """Initialize the Question Manager."""
        self.ai_generator = ai_generator
        self.questions: List[Dict] = []
        self.current_user: Optional[str] = None
        self.user_history: Optional[UserHistory] = None

        # Dictionary to store category managers
        self.category_managers = {}

        # Default categories
        self.default_categories = [
            "Science", "History", "Geography", "Literature",
            "Movies", "Sports", "Technology", "Music"
        ]
        self.categories = set(self.default_categories)
        self.difficulties = {"easy", "medium", "hard"}

        # Setup paths
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.questions_file = os.path.join(self.base_path, 'data', 'questions.json')
        self.backup_dir = os.path.join(self.base_path, 'data', 'backup')
        self.categories_file = os.path.join(self.base_path, 'data', 'categories.json')

        # Load existing questions
        self.load_questions()

        # Initialize category managers for all categories
        for category in self.categories:
            self._get_category_manager(category)

        # Load custom categories if available
        self.load_categories()

    def _get_category_manager(self, category: str) -> CategoryQuestionManager:
        """Get or create a category manager for the specified category.

        Args:
            category: The category name

        Returns:
            CategoryQuestionManager for the specified category
        """
        if category not in self.category_managers:
            self.category_managers[category] = CategoryQuestionManager(category)
        return self.category_managers[category]

    def load_questions(self) -> None:
        """Load questions from the JSON file."""
        try:
            if os.path.exists(self.questions_file):
                with open(self.questions_file, 'r') as f:
                    self.questions = json.load(f)
                    # Update categories with existing ones from questions
                    for q in self.questions:
                        self.categories.add(q['category'])
                logger.info(f"Loaded {len(self.questions)} questions")
            else:
                logger.info("No existing questions file found")
        except Exception as e:
            logger.error(f"Error loading questions: {str(e)}")
            self.questions = []

    def save_questions(self) -> None:
        """Save questions to the JSON file."""
        try:
            # Create backup
            self._create_backup()

            # Save current questions
            with open(self.questions_file, 'w') as f:
                json.dump(self.questions, f, indent=4)
            logger.info(f"Saved {len(self.questions)} questions")
        except Exception as e:
            logger.error(f"Error saving questions: {str(e)}")
            raise

    def _create_backup(self) -> None:
        """Create a backup of the current questions file."""
        if os.path.exists(self.questions_file):
            # Ensure backup directory exists
            os.makedirs(self.backup_dir, exist_ok=True)

            # Create backup filename with timestamp
            backup_file = os.path.join(
                self.backup_dir,
                f'questions_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )

            # Copy the file
            shutil.copy2(self.questions_file, backup_file)
            logger.info(f"Created backup at {backup_file}")

            # Clean up old backups (keep only the 10 most recent)
            self._cleanup_old_backups()

    def get_questions(self, category: str, difficulty: str, count: int) -> List[Dict]:
        """Get a specific number of questions based on category and difficulty.

        This method prioritizes questions the user hasn't seen before to ensure
        variety and prevent repetition.
        """
        # Get the category manager for this category
        category_manager = self._get_category_manager(category)

        # Get questions from the category manager
        category_questions = category_manager.get_questions(difficulty, count)

        # Filter out questions the user has already seen if user history is available
        unseen_questions = []
        seen_questions = []

        if self.user_history and category_questions:
            # Split into seen and unseen questions
            unseen_questions = self.user_history.filter_unseen_questions(category, category_questions)
            seen_questions = [q for q in category_questions if q not in unseen_questions]
            logger.info(f"Found {len(unseen_questions)} unseen and {len(seen_questions)} seen questions")
        else:
            # No user history, treat all as unseen
            unseen_questions = category_questions

        # If not enough unseen questions, generate more
        needed_questions = count - len(unseen_questions)
        if needed_questions > 0:
            logger.info(f"Generating {needed_questions} more questions for {category} ({difficulty})")
            new_questions = self.ai_generator.generate_questions(
                category, difficulty, needed_questions
            )

            # Add new questions to the category manager
            if new_questions:
                category_manager.add_questions(new_questions)
                unseen_questions.extend(new_questions)
                self.categories.add(category)

                # Also add to main questions collection for backward compatibility
                self.questions.extend(new_questions)
                self.save_questions()

        # Shuffle the unseen questions to get a random selection
        import random
        random.shuffle(unseen_questions)

        # If we still don't have enough questions, use seen questions
        result_questions = unseen_questions[:count]
        if len(result_questions) < count and seen_questions:
            # Shuffle seen questions and add as many as needed
            random.shuffle(seen_questions)
            needed = count - len(result_questions)
            result_questions.extend(seen_questions[:needed])
            logger.info(f"Added {min(needed, len(seen_questions))} previously seen questions")

        # Record these questions as seen if user history is available
        if self.user_history and result_questions:
            self.user_history.add_seen_questions(category, result_questions)

        # Return the questions
        return result_questions

    def add_question(self, question: Dict) -> None:
        """Add a new question to the collection."""
        # Add to main questions collection for backward compatibility
        self.questions.append(question)

        # Add to category-specific collection
        category = question['category']
        self.categories.add(category)

        # Get the category manager and add the question
        category_manager = self._get_category_manager(category)
        category_manager.add_questions([question])

        # Save main questions collection
        self.save_questions()

    def remove_question(self, question: Dict) -> None:
        """Remove a question from the collection."""
        self.questions.remove(question)
        # Update categories if needed
        self._update_categories()
        self.save_questions()

    def _update_categories(self) -> None:
        """Update the categories based on existing questions and defaults."""
        # Add categories from existing questions
        question_categories = {q['category'] for q in self.questions}

        # Combine with default categories
        self.categories = question_categories.union(set(self.default_categories))

    def get_categories(self) -> List[str]:
        """Get list of available categories."""
        return sorted(list(self.categories))

    def get_difficulties(self) -> List[str]:
        """Get list of available difficulties."""
        return sorted(list(self.difficulties))

    def regenerate_questions(self, category: str, difficulty: str, count: int) -> List[Dict]:
        """Force regenerate questions using AI."""
        # Generate new questions with priority on AI model
        new_questions = self.ai_generator.generate_questions(category, difficulty, count)

        if new_questions:
            # Add to category-specific collection
            category_manager = self._get_category_manager(category)
            category_manager.add_questions(new_questions)

            # Add to main questions collection for backward compatibility
            self.questions.extend(new_questions)
            self.categories.add(category)
            self.save_questions()

            logger.info(f"Generated {len(new_questions)} new questions for {category} ({difficulty})")

        return new_questions

    def is_ai_ready(self) -> bool:
        """Check if the AI generator is ready."""
        return self.ai_generator.is_ready()

    def set_current_user(self, username: str) -> None:
        """Set the current user and initialize user history.

        Args:
            username: The username to set as current user
        """
        self.current_user = username
        if username:
            self.user_history = UserHistory(username)
            logger.info(f"Set current user to {username} and initialized user history")
        else:
            self.user_history = None
            logger.info("Cleared current user")

    def load_categories(self) -> None:
        """Load custom categories from the categories file."""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r') as f:
                    custom_categories = json.load(f)
                    # Add custom categories to our set
                    for category in custom_categories:
                        self.categories.add(category['name'])
                logger.info(f"Loaded {len(custom_categories)} custom categories")
        except Exception as e:
            logger.error(f"Error loading custom categories: {str(e)}")

    def save_categories(self) -> None:
        """Save custom categories to the categories file."""
        try:
            # Get custom categories (those not in default_categories)
            custom_categories = []
            for category in sorted(list(self.categories)):
                if category not in self.default_categories:
                    custom_categories.append({
                        'name': category,
                        'created_at': datetime.now().isoformat()
                    })

            # Save to file
            with open(self.categories_file, 'w') as f:
                json.dump(custom_categories, f, indent=4)
            logger.info(f"Saved {len(custom_categories)} custom categories")
        except Exception as e:
            logger.error(f"Error saving custom categories: {str(e)}")

    def add_category(self, category_name: str) -> bool:
        """Add a new category.

        Args:
            category_name: The name of the category to add

        Returns:
            True if the category was added, False if it already exists
        """
        if category_name in self.categories:
            logger.info(f"Category {category_name} already exists")
            return False

        # Add to categories set
        self.categories.add(category_name)

        # Initialize a category manager for the new category
        self._get_category_manager(category_name)

        # Save categories to file
        self.save_categories()
        logger.info(f"Added new category: {category_name}")
        return True

    def get_category_question_counts(self) -> Dict[str, Dict[str, int]]:
        """Get the count of questions for each category and difficulty.

        Returns:
            Dictionary with category names as keys and dictionaries of difficulty counts as values
        """
        result = {}

        for category in self.categories:
            category_manager = self._get_category_manager(category)
            result[category] = category_manager.get_question_count()

        return result

    def _cleanup_old_backups(self, max_backups: int = 10) -> None:
        """Clean up old backup files, keeping only the most recent ones.

        Args:
            max_backups: Maximum number of backup files to keep
        """
        try:
            # Check if backup directory exists
            if not os.path.exists(self.backup_dir):
                return

            # Get all backup files
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('questions_backup_') and filename.endswith('.json'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)

            # Remove old backups
            if len(backup_files) > max_backups:
                for filepath, _ in backup_files[max_backups:]:
                    try:
                        os.remove(filepath)
                        logger.info(f"Removed old backup: {os.path.basename(filepath)}")
                    except Exception as e:
                        logger.error(f"Error removing backup {filepath}: {str(e)}")
        except Exception as e:
            logger.error(f"Error cleaning up backups: {str(e)}")