import os
import sys
import customtkinter as ctk
from ui.main_window import MainWindow
from core.question_manager import QuestionManager
from core.ai_generator import AIGenerator
from utils.logger import setup_logger

def setup_environment():
    """Setup the application environment and create necessary directories."""
    dirs = ['data', 'data/backup', 'assets', 'logs']
    for dir_path in dirs:
        os.makedirs(os.path.join(os.path.dirname(__file__), dir_path), exist_ok=True)

def main():
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Quiz App")

    # Setup environment
    setup_environment()

    # Initialize the AI model and question manager
    # Configuration for AI model
    use_local_ai = True  # Enabled by default for better user experience

    # Select which model to use (can be changed to try different models)
    # Supported models: 'distilgpt2', 'gpt2', 'facebook/opt-125m', 'distilbert-base-uncased', 'google/flan-t5-small'
    selected_model = 'distilgpt2'  # Default model - small and fast

    # Check for environment variable to override model selection
    import os
    env_model = os.environ.get('QUIZ_APP_MODEL')
    if env_model:
        selected_model = env_model
        logger.info(f"Using model from environment variable: {selected_model}")

    try:
        # Check if transformers library is available
        from transformers import __version__ as transformers_version
        logger.info(f"Transformers library found (version {transformers_version})")

        # Check if accelerate library is available
        try:
            import accelerate
            logger.info(f"Accelerate library found (version {accelerate.__version__})")
        except ImportError:
            logger.warning("Accelerate library not found. For better performance, install with: pip install accelerate")

        if use_local_ai:
            # Enable local AI model with selected model
            logger.info(f"Enabling local AI model for question generation using model: {selected_model}")
            ai_generator = AIGenerator(use_fallback=False, model_name=selected_model)
        else:
            logger.info("Using fallback mode for faster development (local AI model available but disabled)")
            ai_generator = AIGenerator(use_fallback=True)
    except ImportError:
        logger.warning("Transformers library not available. Using fallback mode.")
        # Use fallback mode if transformers is not available
        ai_generator = AIGenerator(use_fallback=True)

    question_manager = QuestionManager(ai_generator)

    # Setup the GUI
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = MainWindow(question_manager)
    app.mainloop()

if __name__ == "__main__":
    main()