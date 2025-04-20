import tkinter as tk
import customtkinter as ctk
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SkipButtonTest')

# Import required modules
from ui.quiz_screen import QuizScreen
from core.question_manager import QuestionManager
from core.ai_generator import AIGenerator

class TestApp(ctk.CTk):
    """Test application for skip button functionality."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Skip Button Test")
        self.geometry("1000x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create AI generator and question manager
        self.ai_generator = AIGenerator()
        self.question_manager = QuestionManager(self.ai_generator)
        
        # Create test button
        self.test_button = ctk.CTkButton(
            self,
            text="Start Skip Button Test",
            command=self.start_test,
            width=200,
            height=50,
            font=("Helvetica", 16, "bold")
        )
        self.test_button.grid(row=0, column=0, padx=20, pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Click the button to start the test",
            font=("Helvetica", 14)
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=10)
        
    def start_test(self):
        """Start the skip button test."""
        self.test_button.grid_forget()
        self.status_label.grid_forget()
        
        # Create quiz screen with test parameters
        self.quiz_screen = QuizScreen(
            self,
            self.question_manager,
            "Science",  # Category
            "easy",     # Difficulty
            5,          # Number of questions
            30,         # Time per question
            self.end_test
        )
        self.quiz_screen.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        logger.info("Test started - Please test the skip button functionality")
        
    def end_test(self):
        """End the test and show results."""
        if hasattr(self, 'quiz_screen'):
            self.quiz_screen.destroy()
            
        # Show results
        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        results_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            results_frame,
            text="Skip Button Test Completed",
            font=("Helvetica", 24, "bold")
        ).grid(row=0, column=0, pady=20)
        
        ctk.CTkLabel(
            results_frame,
            text="The test has been completed. Please check the logs for any errors.",
            font=("Helvetica", 16)
        ).grid(row=1, column=0, pady=10)
        
        # Restart button
        ctk.CTkButton(
            results_frame,
            text="Restart Test",
            command=self.restart_test,
            width=200,
            height=50,
            font=("Helvetica", 16, "bold")
        ).grid(row=2, column=0, pady=30)
        
    def restart_test(self):
        """Restart the test."""
        for widget in self.winfo_children():
            widget.destroy()
            
        self.test_button = ctk.CTkButton(
            self,
            text="Start Skip Button Test",
            command=self.start_test,
            width=200,
            height=50,
            font=("Helvetica", 16, "bold")
        )
        self.test_button.grid(row=0, column=0, padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Click the button to start the test",
            font=("Helvetica", 14)
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=10)

if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
