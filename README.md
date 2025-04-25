# AI-Powered Quiz App

A modern, feature-rich quiz application built with Python and CustomTkinter, featuring local AI-powered question generation with category-specific question storage.

## Features

- Beautiful, modern UI with dark/light theme support
- AI-powered question generation using transformer models
- Category-specific JSON files for efficient question management
- Multiple categories and difficulty levels
- Timer-based quizzes
- Score tracking and performance summary
- Admin panel for managing questions
- Comprehensive statistics with question availability tracking
- Efficient performance with background model loading

## Requirements

- Python 3.10 or higher
- Required packages (install via `pip install -r requirements.txt`):
  - customtkinter>=5.2.0
  - transformers>=4.35.0
  - torch>=2.0.0
  - pillow>=10.0.0
  - tqdm>=4.66.0
  - numpy>=1.24.0
  - python-dotenv>=1.0.0

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd quiz-app
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) For enhanced AI performance:
   ```bash
   pip install accelerate
   ```
   This enables GPU acceleration (if available) and improves question generation speed.

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. Main Menu:
   - Select a category
   - Choose difficulty level
   - Set number of questions
   - Set time per question
   - Click "Start Quiz" to begin

3. During Quiz:
   - Read the question
   - Select your answer before time runs out
   - Use the Skip, Keep, or Sheep buttons for different actions
   - View your progress and current score
   - See final results at the end

4. Statistics:
   - View performance by category and difficulty
   - See available question counts for each category
   - Track your progress over time

5. Category Management:
   - Create custom categories
   - Generate questions for new categories
   - Manage existing categories

6. Admin Mode:
   - View all questions
   - Generate new questions for any category
   - Delete existing questions
   - Questions are automatically saved to category-specific files

## Project Structure

```
quiz_app/
├── main.py                    # Main entry point
├── migrate_questions.py       # Migration tool for category-specific files
├── ui/                        # UI components
│   ├── main_window.py         # Main application window
│   ├── quiz_screen.py         # Quiz interface
│   ├── admin_screen.py        # Admin panel
│   ├── statistics_screen.py   # Statistics and analytics
│   ├── settings_screen.py     # Application settings
│   └── category_manager.py    # Category management
├── core/                      # Core functionality
│   ├── question_manager.py    # Question management
│   ├── category_question_manager.py  # Category-specific question management
│   ├── ai_generator.py        # AI question generation
│   └── user_history.py        # User history tracking
├── data/                      # Data storage
│   ├── questions.json         # Main question database (legacy)
│   ├── *_questions.json       # Category-specific question files (e.g., geography_questions.json)
│   ├── fallback_questions.json # Fallback questions
│   ├── categories.json        # Custom categories configuration
│   └── backup/                # Automatic backups
├── assets/                    # UI assets
└── utils/                     # Utilities
    └── logger.py              # Logging configuration
```

## Features in Detail

### AI Question Generation
- Uses a fast, local AI model (distilgpt2 by default) for efficient question generation
- Supports multiple transformer models with automatic fallback mechanism
- Generates contextually relevant questions based on category and difficulty
- Category-specific prompts for higher quality questions
- No internet connection required after initial model download
- Robust fallback system with API and category-specific JSON files
- Enhanced performance with accelerate library (optional)
- Automatic retry mechanism with parameter adjustment for better results

### Question Management
- JSON-based storage for easy backup and portability
- Separate JSON files for each category to organize questions efficiently
- Automatic backup creation before modifications
- Category and difficulty-based organization
- Statistics tracking for available questions by category and difficulty

### Category-Specific Question Storage
- Each category maintains its own JSON file (e.g., geography_questions.json)
- AI-generated questions are automatically saved to the appropriate category file
- Questions are organized by difficulty level within each category file
- Efficient retrieval of questions by category without loading the entire database
- Visual statistics showing question counts for each category and difficulty
- Migration tool to convert legacy questions to the new category-based format

### User Interface
- Modern, responsive design using CustomTkinter
- Dark/light theme support
- Intuitive navigation and controls
- Real-time feedback and status updates

### Quiz Features
- Timer-based questions with automatic progression
- Score tracking and performance metrics
- Category and difficulty selection
- Configurable number of questions and time limits
- Skip, Keep, and Sheep buttons for enhanced interaction

### Migration Tool
- Utility to convert legacy questions to category-specific format
- Run `python migrate_questions.py` to convert existing questions
- Automatically organizes questions by category and difficulty
- Preserves all question data during migration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.