import json
import logging
import threading
import os
import random
import urllib.request
import urllib.parse
import urllib.error
import html
import time
import re
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Import for local AI model
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch
    # Check if accelerate is available
    try:
        import accelerate
        ACCELERATE_AVAILABLE = True
    except ImportError:
        ACCELERATE_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    ACCELERATE_AVAILABLE = False

logger = logging.getLogger('QuizApp')

class AIGenerator:
    def __init__(self, use_fallback=True, model_name=None):
        """Initialize the AI Generator with fallback questions.

        Args:
            use_fallback (bool): Whether to use fallback mode instead of AI model
            model_name (str, optional): Name of the model to use. Defaults to None, which uses the default model.
                Supported models: 'distilgpt2', 'gpt2-small', 'facebook/opt-125m', 'distilbert-base-uncased'
        """
        # Set fallback mode based on parameter
        self.use_fallback = use_fallback

        # Initialize state
        self.is_model_ready = False
        self.local_model = None
        self.tokenizer = None
        self.generator = None
        self.model_loading_thread = None
        self.model_name = model_name or "distilgpt2"  # Default to distilgpt2 if not specified

        # Load fallback questions
        self.fallback_questions = self._load_fallback_questions()

        # Load geography questions from JSON backup
        self.geography_questions = self._load_geography_questions()

        # API URL for Open Trivia Database
        self.api_url = "https://opentdb.com/api.php"

        # Maximum time to wait for local AI model (in seconds)
        self.max_wait_time = 10  # Increased from 5 to 10 seconds for better results

        # Track model loading attempts
        self.model_loading_attempts = 0
        self.max_model_loading_attempts = 3

        # Start loading the model in a separate thread if not using fallback
        if not self.use_fallback and TRANSFORMERS_AVAILABLE:
            if not ACCELERATE_AVAILABLE:
                logger.warning("Accelerate library not available. Using CPU-only mode for local model.")

            logger.info(f"Starting to load local AI model '{self.model_name}' in background")
            self.model_loading_thread = threading.Thread(target=self._load_local_model)
            self.model_loading_thread.daemon = True
            self.model_loading_thread.start()
        else:
            if not TRANSFORMERS_AVAILABLE:
                logger.warning("Transformers library not available. Using fallback mode.")
            else:
                logger.info("Using fallback mode for questions (local AI model disabled)")
            self.is_model_ready = True

    def _load_fallback_questions(self) -> Dict:
        """Load fallback questions from a file or use hardcoded ones."""
        fallback_dict = {}

        # Define categories
        categories = [
            "Science", "History", "Geography", "Literature",
            "Movies", "Sports", "Technology", "Music"
        ]

        # Try to load from file first
        fallback_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'fallback_questions.json'
        )

        if os.path.exists(fallback_file):
            try:
                with open(fallback_file, 'r') as f:
                    fallback_dict = json.load(f)
                logger.info(f"Loaded fallback questions from {fallback_file}")
                return fallback_dict
            except Exception as e:
                logger.error(f"Error loading fallback questions: {str(e)}")

        # If file doesn't exist or had error, create hardcoded questions
        logger.info("Creating hardcoded fallback questions")

        for category in categories:
            fallback_dict[category] = {
                "easy": self._create_fallback_questions(category, "easy", 10),
                "medium": self._create_fallback_questions(category, "medium", 10),
                "hard": self._create_fallback_questions(category, "hard", 10)
            }

        # Save for future use
        try:
            os.makedirs(os.path.dirname(fallback_file), exist_ok=True)
            with open(fallback_file, 'w') as f:
                json.dump(fallback_dict, f, indent=4)
            logger.info(f"Saved fallback questions to {fallback_file}")
        except Exception as e:
            logger.error(f"Error saving fallback questions: {str(e)}")

        return fallback_dict

    def _create_fallback_questions(self, category: str, difficulty: str, count: int) -> List[Dict]:
        """Create hardcoded fallback questions for a category and difficulty."""
        questions = []

        # Science questions
        if category == "Science":
            if difficulty == "easy":
                questions = [
                    {
                        "question": "What is the chemical symbol for water?",
                        "options": ["H2O", "CO2", "NaCl", "O2"],
                        "correct_answer": "H2O",
                        "category": "Science",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which planet is known as the Red Planet?",
                        "options": ["Mars", "Venus", "Jupiter", "Mercury"],
                        "correct_answer": "Mars",
                        "category": "Science",
                        "difficulty": "easy"
                    },
                    {
                        "question": "What is the closest star to Earth?",
                        "options": ["Sun", "Proxima Centauri", "Alpha Centauri", "Sirius"],
                        "correct_answer": "Sun",
                        "category": "Science",
                        "difficulty": "easy"
                    }
                ]
            elif difficulty == "medium":
                questions = [
                    {
                        "question": "Which element has the atomic number 79?",
                        "options": ["Gold", "Silver", "Platinum", "Copper"],
                        "correct_answer": "Gold",
                        "category": "Science",
                        "difficulty": "medium"
                    },
                    {
                        "question": "What is the process called where plants make their own food using sunlight?",
                        "options": ["Photosynthesis", "Respiration", "Digestion", "Fermentation"],
                        "correct_answer": "Photosynthesis",
                        "category": "Science",
                        "difficulty": "medium"
                    }
                ]
            elif difficulty == "hard":
                questions = [
                    {
                        "question": "What is the half-life of Carbon-14?",
                        "options": ["5,730 years", "1,600 years", "10,000 years", "3,200 years"],
                        "correct_answer": "5,730 years",
                        "category": "Science",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which subatomic particle has a positive charge?",
                        "options": ["Proton", "Neutron", "Electron", "Positron"],
                        "correct_answer": "Proton",
                        "category": "Science",
                        "difficulty": "hard"
                    }
                ]

        # History questions
        elif category == "History":
            if difficulty == "easy":
                questions = [
                    {
                        "question": "Who was the first President of the United States?",
                        "options": ["George Washington", "Thomas Jefferson", "Abraham Lincoln", "John Adams"],
                        "correct_answer": "George Washington",
                        "category": "History",
                        "difficulty": "easy"
                    },
                    {
                        "question": "In what year did World War II end?",
                        "options": ["1945", "1939", "1942", "1944"],
                        "correct_answer": "1945",
                        "category": "History",
                        "difficulty": "easy"
                    }
                ]

        # Geography questions
        elif category == "Geography":
            if difficulty == "easy":
                questions = [
                    {
                        "question": "What is the capital of France?",
                        "options": ["Paris", "London", "Berlin", "Madrid"],
                        "correct_answer": "Paris",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which ocean is the largest?",
                        "options": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"],
                        "correct_answer": "Pacific Ocean",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "What is the capital of Japan?",
                        "options": ["Tokyo", "Kyoto", "Osaka", "Hiroshima"],
                        "correct_answer": "Tokyo",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which is the longest river in the world?",
                        "options": ["Nile", "Amazon", "Mississippi", "Yangtze"],
                        "correct_answer": "Nile",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which country has the largest population in the world?",
                        "options": ["China", "India", "United States", "Russia"],
                        "correct_answer": "China",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "On which continent is the Sahara Desert located?",
                        "options": ["Africa", "Asia", "Australia", "South America"],
                        "correct_answer": "Africa",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "What is the name of the tallest mountain in the world?",
                        "options": ["Mount Everest", "K2", "Mount Kilimanjaro", "Mount Fuji"],
                        "correct_answer": "Mount Everest",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which country is home to the Great Barrier Reef?",
                        "options": ["Australia", "Mexico", "Thailand", "Brazil"],
                        "correct_answer": "Australia",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "What is the capital of Canada?",
                        "options": ["Ottawa", "Toronto", "Vancouver", "Montreal"],
                        "correct_answer": "Ottawa",
                        "category": "Geography",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which of these countries is NOT in Europe?",
                        "options": ["Egypt", "Spain", "Italy", "Germany"],
                        "correct_answer": "Egypt",
                        "category": "Geography",
                        "difficulty": "easy"
                    }
                ]
            elif difficulty == "medium":
                questions = [
                    {
                        "question": "Which country has the most pyramids?",
                        "options": ["Sudan", "Egypt", "Mexico", "Peru"],
                        "correct_answer": "Sudan",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "What is the capital of Australia?",
                        "options": ["Canberra", "Sydney", "Melbourne", "Perth"],
                        "correct_answer": "Canberra",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which of these countries is landlocked?",
                        "options": ["Bolivia", "Peru", "Ecuador", "Chile"],
                        "correct_answer": "Bolivia",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which African country was formerly known as Abyssinia?",
                        "options": ["Ethiopia", "Nigeria", "Kenya", "Morocco"],
                        "correct_answer": "Ethiopia",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "The Strait of Gibraltar connects the Atlantic Ocean to which sea?",
                        "options": ["Mediterranean Sea", "Red Sea", "Black Sea", "Baltic Sea"],
                        "correct_answer": "Mediterranean Sea",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "What is the largest desert in the world?",
                        "options": ["Antarctic Desert", "Sahara Desert", "Arabian Desert", "Gobi Desert"],
                        "correct_answer": "Antarctic Desert",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which country has the most natural lakes?",
                        "options": ["Canada", "United States", "Russia", "Finland"],
                        "correct_answer": "Canada",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "What is the capital of New Zealand?",
                        "options": ["Wellington", "Auckland", "Christchurch", "Queenstown"],
                        "correct_answer": "Wellington",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which mountain range separates Europe from Asia?",
                        "options": ["Ural Mountains", "Alps", "Caucasus Mountains", "Carpathian Mountains"],
                        "correct_answer": "Ural Mountains",
                        "category": "Geography",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which river flows through the Grand Canyon?",
                        "options": ["Colorado River", "Missouri River", "Rio Grande", "Mississippi River"],
                        "correct_answer": "Colorado River",
                        "category": "Geography",
                        "difficulty": "medium"
                    }
                ]
            elif difficulty == "hard":
                questions = [
                    {
                        "question": "Which South American country has the largest land area?",
                        "options": ["Brazil", "Argentina", "Peru", "Colombia"],
                        "correct_answer": "Brazil",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "What is the world's oldest continuously inhabited city?",
                        "options": ["Damascus", "Jerusalem", "Athens", "Rome"],
                        "correct_answer": "Damascus",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which country is the world's largest producer of coffee?",
                        "options": ["Brazil", "Colombia", "Vietnam", "Ethiopia"],
                        "correct_answer": "Brazil",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "In which country would you find the city of Timbuktu?",
                        "options": ["Mali", "Niger", "Chad", "Sudan"],
                        "correct_answer": "Mali",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which is the only country to border both the Atlantic and Indian Oceans?",
                        "options": ["South Africa", "Australia", "Brazil", "India"],
                        "correct_answer": "South Africa",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "What is the capital of Mongolia?",
                        "options": ["Ulaanbaatar", "Astana", "Bishkek", "Tashkent"],
                        "correct_answer": "Ulaanbaatar",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which country has the most time zones?",
                        "options": ["France", "Russia", "United States", "Australia"],
                        "correct_answer": "France",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "What is the lowest point on Earth's continental crust?",
                        "options": ["Dead Sea", "Caspian Sea", "Death Valley", "Lake Eyre"],
                        "correct_answer": "Dead Sea",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which country has the largest number of active volcanoes?",
                        "options": ["Indonesia", "Japan", "Philippines", "United States"],
                        "correct_answer": "Indonesia",
                        "category": "Geography",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which African country was never colonized by Europeans?",
                        "options": ["Ethiopia", "South Africa", "Kenya", "Nigeria"],
                        "correct_answer": "Ethiopia",
                        "category": "Geography",
                        "difficulty": "hard"
                    }
                ]

        # Literature questions
        elif category == "Literature":
            if difficulty == "easy":
                questions = [
                    {
                        "question": "Who wrote 'Romeo and Juliet'?",
                        "options": ["William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain"],
                        "correct_answer": "William Shakespeare",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Who wrote 'Harry Potter'?",
                        "options": ["J.K. Rowling", "Stephen King", "George R.R. Martin", "Tolkien"],
                        "correct_answer": "J.K. Rowling",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Who is the author of 'Pride and Prejudice'?",
                        "options": ["Jane Austen", "Charlotte Brontë", "Emily Brontë", "Virginia Woolf"],
                        "correct_answer": "Jane Austen",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "What is the name of the main character in 'The Great Gatsby'?",
                        "options": ["Jay Gatsby", "Nick Carraway", "Tom Buchanan", "Daisy Buchanan"],
                        "correct_answer": "Jay Gatsby",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Who wrote 'The Adventures of Tom Sawyer'?",
                        "options": ["Mark Twain", "Charles Dickens", "Ernest Hemingway", "F. Scott Fitzgerald"],
                        "correct_answer": "Mark Twain",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which novel begins with the line 'It was the best of times, it was the worst of times'?",
                        "options": ["A Tale of Two Cities", "Great Expectations", "Oliver Twist", "David Copperfield"],
                        "correct_answer": "A Tale of Two Cities",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Who wrote 'To Kill a Mockingbird'?",
                        "options": ["Harper Lee", "J.D. Salinger", "John Steinbeck", "F. Scott Fitzgerald"],
                        "correct_answer": "Harper Lee",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "What is the name of the hobbit in 'The Lord of the Rings'?",
                        "options": ["Frodo Baggins", "Bilbo Baggins", "Samwise Gamgee", "Gollum"],
                        "correct_answer": "Frodo Baggins",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "In which century did William Shakespeare live?",
                        "options": ["16th-17th century", "15th-16th century", "17th-18th century", "14th-15th century"],
                        "correct_answer": "16th-17th century",
                        "category": "Literature",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Who wrote 'The Catcher in the Rye'?",
                        "options": ["J.D. Salinger", "F. Scott Fitzgerald", "Ernest Hemingway", "Mark Twain"],
                        "correct_answer": "J.D. Salinger",
                        "category": "Literature",
                        "difficulty": "easy"
                    }
                ]
            elif difficulty == "medium":
                questions = [
                    {
                        "question": "Who wrote 'One Hundred Years of Solitude'?",
                        "options": ["Gabriel García Márquez", "Isabel Allende", "Jorge Luis Borges", "Pablo Neruda"],
                        "correct_answer": "Gabriel García Márquez",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which novel features the character Holden Caulfield?",
                        "options": ["The Catcher in the Rye", "The Great Gatsby", "To Kill a Mockingbird", "Lord of the Flies"],
                        "correct_answer": "The Catcher in the Rye",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Who wrote 'Crime and Punishment'?",
                        "options": ["Fyodor Dostoevsky", "Leo Tolstoy", "Anton Chekhov", "Nikolai Gogol"],
                        "correct_answer": "Fyodor Dostoevsky",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which Shakespeare play features the character Ophelia?",
                        "options": ["Hamlet", "Macbeth", "Romeo and Juliet", "King Lear"],
                        "correct_answer": "Hamlet",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Who wrote 'The Old Man and the Sea'?",
                        "options": ["Ernest Hemingway", "F. Scott Fitzgerald", "John Steinbeck", "William Faulkner"],
                        "correct_answer": "Ernest Hemingway",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which poet wrote 'The Road Not Taken'?",
                        "options": ["Robert Frost", "Walt Whitman", "Emily Dickinson", "T.S. Eliot"],
                        "correct_answer": "Robert Frost",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "What was Charles Dickens' final completed novel?",
                        "options": ["Our Mutual Friend", "Great Expectations", "A Tale of Two Cities", "David Copperfield"],
                        "correct_answer": "Our Mutual Friend",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which novel begins with the line 'Call me Ishmael'?",
                        "options": ["Moby-Dick", "The Great Gatsby", "The Old Man and the Sea", "To Kill a Mockingbird"],
                        "correct_answer": "Moby-Dick",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Who wrote the poetry collection 'Leaves of Grass'?",
                        "options": ["Walt Whitman", "Emily Dickinson", "Robert Frost", "T.S. Eliot"],
                        "correct_answer": "Walt Whitman",
                        "category": "Literature",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which novel features the character Jay Gatsby?",
                        "options": ["The Great Gatsby", "The Catcher in the Rye", "To Kill a Mockingbird", "Moby-Dick"],
                        "correct_answer": "The Great Gatsby",
                        "category": "Literature",
                        "difficulty": "medium"
                    }
                ]
            elif difficulty == "hard":
                questions = [
                    {
                        "question": "Who wrote 'Ulysses'?",
                        "options": ["James Joyce", "Virginia Woolf", "Marcel Proust", "D.H. Lawrence"],
                        "correct_answer": "James Joyce",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which author created the character Inspector Morse?",
                        "options": ["Colin Dexter", "Agatha Christie", "Arthur Conan Doyle", "P.D. James"],
                        "correct_answer": "Colin Dexter",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which novel by Albert Camus tells the story of a man named Meursault who kills an Arab?",
                        "options": ["The Stranger", "The Plague", "The Fall", "The Myth of Sisyphus"],
                        "correct_answer": "The Stranger",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Who wrote 'The Brothers Karamazov'?",
                        "options": ["Fyodor Dostoevsky", "Leo Tolstoy", "Anton Chekhov", "Ivan Turgenev"],
                        "correct_answer": "Fyodor Dostoevsky",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which author won the Nobel Prize in Literature in 1954?",
                        "options": ["Ernest Hemingway", "William Faulkner", "John Steinbeck", "T.S. Eliot"],
                        "correct_answer": "Ernest Hemingway",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which of these works is NOT by Shakespeare?",
                        "options": ["Doctor Faustus", "The Tempest", "King Lear", "Twelfth Night"],
                        "correct_answer": "Doctor Faustus",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Who wrote 'The Sound and the Fury'?",
                        "options": ["William Faulkner", "Ernest Hemingway", "F. Scott Fitzgerald", "John Steinbeck"],
                        "correct_answer": "William Faulkner",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "What was the original title of Jane Austen's 'Pride and Prejudice'?",
                        "options": ["First Impressions", "Social Standings", "Elizabeth and Darcy", "A Lady's Reputation"],
                        "correct_answer": "First Impressions",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which Russian author wrote 'War and Peace'?",
                        "options": ["Leo Tolstoy", "Fyodor Dostoevsky", "Anton Chekhov", "Nikolai Gogol"],
                        "correct_answer": "Leo Tolstoy",
                        "category": "Literature",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which literary movement was James Joyce associated with?",
                        "options": ["Modernism", "Romanticism", "Naturalism", "Realism"],
                        "correct_answer": "Modernism",
                        "category": "Literature",
                        "difficulty": "hard"
                    }
                ]

        # Movies questions
        elif category == "Movies":
            if difficulty == "easy":
                questions = [
                    {
                        "question": "Which movie won the Oscar for Best Picture in 2020?",
                        "options": ["Parasite", "1917", "Joker", "Once Upon a Time in Hollywood"],
                        "correct_answer": "Parasite",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Who directed the movie 'Titanic'?",
                        "options": ["James Cameron", "Steven Spielberg", "Christopher Nolan", "Martin Scorsese"],
                        "correct_answer": "James Cameron",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which actor played Iron Man in the Marvel Cinematic Universe?",
                        "options": ["Robert Downey Jr.", "Chris Evans", "Chris Hemsworth", "Mark Ruffalo"],
                        "correct_answer": "Robert Downey Jr.",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which animated movie features a character named Simba?",
                        "options": ["The Lion King", "Finding Nemo", "Toy Story", "Shrek"],
                        "correct_answer": "The Lion King",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Who played Jack in the movie 'Titanic'?",
                        "options": ["Leonardo DiCaprio", "Brad Pitt", "Tom Cruise", "Johnny Depp"],
                        "correct_answer": "Leonardo DiCaprio",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which of these movies is NOT directed by Christopher Nolan?",
                        "options": ["Avatar", "Inception", "Interstellar", "The Dark Knight"],
                        "correct_answer": "Avatar",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "What was the first movie in the 'Harry Potter' series?",
                        "options": ["Harry Potter and the Philosopher's Stone", "Harry Potter and the Chamber of Secrets", "Harry Potter and the Prisoner of Azkaban", "Harry Potter and the Goblet of Fire"],
                        "correct_answer": "Harry Potter and the Philosopher's Stone",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which actor played Neo in 'The Matrix'?",
                        "options": ["Keanu Reeves", "Tom Cruise", "Brad Pitt", "Will Smith"],
                        "correct_answer": "Keanu Reeves",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which movie features a character named Forrest Gump?",
                        "options": ["Forrest Gump", "The Green Mile", "Cast Away", "Saving Private Ryan"],
                        "correct_answer": "Forrest Gump",
                        "category": "Movies",
                        "difficulty": "easy"
                    },
                    {
                        "question": "Which of these is NOT a Pixar movie?",
                        "options": ["Shrek", "Toy Story", "Finding Nemo", "Up"],
                        "correct_answer": "Shrek",
                        "category": "Movies",
                        "difficulty": "easy"
                    }
                ]
            elif difficulty == "medium":
                questions = [
                    {
                        "question": "Who directed 'Pulp Fiction'?",
                        "options": ["Quentin Tarantino", "Martin Scorsese", "Steven Spielberg", "David Fincher"],
                        "correct_answer": "Quentin Tarantino",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which actor won an Oscar for his role in 'The Revenant'?",
                        "options": ["Leonardo DiCaprio", "Brad Pitt", "Matthew McConaughey", "Eddie Redmayne"],
                        "correct_answer": "Leonardo DiCaprio",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which movie features the character Hannibal Lecter?",
                        "options": ["The Silence of the Lambs", "Seven", "Psycho", "American Psycho"],
                        "correct_answer": "The Silence of the Lambs",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Who directed 'Schindler's List'?",
                        "options": ["Steven Spielberg", "Martin Scorsese", "Stanley Kubrick", "Francis Ford Coppola"],
                        "correct_answer": "Steven Spielberg",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which movie won the most Oscars in history?",
                        "options": ["Titanic, The Lord of the Rings: The Return of the King, and Ben-Hur (tied)", "Avatar", "Gone with the Wind", "The Godfather"],
                        "correct_answer": "Titanic, The Lord of the Rings: The Return of the King, and Ben-Hur (tied)",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which actress played Hermione Granger in the Harry Potter films?",
                        "options": ["Emma Watson", "Emma Stone", "Jennifer Lawrence", "Emma Roberts"],
                        "correct_answer": "Emma Watson",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "In which year was the first Star Wars movie released?",
                        "options": ["1977", "1980", "1975", "1983"],
                        "correct_answer": "1977",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "What is the highest-grossing animated film of all time (as of 2023)?",
                        "options": ["The Lion King (2019)", "Frozen II", "Super Mario Bros. Movie", "Incredibles 2"],
                        "correct_answer": "The Lion King (2019)",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Which film won the Academy Award for Best Picture in 2019?",
                        "options": ["Green Book", "Roma", "Black Panther", "A Star Is Born"],
                        "correct_answer": "Green Book",
                        "category": "Movies",
                        "difficulty": "medium"
                    },
                    {
                        "question": "Who directed 'Inception'?",
                        "options": ["Christopher Nolan", "James Cameron", "Steven Spielberg", "Martin Scorsese"],
                        "correct_answer": "Christopher Nolan",
                        "category": "Movies",
                        "difficulty": "medium"
                    }
                ]
            elif difficulty == "hard":
                questions = [
                    {
                        "question": "Which actor has won the most Academy Awards for Best Actor?",
                        "options": ["Daniel Day-Lewis", "Jack Nicholson", "Marlon Brando", "Tom Hanks"],
                        "correct_answer": "Daniel Day-Lewis",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Who directed the 1963 film '8½'?",
                        "options": ["Federico Fellini", "Ingmar Bergman", "Akira Kurosawa", "François Truffaut"],
                        "correct_answer": "Federico Fellini",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which movie was based on the novel 'Do Androids Dream of Electric Sheep?'",
                        "options": ["Blade Runner", "Total Recall", "The Matrix", "Minority Report"],
                        "correct_answer": "Blade Runner",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which film won the Palme d'Or at the Cannes Film Festival in 1994?",
                        "options": ["Pulp Fiction", "The Piano", "Schindler's List", "Three Colors: Red"],
                        "correct_answer": "Pulp Fiction",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Who was the youngest person to win an Academy Award for Best Director?",
                        "options": ["Damien Chazelle", "Orson Welles", "Steven Spielberg", "John Singleton"],
                        "correct_answer": "Damien Chazelle",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which film holds the record for most Academy Award nominations without winning any?",
                        "options": ["The Turning Point and The Color Purple (tied)", "American Hustle", "Gangs of New York", "The Irishman"],
                        "correct_answer": "The Turning Point and The Color Purple (tied)",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "In the original 'King Kong' (1933), what was the name of the island where Kong was found?",
                        "options": ["Skull Island", "Monster Island", "Kong Island", "Ape Island"],
                        "correct_answer": "Skull Island",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which actress has received the most Academy Award nominations without winning?",
                        "options": ["Glenn Close", "Amy Adams", "Deborah Kerr", "Thelma Ritter"],
                        "correct_answer": "Glenn Close",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Who was originally cast as Aragorn in 'The Lord of the Rings' before Viggo Mortensen?",
                        "options": ["Stuart Townsend", "Russell Crowe", "Nicolas Cage", "Daniel Day-Lewis"],
                        "correct_answer": "Stuart Townsend",
                        "category": "Movies",
                        "difficulty": "hard"
                    },
                    {
                        "question": "Which classic film features the line 'Rosebud'?",
                        "options": ["Citizen Kane", "Casablanca", "Gone with the Wind", "It's a Wonderful Life"],
                        "correct_answer": "Citizen Kane",
                        "category": "Movies",
                        "difficulty": "hard"
                    }
                ]

        # Sports questions
        elif category == "Sports":
            if difficulty == "easy":
                questions = [
                    {
                        "question": "In which sport would you perform a slam dunk?",
                        "options": ["Basketball", "Football", "Tennis", "Golf"],
                        "correct_answer": "Basketball",
                        "category": "Sports",
                        "difficulty": "easy"
                    }
                ]

        # Technology questions
        elif category == "Technology":
            if difficulty == "easy":
                questions = [
                    {
                        "question": "Who founded Microsoft?",
                        "options": ["Bill Gates", "Steve Jobs", "Mark Zuckerberg", "Jeff Bezos"],
                        "correct_answer": "Bill Gates",
                        "category": "Technology",
                        "difficulty": "easy"
                    }
                ]

        # Music questions
        elif category == "Music":
            if difficulty == "easy":
                questions = [
                    {
                        "question": "Which band performed the song 'Bohemian Rhapsody'?",
                        "options": ["Queen", "The Beatles", "Led Zeppelin", "Rolling Stones"],
                        "correct_answer": "Queen",
                        "category": "Music",
                        "difficulty": "easy"
                    }
                ]

        # Fill remaining with generic questions if needed
        while len(questions) < count:
            remaining = count - len(questions)
            logger.warning(f"Not enough real questions for {category} ({difficulty}). Creating {remaining} generic placeholders.")

            # Create more realistic generic questions based on the category
            if category == "Science":
                generic_q = {
                    "question": f"What scientific discovery was made in the {len(questions)+1}0s that revolutionized the field?",
                    "options": [
                        "Correct scientific theory",
                        "Incorrect scientific theory A",
                        "Incorrect scientific theory B",
                        "Incorrect scientific theory C"
                    ],
                    "correct_answer": "Correct scientific theory",
                    "category": category,
                    "difficulty": difficulty
                }
            elif category == "History":
                generic_q = {
                    "question": f"Which historical figure was most influential in the {len(questions)+1}th century?",
                    "options": [
                        "Correct historical figure",
                        "Incorrect historical figure A",
                        "Incorrect historical figure B",
                        "Incorrect historical figure C"
                    ],
                    "correct_answer": "Correct historical figure",
                    "category": category,
                    "difficulty": difficulty
                }
            elif category == "Geography":
                generic_q = {
                    "question": f"Which geographical feature is most prominent in {['Asia', 'Africa', 'Europe', 'North America'][len(questions) % 4]}?",
                    "options": [
                        "Correct geographical answer",
                        "Incorrect geographical answer A",
                        "Incorrect geographical answer B",
                        "Incorrect geographical answer C"
                    ],
                    "correct_answer": "Correct geographical answer",
                    "category": category,
                    "difficulty": difficulty
                }
            elif category == "Literature":
                generic_q = {
                    "question": f"Which author made the biggest contribution to {len(questions)+1}th century literature?",
                    "options": [
                        "Correct author",
                        "Incorrect author A",
                        "Incorrect author B",
                        "Incorrect author C"
                    ],
                    "correct_answer": "Correct author",
                    "category": category,
                    "difficulty": difficulty
                }
            else:
                # Generic fallback for other categories
                generic_q = {
                    "question": f"Important question about {category} (#{len(questions)+1})",
                    "options": [
                        "Correct Answer",
                        "Incorrect Answer A",
                        "Incorrect Answer B",
                        "Incorrect Answer C"
                    ],
                    "correct_answer": "Correct Answer",
                    "category": category,
                    "difficulty": difficulty
                }

            questions.append(generic_q)

        return questions

    def _load_local_model(self):
        """Load the local AI model for question generation with retry mechanism."""
        self.model_loading_attempts += 1
        try:
            logger.info(f"Loading local AI model '{self.model_name}' (attempt {self.model_loading_attempts}/{self.max_model_loading_attempts})...")

            # Configure model-specific parameters
            model_config = self._get_model_config(self.model_name)

            # Load tokenizer with appropriate settings
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=model_config.get('use_fast_tokenizer', True)
            )

            # Load model with appropriate settings based on available libraries
            if ACCELERATE_AVAILABLE:
                self.local_model = model_config['model_class'].from_pretrained(
                    self.model_name,
                    low_cpu_mem_usage=True,
                    device_map="auto"
                )
            else:
                # CPU-only mode
                self.local_model = model_config['model_class'].from_pretrained(
                    self.model_name,
                    low_cpu_mem_usage=True
                )

            # Create text generation pipeline with model-specific parameters
            pipeline_kwargs = {
                'model': self.local_model,
                'tokenizer': self.tokenizer,
                'max_length': model_config.get('max_length', 256),
                'do_sample': True,
                'temperature': model_config.get('temperature', 0.8),
                'top_p': model_config.get('top_p', 0.92),
                'num_return_sequences': 1
            }

            # Add pad_token_id for models that need it
            if model_config.get('needs_pad_token', True) and hasattr(self.tokenizer, 'eos_token_id'):
                pipeline_kwargs['pad_token_id'] = self.tokenizer.eos_token_id

            self.generator = pipeline(
                model_config.get('pipeline_task', 'text-generation'),
                **pipeline_kwargs
            )

            logger.info(f"Local AI model '{self.model_name}' loaded successfully")
            self.is_model_ready = True
        except Exception as e:
            logger.error(f"Error loading local AI model: {str(e)}")
            self.is_model_ready = False

            # Retry with a different model if we haven't reached max attempts
            if self.model_loading_attempts < self.max_model_loading_attempts:
                logger.info(f"Retrying with fallback model...")
                # Try a different model on each retry
                fallback_models = ["distilgpt2", "gpt2", "facebook/opt-125m"]
                next_model_index = min(self.model_loading_attempts, len(fallback_models) - 1)
                self.model_name = fallback_models[next_model_index]

                # Wait a moment before retrying
                import time
                time.sleep(2)

                # Try again with the new model
                self._load_local_model()

    def _get_model_config(self, model_name):
        """Get configuration for the specified model."""
        # Import model classes based on model type
        from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoModelForMaskedLM

        # Default configuration for causal language models
        default_config = {
            'model_class': AutoModelForCausalLM,
            'pipeline_task': 'text-generation',
            'max_length': 256,
            'temperature': 0.8,
            'top_p': 0.92,
            'use_fast_tokenizer': True,
            'needs_pad_token': True
        }

        # Model-specific configurations
        configs = {
            'distilgpt2': default_config,
            'gpt2': default_config,
            'gpt2-small': default_config,
            'facebook/opt-125m': default_config,
            'distilbert-base-uncased': {
                'model_class': AutoModelForMaskedLM,
                'pipeline_task': 'fill-mask',
                'max_length': 128,
                'temperature': 1.0,
                'top_p': 0.95,
                'use_fast_tokenizer': True,
                'needs_pad_token': True
            },
            'google/flan-t5-small': {
                'model_class': AutoModelForSeq2SeqLM,
                'pipeline_task': 'text2text-generation',
                'max_length': 128,
                'temperature': 0.9,
                'top_p': 0.95,
                'use_fast_tokenizer': True,
                'needs_pad_token': False
            }
        }

        # Return the configuration for the specified model, or the default if not found
        return configs.get(model_name, default_config)

    def _load_geography_questions(self) -> Dict:
        """Load geography questions from a dedicated JSON file."""
        geography_dict = {"easy": [], "medium": [], "hard": []}

        # Try to load from file
        geography_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'geography_questions.json'
        )

        if os.path.exists(geography_file):
            try:
                with open(geography_file, 'r') as f:
                    geography_dict = json.load(f)
                logger.info(f"Loaded geography questions from {geography_file}")
                return geography_dict
            except Exception as e:
                logger.error(f"Error loading geography questions: {str(e)}")

        # If file doesn't exist, use the geography questions from fallback
        if "Geography" in self.fallback_questions:
            return self.fallback_questions["Geography"]

        return geography_dict

    def _filter_sample_questions(self, questions: List[Dict]) -> List[Dict]:
        """Filter out sample questions based on patterns."""
        filtered_questions = []
        # Enhanced patterns to catch more sample questions
        sample_patterns = [
            r"sample\s+\w+\s+question",  # Matches "sample X question"
            r"sample\s+question",
            r"\w+\s+sample\s+question",  # Matches "X sample question"
            r"\w+\s+easy\s+question",    # Matches "X easy question"
            r"\w+\s+medium\s+question",  # Matches "X medium question"
            r"\w+\s+hard\s+question",    # Matches "X hard question"
            r"easy\s+question\s+#\d+",
            r"medium\s+question\s+#\d+",
            r"hard\s+question\s+#\d+",
            r"correct\s+answer\s+#\d+",
            r"wrong\s+answer\s+[abc]?\s+#\d+",  # Optional a/b/c
            r"incorrect\s+answer\s+[abc]?\s+#\d+",  # Optional a/b/c
            r"treasure\s+hunt",  # Specific to reported issue
            r"technology\s+sample",  # Specific to reported issue
            r"technology\s+easy\s+question",  # Specific to reported issue
            r"sample",  # Catch any remaining sample text
            r"#\d+"  # Catch any numbered questions/answers
        ]

        # Category-specific patterns
        category_patterns = {
            "Movies": [r"sample\s+movies", r"movies\s+sample", r"movie\s+sample", r"sample\s+movie"],
            "Technology": [r"technology\s+sample", r"sample\s+technology", r"tech\s+sample", r"sample\s+tech"],
            "Science": [r"science\s+sample", r"sample\s+science"],
            "Literacy": [r"literacy\s+sample", r"sample\s+literacy"]
        }

        for q in questions:
            is_sample = False
            question_text = q["question"].lower()
            category = q.get("category", "").lower()

            # Check if question matches any sample pattern
            for pattern in sample_patterns:
                if re.search(pattern, question_text, re.IGNORECASE):
                    is_sample = True
                    logger.debug(f"Filtered question matching pattern '{pattern}': {question_text}")
                    break

            # Check category-specific patterns
            if not is_sample and category in category_patterns:
                for pattern in category_patterns[category]:
                    if re.search(pattern, question_text, re.IGNORECASE):
                        is_sample = True
                        logger.debug(f"Filtered question matching category pattern '{pattern}': {question_text}")
                        break

            # Check if options contain sample patterns
            if not is_sample:
                for option in q["options"]:
                    option_text = option.lower()
                    for pattern in sample_patterns:
                        if re.search(pattern, option_text, re.IGNORECASE):
                            is_sample = True
                            logger.debug(f"Filtered option matching pattern '{pattern}': {option_text}")
                            break
                    if is_sample:
                        break

            # Additional check for suspicious questions
            if not is_sample:
                # Check for very short questions (likely placeholders)
                if len(question_text.split()) < 4:
                    is_sample = True
                    logger.debug(f"Filtered suspiciously short question: {question_text}")
                # Check for questions with no question mark
                elif not question_text.endswith('?') and not re.search(r'\?', question_text):
                    is_sample = True
                    logger.debug(f"Filtered question without question mark: {question_text}")

            if not is_sample:
                filtered_questions.append(q)

        # Log how many questions were filtered out
        filtered_count = len(questions) - len(filtered_questions)
        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} sample questions")

        return filtered_questions

    def generate_questions(self, category: str, difficulty: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions based on category and difficulty.

        This method implements a fallback mechanism:
        1. First tries to generate questions using the local AI model (if enabled)
        2. If that fails or times out, tries the Open Trivia DB API
        3. If that fails, uses the local JSON backup
        4. Filters out any sample questions
        """
        # Start with an empty list
        questions = []

        # Special handling for Geography category
        if category == "Geography":
            # Try to generate questions using local AI model first
            if not self.use_fallback and self.is_model_ready:
                try:
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            self._generate_ai_questions,
                            category,
                            difficulty,
                            num_questions
                        )
                        questions = future.result(timeout=self.max_wait_time)
                        if questions:
                            logger.info(f"Generated {len(questions)} questions using local AI model")
                except (TimeoutError, Exception) as e:
                    logger.warning(f"Local AI model timed out or failed: {str(e)}")
                    questions = []

        # If we don't have enough questions yet, try the API
        if len(questions) < num_questions:
            needed = num_questions - len(questions)
            api_questions = self._fetch_questions_from_api(category, difficulty, needed)
            questions.extend(api_questions)

            if api_questions:
                logger.info(f"Added {len(api_questions)} questions from Open Trivia DB API")

        # For Geography category, prioritize our high-quality geography questions
        if category == "Geography" and len(questions) < num_questions:
            needed = num_questions - len(questions)
            if difficulty in self.geography_questions and self.geography_questions[difficulty]:
                available = self.geography_questions[difficulty]
                # Ensure we don't select questions that are already in our list
                available_filtered = [q for q in available if q not in questions]
                if available_filtered:
                    # Take as many as needed, up to what's available
                    backup_questions = random.sample(available_filtered, min(needed, len(available_filtered)))
                    questions.extend(backup_questions)
                    logger.info(f"Added {len(backup_questions)} high-quality questions from Geography backup")

        # If we still don't have enough questions, use general fallback
        if len(questions) < num_questions:
            needed = num_questions - len(questions)
            fallback_questions = self._generate_fallback_questions(category, difficulty, needed)
            questions.extend(fallback_questions)
            logger.info(f"Added {len(fallback_questions)} questions from fallback system")

        # Filter out sample questions
        filtered_questions = self._filter_sample_questions(questions)
        logger.info(f"After filtering, {len(filtered_questions)} questions remain out of {len(questions)}")

        # If filtering removed too many questions, get more from fallback
        if len(filtered_questions) < num_questions:
            needed = num_questions - len(filtered_questions)
            logger.info(f"Need {needed} more questions after filtering")

            # Try to get more questions from fallback with extra to account for filtering
            more_questions = self._generate_fallback_questions(category, difficulty, needed * 3)  # Get 3x extra to account for filtering
            more_filtered = self._filter_sample_questions(more_questions)
            logger.info(f"Got {len(more_filtered)} additional filtered questions from fallback")

            # Add the filtered questions
            filtered_questions.extend(more_filtered[:needed])

            # If we still don't have enough, create guaranteed non-sample questions
            if len(filtered_questions) < num_questions:
                still_needed = num_questions - len(filtered_questions)
                logger.warning(f"Still need {still_needed} more questions. Creating guaranteed non-sample questions.")

                # Create guaranteed real questions for each category
                real_questions = self._create_guaranteed_questions(category, difficulty, still_needed)
                filtered_questions.extend(real_questions)
                logger.info(f"Added {len(real_questions)} guaranteed real questions")

        # Final check to ensure we have exactly the requested number
        return filtered_questions[:num_questions]

    def _fetch_questions_from_api(self, category: str, difficulty: str, num_questions: int) -> List[Dict]:
        """Fetch questions from the Open Trivia DB API."""
        try:
            # Map our categories to Open Trivia DB categories
            category_mapping = {
                "Science": 17,       # Science & Nature
                "History": 23,       # History
                "Geography": 22,     # Geography
                "Literature": 10,    # Books
                "Movies": 11,        # Film
                "Sports": 21,        # Sports
                "Technology": 18,    # Computers
                "Music": 12         # Music
            }

            # Convert difficulty to match API (already lowercase in our app)
            # Construct the API URL with parameters
            params = {
                "amount": num_questions,
                "type": "multiple"  # We want multiple choice questions
            }

            # Add category if we have a mapping
            if category in category_mapping:
                params["category"] = category_mapping[category]

            # Add difficulty
            if difficulty in ["easy", "medium", "hard"]:
                params["difficulty"] = difficulty

            # Build the URL
            url = f"{self.api_url}?{urllib.parse.urlencode(params)}"

            # Make the request
            logger.info(f"Fetching questions from {url}")
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())

            # Check if we got results
            if data["response_code"] == 0 and data["results"]:
                logger.info(f"Successfully fetched {len(data['results'])} questions from API")

                # Convert to our format
                questions = []
                for q in data["results"]:
                    # Decode HTML entities
                    question_text = html.unescape(q["question"])
                    correct_answer = html.unescape(q["correct_answer"])
                    incorrect_answers = [html.unescape(a) for a in q["incorrect_answers"]]

                    # Combine correct and incorrect answers
                    options = [correct_answer] + incorrect_answers
                    # Shuffle them
                    random.shuffle(options)

                    # Create our question format
                    question = {
                        "question": question_text,
                        "options": options,
                        "correct_answer": correct_answer,
                        "category": category,
                        "difficulty": difficulty
                    }
                    questions.append(question)
                return questions
            else:
                logger.warning(f"API returned response code {data['response_code']}")
                return []

        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error fetching questions from API: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching questions: {str(e)}")
            return []

    def _generate_fallback_questions(self, category: str, difficulty: str, num_questions: int) -> List[Dict]:
        """Get fallback questions for the given category and difficulty."""
        logger.info(f"Using fallback questions for {category} ({difficulty})")

        if category not in self.fallback_questions:
            # If category doesn't exist, use a random existing category
            available_cats = list(self.fallback_questions.keys())
            if available_cats:
                category = random.choice(available_cats)
            else:
                # Should never happen but just in case
                return self._create_fallback_questions(category, difficulty, num_questions)

        if difficulty not in self.fallback_questions[category]:
            # If difficulty doesn't exist, use a random existing difficulty
            available_diffs = list(self.fallback_questions[category].keys())
            if available_diffs:
                difficulty = random.choice(available_diffs)
            else:
                # Should never happen but just in case
                return self._create_fallback_questions(category, difficulty, num_questions)

        # Get fallback questions for the category/difficulty
        available_questions = self.fallback_questions[category][difficulty]

        # Select random questions up to the requested number
        if len(available_questions) <= num_questions:
            return available_questions
        else:
            return random.sample(available_questions, num_questions)

    def _generate_ai_questions(self, category: str, difficulty: str, num_questions: int) -> List[Dict]:
        """Generate questions using the local AI model with automatic retry mechanism."""
        if not self.is_model_ready or not self.generator:
            logger.warning("AI model not ready or generator not available")
            return []

        questions = []
        max_retries = 3  # Maximum number of retry attempts
        retry_delay = 1  # Delay between retries in seconds

        # Create a more detailed prompt for the AI model based on category and difficulty
        prompt_template = self._create_prompt_for_category(category, difficulty, num_questions)

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Generating AI questions (attempt {attempt}/{max_retries})")

                # Generate text using the model with adjusted parameters based on retry attempt
                temperature = 0.7 + (attempt * 0.1)  # Increase temperature with each retry
                result = self.generator(
                    prompt_template,
                    max_new_tokens=1024,
                    do_sample=True,
                    temperature=min(temperature, 1.0),  # Cap at 1.0
                    num_return_sequences=1
                )
                generated_text = result[0]['generated_text']

                # Extract JSON array from the generated text
                json_match = re.search(r'\[\s*\{.*?\}\s*\]', generated_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        generated_questions = json.loads(json_str)

                        # Validate and format each question
                        for q in generated_questions:
                            if all(key in q for key in ["question", "options", "correct_answer", "category", "difficulty"]):
                                # Ensure correct_answer is in options
                                if q["correct_answer"] not in q["options"]:
                                    q["options"][0] = q["correct_answer"]

                                # Ensure we have exactly 4 options
                                while len(q["options"]) < 4:
                                    q["options"].append(f"Option {len(q['options']) + 1}")

                                # Shuffle options
                                random.shuffle(q["options"])

                                questions.append(q)

                        # If we got at least one valid question, return them
                        if questions:
                            logger.info(f"Successfully generated {len(questions)} questions on attempt {attempt}")
                            return questions
                    except json.JSONDecodeError as json_err:
                        logger.error(f"JSON parsing error on attempt {attempt}: {str(json_err)}")
                        # Continue to next retry

                # If we reach here, either no JSON was found or no valid questions were generated
                logger.warning(f"No valid questions generated on attempt {attempt}")

                # Wait before retrying (except on last attempt)
                if attempt < max_retries:
                    import time
                    time.sleep(retry_delay)
                    # Adjust the prompt for next attempt
                    prompt_template = self._create_prompt_for_category(category, difficulty, num_questions, simplified=(attempt > 1))

            except Exception as e:
                logger.error(f"Error generating questions with AI model (attempt {attempt}): {str(e)}")
                # Wait before retrying (except on last attempt)
                if attempt < max_retries:
                    import time
                    time.sleep(retry_delay)

        logger.error(f"Failed to generate questions after {max_retries} attempts")
        return []  # Return empty list if all retries failed

    def _create_prompt_for_category(self, category: str, difficulty: str, num_questions: int, simplified: bool = False) -> str:
        """Create an appropriate prompt for the given category and difficulty."""
        if simplified:
            # Simplified prompt for retry attempts
            return f"""Generate {num_questions} multiple-choice {difficulty} questions about {category}.
[
  {{
    "question": "Question text",
    "options": ["Correct answer", "Wrong answer 1", "Wrong answer 2", "Wrong answer 3"],
    "correct_answer": "Correct answer",
    "category": "{category}",
    "difficulty": "{difficulty}"
  }}
]
"""

        # Category-specific prompts for first attempt
        if category == "Geography":
            return f"""Generate {num_questions} factual multiple-choice {difficulty} geography questions.
Each question should be about countries, capitals, landmarks, rivers, mountains, or other geographical features.
Format as a JSON array with each question having the following structure:
[
  {{
    "question": "What is the capital of France?",
    "options": ["Paris", "London", "Berlin", "Madrid"],
    "correct_answer": "Paris",
    "category": "Geography",
    "difficulty": "{difficulty}"
  }}
]
"""
        elif category == "History":
            return f"""Generate {num_questions} factual multiple-choice {difficulty} history questions.
Each question should be about historical events, figures, periods, or discoveries.
Format as a JSON array with each question having the following structure:
[
  {{
    "question": "Who was the first President of the United States?",
    "options": ["George Washington", "Thomas Jefferson", "Abraham Lincoln", "John Adams"],
    "correct_answer": "George Washington",
    "category": "History",
    "difficulty": "{difficulty}"
  }}
]
"""
        elif category == "Science":
            return f"""Generate {num_questions} factual multiple-choice {difficulty} science questions.
Each question should be about physics, chemistry, biology, astronomy, or other scientific fields.
Format as a JSON array with each question having the following structure:
[
  {{
    "question": "What is the chemical symbol for gold?",
    "options": ["Au", "Ag", "Fe", "Cu"],
    "correct_answer": "Au",
    "category": "Science",
    "difficulty": "{difficulty}"
  }}
]
"""
        else:
            # Default prompt for other categories
            return f"""Generate {num_questions} factual multiple-choice {difficulty} questions about {category}.
Format as a JSON array with each question having the following structure:
[
  {{
    "question": "Sample question about {category}?",
    "options": ["Correct answer", "Wrong answer 1", "Wrong answer 2", "Wrong answer 3"],
    "correct_answer": "Correct answer",
    "category": "{category}",
    "difficulty": "{difficulty}"
  }}
]
"""

    def is_ready(self) -> bool:
        """Check if the generator is ready to generate questions."""
        return self.is_model_ready

    def _create_guaranteed_questions(self, category: str, difficulty: str, count: int) -> List[Dict]:
        """Create guaranteed non-sample questions for a category.

        These are hardcoded high-quality questions that are guaranteed not to be sample questions.

        Args:
            category: The category to create questions for
            difficulty: The difficulty level
            count: Number of questions to create

        Returns:
            List of guaranteed non-sample questions
        """
        # Create a dictionary of guaranteed questions by category and difficulty
        guaranteed_questions = {
            "Science": {
                "easy": [
                    {
                        "question": "What is the largest planet in our solar system?",
                        "options": ["Jupiter", "Saturn", "Neptune", "Earth"],
                        "correct_answer": "Jupiter",
                        "category": "Science",
                        "difficulty": "easy"
                    },
                    {
                        "question": "What is the chemical formula for water?",
                        "options": ["H2O", "CO2", "O2", "NaCl"],
                        "correct_answer": "H2O",
                        "category": "Science",
                        "difficulty": "easy"
                    }
                ],
                "medium": [
                    {
                        "question": "What is the atomic number of carbon?",
                        "options": ["6", "12", "14", "8"],
                        "correct_answer": "6",
                        "category": "Science",
                        "difficulty": "medium"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the half-life of Carbon-14?",
                        "options": ["5,730 years", "1,600 years", "10,000 years", "3,200 years"],
                        "correct_answer": "5,730 years",
                        "category": "Science",
                        "difficulty": "hard"
                    }
                ]
            },
            "History": {
                "easy": [
                    {
                        "question": "Who was the first President of the United States?",
                        "options": ["George Washington", "Thomas Jefferson", "Abraham Lincoln", "John Adams"],
                        "correct_answer": "George Washington",
                        "category": "History",
                        "difficulty": "easy"
                    }
                ],
                "medium": [
                    {
                        "question": "In what year did World War II end?",
                        "options": ["1945", "1939", "1942", "1944"],
                        "correct_answer": "1945",
                        "category": "History",
                        "difficulty": "medium"
                    }
                ],
                "hard": [
                    {
                        "question": "Which treaty ended the War of 1812?",
                        "options": ["Treaty of Ghent", "Treaty of Paris", "Treaty of Versailles", "Treaty of Tordesillas"],
                        "correct_answer": "Treaty of Ghent",
                        "category": "History",
                        "difficulty": "hard"
                    }
                ]
            },
            "Geography": {
                "easy": [
                    {
                        "question": "What is the capital of France?",
                        "options": ["Paris", "London", "Berlin", "Madrid"],
                        "correct_answer": "Paris",
                        "category": "Geography",
                        "difficulty": "easy"
                    }
                ],
                "medium": [
                    {
                        "question": "Which river is the longest in the world?",
                        "options": ["Nile", "Amazon", "Mississippi", "Yangtze"],
                        "correct_answer": "Nile",
                        "category": "Geography",
                        "difficulty": "medium"
                    }
                ],
                "hard": [
                    {
                        "question": "Which country has the most natural lakes?",
                        "options": ["Canada", "United States", "Russia", "Finland"],
                        "correct_answer": "Canada",
                        "category": "Geography",
                        "difficulty": "hard"
                    }
                ]
            },
            "Literature": {
                "easy": [
                    {
                        "question": "Who wrote 'Romeo and Juliet'?",
                        "options": ["William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain"],
                        "correct_answer": "William Shakespeare",
                        "category": "Literature",
                        "difficulty": "easy"
                    }
                ],
                "medium": [
                    {
                        "question": "Which novel begins with the line 'It was the best of times, it was the worst of times'?",
                        "options": ["A Tale of Two Cities", "Great Expectations", "Oliver Twist", "David Copperfield"],
                        "correct_answer": "A Tale of Two Cities",
                        "category": "Literature",
                        "difficulty": "medium"
                    }
                ],
                "hard": [
                    {
                        "question": "Who wrote 'One Hundred Years of Solitude'?",
                        "options": ["Gabriel García Márquez", "Jorge Luis Borges", "Pablo Neruda", "Isabel Allende"],
                        "correct_answer": "Gabriel García Márquez",
                        "category": "Literature",
                        "difficulty": "hard"
                    }
                ]
            },
            "Movies": {
                "easy": [
                    {
                        "question": "Who directed the movie 'Titanic'?",
                        "options": ["James Cameron", "Steven Spielberg", "Christopher Nolan", "Martin Scorsese"],
                        "correct_answer": "James Cameron",
                        "category": "Movies",
                        "difficulty": "easy"
                    }
                ],
                "medium": [
                    {
                        "question": "Which actor played Iron Man in the Marvel Cinematic Universe?",
                        "options": ["Robert Downey Jr.", "Chris Evans", "Chris Hemsworth", "Mark Ruffalo"],
                        "correct_answer": "Robert Downey Jr.",
                        "category": "Movies",
                        "difficulty": "medium"
                    }
                ],
                "hard": [
                    {
                        "question": "Which film won the Academy Award for Best Picture in 1994?",
                        "options": ["Schindler's List", "The Fugitive", "The Piano", "The Remains of the Day"],
                        "correct_answer": "Schindler's List",
                        "category": "Movies",
                        "difficulty": "hard"
                    }
                ]
            },
            "Technology": {
                "easy": [
                    {
                        "question": "What does CPU stand for?",
                        "options": ["Central Processing Unit", "Computer Personal Unit", "Central Process Unit", "Central Processor Unit"],
                        "correct_answer": "Central Processing Unit",
                        "category": "Technology",
                        "difficulty": "easy"
                    }
                ],
                "medium": [
                    {
                        "question": "In what year was the first iPhone released?",
                        "options": ["2007", "2005", "2009", "2010"],
                        "correct_answer": "2007",
                        "category": "Technology",
                        "difficulty": "medium"
                    }
                ],
                "hard": [
                    {
                        "question": "Who is considered the father of modern computer science?",
                        "options": ["Alan Turing", "Bill Gates", "Steve Jobs", "Tim Berners-Lee"],
                        "correct_answer": "Alan Turing",
                        "category": "Technology",
                        "difficulty": "hard"
                    }
                ]
            }
        }

        # Default questions for any category not in our guaranteed list
        default_questions = [
            {
                "question": "What is the capital of Japan?",
                "options": ["Tokyo", "Beijing", "Seoul", "Bangkok"],
                "correct_answer": "Tokyo",
                "category": category,
                "difficulty": difficulty
            },
            {
                "question": "Who painted the Mona Lisa?",
                "options": ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Michelangelo"],
                "correct_answer": "Leonardo da Vinci",
                "category": category,
                "difficulty": difficulty
            },
            {
                "question": "What is the largest ocean on Earth?",
                "options": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"],
                "correct_answer": "Pacific Ocean",
                "category": category,
                "difficulty": difficulty
            }
        ]

        # Get questions for the requested category and difficulty
        result = []

        # Check if we have guaranteed questions for this category and difficulty
        if category in guaranteed_questions and difficulty in guaranteed_questions[category]:
            available = guaranteed_questions[category][difficulty]
            # Take as many as needed, up to what's available
            result.extend(available[:min(count, len(available))])

        # If we still need more questions, use default questions
        if len(result) < count:
            needed = count - len(result)
            # Cycle through default questions if we need more than are available
            for i in range(needed):
                question = default_questions[i % len(default_questions)].copy()
                # Ensure category and difficulty are set correctly
                question["category"] = category
                question["difficulty"] = difficulty
                result.append(question)

        return result

    def change_model(self, new_model_name: str) -> bool:
        """Change the AI model to a different one.

        Args:
            new_model_name (str): Name of the new model to use

        Returns:
            bool: True if model was changed successfully, False otherwise
        """
        if new_model_name == self.model_name:
            logger.info(f"Model is already set to {new_model_name}")
            return True

        logger.info(f"Changing AI model from {self.model_name} to {new_model_name}")

        # Reset model state
        self.is_model_ready = False
        self.model_name = new_model_name

        # Clean up existing model resources
        if self.local_model is not None:
            del self.local_model
            self.local_model = None

        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None

        if self.generator is not None:
            del self.generator
            self.generator = None

        # Force garbage collection to free up memory
        import gc
        gc.collect()

        if TRANSFORMERS_AVAILABLE and not self.use_fallback:
            # Reset attempt counter
            self.model_loading_attempts = 0

            # Load the new model
            try:
                self._load_local_model()
                return self.is_model_ready
            except Exception as e:
                logger.error(f"Error changing AI model: {str(e)}")
                return False
        else:
            # If we're in fallback mode, just update the model name
            self.is_model_ready = True
            return True