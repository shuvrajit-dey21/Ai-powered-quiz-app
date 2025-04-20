import customtkinter as ctk
import json
import os
from datetime import datetime
import logging
from typing import Callable, List, Dict
from PIL import Image
import random

logger = logging.getLogger('QuizApp')

class QuizScreen(ctk.CTkFrame):
    def __init__(
        self,
        master,
        question_manager,
        category: str,
        difficulty: str,
        num_questions: int,
        time_per_question: int,
        on_complete: Callable
    ):
        super().__init__(master)

        self.question_manager = question_manager
        self.category = category
        self.difficulty = difficulty
        self.num_questions = num_questions
        self.time_per_question = time_per_question
        self.on_complete = on_complete

        # Quiz state
        self.current_question = 0
        self.score = 0
        self.questions = []
        self.answers = []
        self.time_left = time_per_question
        self.quiz_active = False

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI elements
        self.create_header()
        self.create_question_area()
        self.create_footer()

        # Start quiz
        self.start_quiz()

    def create_header(self):
        """Create the quiz header with progress and timer."""
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(1, weight=1)

        # Category and difficulty
        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            info_frame,
            text=f"Category: {self.category}",
            font=("Helvetica", 14, "bold")
        ).grid(row=0, column=0, padx=10)

        difficulty_colors = {
            "easy": "green",
            "medium": "orange",
            "hard": "red"
        }

        ctk.CTkLabel(
            info_frame,
            text=f"Difficulty: {self.difficulty.capitalize()}",
            font=("Helvetica", 14, "bold"),
            text_color=difficulty_colors[self.difficulty]
        ).grid(row=0, column=1, padx=10)

        # Progress
        self.progress_label = ctk.CTkLabel(
            header,
            text=f"Question 1/{self.num_questions}",
            font=("Helvetica", 14)
        )
        self.progress_label.grid(row=0, column=1)

        # Timer
        self.timer_label = ctk.CTkLabel(
            header,
            text=f"Time: {self.time_per_question}s",
            font=("Helvetica", 14)
        )
        self.timer_label.grid(row=0, column=2, padx=20)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(header)
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        self.progress_bar.set(0)

    def create_question_area(self):
        """Create the main question area."""
        self.question_frame = ctk.CTkFrame(self)
        self.question_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.question_frame.grid_columnconfigure(0, weight=1)
        self.question_frame.grid_rowconfigure(2, weight=1)  # Changed to 2 to accommodate feedback label

        # Question text with improved styling
        self.question_label = ctk.CTkLabel(
            self.question_frame,
            text="Loading question...",
            font=("Helvetica", 20, "bold"),  # Increased font size and made bold
            wraplength=700,  # Increased wraplength
            corner_radius=10,
            fg_color=("#f0f0f0", "#2d2d2d"),  # Light/dark mode background
            text_color=("#333333", "#ffffff")  # Light/dark mode text color
        )
        self.question_label.grid(row=0, column=0, pady=20, sticky="ew", padx=20)

        # Feedback label for correct/incorrect answers
        self.feedback_label = ctk.CTkLabel(
            self.question_frame,
            text="",
            font=("Helvetica", 16, "bold"),
            text_color="white",
            height=0  # Initially hidden
        )
        self.feedback_label.grid(row=1, column=0, pady=(0, 10), sticky="ew")

        # Answer buttons frame with improved styling
        self.answers_frame = ctk.CTkFrame(self.question_frame, fg_color="transparent")
        self.answers_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.answers_frame.grid_columnconfigure(0, weight=1)

        # Create answer buttons (will be populated later)
        self.answer_buttons = []

    def create_footer(self):
        """Create the quiz footer with navigation buttons."""
        footer = ctk.CTkFrame(self)
        footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        footer.grid_columnconfigure((0,1,2), weight=1)

        # Previous button with improved styling
        self.prev_button = ctk.CTkButton(
            footer,
            text="← Previous",
            command=self.previous_question,
            width=150,
            height=45,
            corner_radius=10,
            font=("Helvetica", 14, "bold"),
            fg_color="#6c757d",  # Gray
            hover_color="#5a6268",  # Darker gray
            state="disabled",
            border_width=0,
            text_color="white"
        )
        self.prev_button.grid(row=0, column=0, padx=15)

        # Skip button with improved styling
        self.skip_button = ctk.CTkButton(
            footer,
            text="Skip →",
            command=self.skip_question,
            width=150,
            height=45,
            corner_radius=10,
            font=("Helvetica", 14, "bold"),
            fg_color="#17a2b8",  # Info blue
            hover_color="#138496",  # Darker blue
            border_width=0,
            text_color="white"
        )
        self.skip_button.grid(row=0, column=1, padx=15)

        # Submit button with improved styling
        self.submit_button = ctk.CTkButton(
            footer,
            text="Submit Quiz",
            command=self.submit_quiz,
            width=150,
            height=45,
            corner_radius=10,
            font=("Helvetica", 14, "bold"),
            fg_color="#28a745",  # Green
            hover_color="#218838",  # Darker green
            state="disabled",
            border_width=0,
            text_color="white"
        )
        self.submit_button.grid(row=0, column=2, padx=15)

    def start_quiz(self):
        """Start the quiz by loading questions and initializing the timer."""
        try:
            # Show loading indicator
            self.show_loading_indicator()

            # Use a separate thread to load questions to avoid UI freezing
            import threading
            threading.Thread(target=self._load_questions_thread, daemon=True).start()

        except Exception as e:
            logger.error(f"Error starting quiz: {str(e)}")
            self.show_error("Failed to load questions")

    def show_loading_indicator(self):
        """Show a loading indicator while questions are being generated."""
        # Clear any existing content in the answers frame
        for widget in self.answers_frame.winfo_children():
            widget.destroy()

        # Update question text
        self.question_label.configure(text="Generating questions...")

        # Add a progress bar
        self.loading_progress = ctk.CTkProgressBar(
            self.answers_frame,
            width=400,
            mode="indeterminate"
        )
        self.loading_progress.grid(row=0, column=0, pady=20)
        self.loading_progress.start()

        # Add a message
        self.loading_label = ctk.CTkLabel(
            self.answers_frame,
            text="Please wait while we generate your questions...",
            font=("Helvetica", 14)
        )
        self.loading_label.grid(row=1, column=0, pady=10)

        # Add AI model status
        ai_ready = self.question_manager.is_ai_ready()
        status_text = "AI Model: Ready ✓" if ai_ready else "AI Model: Loading..."
        status_color = "green" if ai_ready else "orange"

        self.ai_status_label = ctk.CTkLabel(
            self.answers_frame,
            text=status_text,
            font=("Helvetica", 12),
            text_color=status_color
        )
        self.ai_status_label.grid(row=2, column=0, pady=5)

        # Disable navigation buttons during loading
        self.prev_button.configure(state="disabled")
        self.skip_button.configure(state="disabled")
        self.submit_button.configure(state="disabled")

    def _load_questions_thread(self):
        """Load questions in a separate thread to avoid UI freezing."""
        try:
            # Get questions from question manager
            questions = self.question_manager.get_questions(
                self.category,
                self.difficulty,
                self.num_questions
            )

            # Update UI in the main thread
            self.after(0, lambda: self._questions_loaded(questions))

        except Exception as e:
            logger.error(f"Error loading questions: {str(e)}")
            self.after(0, lambda: self.show_error("Failed to load questions"))

    def _questions_loaded(self, questions):
        """Handle loaded questions and start the quiz."""
        # Store questions
        self.questions = questions

        # Initialize answers list
        self.answers = [None] * len(self.questions)

        # Remove loading indicator
        if hasattr(self, 'loading_progress'):
            self.loading_progress.destroy()
        if hasattr(self, 'loading_label'):
            self.loading_label.destroy()
        if hasattr(self, 'ai_status_label'):
            self.ai_status_label.destroy()

        # Show first question
        self.show_question(0)

        # Start timer
        self.quiz_active = True
        self.update_timer()

    def show_question(self, index: int):
        """Display the question at the given index."""
        if 0 <= index < len(self.questions):
            # Temporarily disable skip button during transition to prevent double-clicks
            self.skip_button.configure(state="disabled")

            self.current_question = index
            question = self.questions[index]

            # Update question text
            self.question_label.configure(text=question["question"])

            # Update progress
            self.progress_label.configure(text=f"Question {index + 1}/{self.num_questions}")
            self.progress_bar.set((index + 1) / self.num_questions)

            # Clear old answer buttons
            for btn in self.answer_buttons:
                btn.destroy()
            self.answer_buttons.clear()

            # Create new answer buttons with improved styling
            options = question["options"]
            random.shuffle(options)  # Randomize order

            # Reset feedback label
            self.feedback_label.configure(text="", height=0)

            for i, option in enumerate(options):
                # Create a container frame for each button to enable hover effects
                btn_container = ctk.CTkFrame(self.answers_frame, fg_color="transparent")
                btn_container.grid(row=i, column=0, pady=8, sticky="ew")
                btn_container.grid_columnconfigure(0, weight=1)

                # Create the button with improved styling
                btn = ctk.CTkButton(
                    btn_container,
                    text=option,
                    command=lambda o=option: self.select_answer(o),
                    width=450,  # Increased width
                    height=60,   # Increased height
                    font=("Helvetica", 16),  # Larger font
                    fg_color="#3a7ca5" if self.answers[index] != option else "#28a745",  # Blue for unselected, green for selected
                    hover_color="#2c6384" if self.answers[index] != option else "#218838",  # Darker blue/green on hover
                    corner_radius=10,  # Rounded corners
                    border_width=0,
                    text_color="white"
                )
                btn.grid(row=0, column=0, sticky="ew")
                self.answer_buttons.append(btn)

            # Update navigation buttons
            self.prev_button.configure(state="normal" if index > 0 else "disabled")
            self.skip_button.configure(text="Skip →" if index < len(self.questions) - 1 else "Finish")
            self.submit_button.configure(state="normal" if all(a is not None for a in self.answers) else "disabled")

            # Re-enable skip button after a short delay to prevent accidental double-clicks
            self.after(300, lambda: self.skip_button.configure(state="normal"))

    def select_answer(self, answer: str):
        """Handle answer selection with visual feedback."""
        self.answers[self.current_question] = answer
        question = self.questions[self.current_question]
        correct_answer_key = "correct_answer" if "correct_answer" in question else "answer"
        correct_answer = question[correct_answer_key]
        is_correct = (answer == correct_answer)

        # Update button colors with visual feedback
        for btn in self.answer_buttons:
            btn_text = btn.cget("text")
            if btn_text == answer:
                # Selected answer
                if is_correct:
                    # Correct answer - green
                    btn.configure(fg_color="#28a745", hover_color="#218838", border_width=2, border_color="white")
                else:
                    # Incorrect answer - red
                    btn.configure(fg_color="#dc3545", hover_color="#c82333", border_width=2, border_color="white")
            elif btn_text == correct_answer and not is_correct:
                # Show correct answer when user selects wrong answer
                btn.configure(fg_color="#28a745", hover_color="#218838", border_width=2, border_color="white")
            else:
                # Unselected answers
                btn.configure(fg_color="gray40", hover_color="gray30", border_width=0)

        # Enable submit if all questions answered
        if all(a is not None for a in self.answers):
            self.submit_button.configure(state="normal")

        # Show feedback message
        self.show_answer_feedback(is_correct)

        # Auto-advance to next question if not last
        if self.current_question < len(self.questions) - 1:
            self.after(1500, lambda: self.show_question(self.current_question + 1))

    def show_answer_feedback(self, is_correct: bool):
        """Show feedback message for correct/incorrect answers."""
        if is_correct:
            self.feedback_label.configure(
                text="✓ Correct!",
                fg_color="#28a745",
                height=40,
                corner_radius=8
            )
        else:
            self.feedback_label.configure(
                text="✗ Incorrect",
                fg_color="#dc3545",
                height=40,
                corner_radius=8
            )

    def previous_question(self):
        """Show the previous question."""
        if self.current_question > 0:
            self.show_question(self.current_question - 1)

    def skip_question(self):
        """Skip to the next question or finish quiz.

        This method ensures the skip button works correctly by handling edge cases
        and ensuring the UI state is updated properly.
        """
        try:
            # Make sure we have questions loaded
            if not self.questions:
                logger.warning("Skip button pressed but no questions loaded")
                return

            # Check if we're on the last question
            if self.current_question < len(self.questions) - 1:
                # Move to the next question
                next_question = self.current_question + 1
                logger.info(f"Skipping from question {self.current_question + 1} to {next_question + 1}")

                # Force update the UI to show the next question
                self.after(0, lambda: self.show_question(next_question))

                # Re-enable the skip button after a short delay
                self.after(100, lambda: self.skip_button.configure(state="normal"))
            else:
                # We're on the last question, so finish the quiz
                logger.info("Skip button pressed on last question, submitting quiz")
                self.after(0, lambda: self.submit_quiz())
        except Exception as e:
            logger.error(f"Error in skip_question: {str(e)}")
            # Try to recover by showing an error and staying on current question
            self.show_error("Error skipping question. Please try again.")
            # Re-enable the skip button
            self.after(100, lambda: self.skip_button.configure(state="normal"))

    def update_timer(self):
        """Update the timer display."""
        if self.quiz_active and self.time_left > 0:
            self.time_left -= 1
            self.timer_label.configure(text=f"Time: {self.time_left}s")

            # Update color based on time left
            if self.time_left <= 10:
                self.timer_label.configure(text_color="red")

            self.after(1000, self.update_timer)
        elif self.time_left <= 0:
            self.submit_quiz()

    def submit_quiz(self):
        """Submit the quiz and show results."""
        self.quiz_active = False

        # Calculate score
        correct_answers = 0
        for i, question in enumerate(self.questions):
            correct_answer_key = "correct_answer" if "correct_answer" in question else "answer"
            if self.answers[i] == question[correct_answer_key]:
                correct_answers += 1

        self.score = (correct_answers / len(self.questions)) * 100

        # Save results
        self.save_results(correct_answers)

        # Show results dialog
        self.show_results(correct_answers)

    def save_results(self, correct_answers: int):
        """Save quiz results to statistics file."""
        try:
            stats_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'stats.json'
            )

            # Load existing stats
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            else:
                stats = {
                    "total_quizzes": 0,
                    "total_questions": 0,
                    "correct_answers": 0,
                    "average_score": 0,
                    "best_category": "None",
                    "best_score": 0,
                    "categories": {},
                    "difficulties": {
                        "easy": {"total": 0, "correct": 0},
                        "medium": {"total": 0, "correct": 0},
                        "hard": {"total": 0, "correct": 0}
                    },
                    "history": []
                }

            # Update general stats
            stats["total_quizzes"] += 1
            stats["total_questions"] += len(self.questions)
            stats["correct_answers"] += correct_answers
            stats["average_score"] = (
                stats["correct_answers"] / stats["total_questions"]
            ) * 100

            # Update category stats
            if self.category not in stats["categories"]:
                stats["categories"][self.category] = {
                    "total": 0,
                    "correct": 0,
                    "best_score": 0
                }

            cat_stats = stats["categories"][self.category]
            cat_stats["total"] += len(self.questions)
            cat_stats["correct"] += correct_answers
            cat_stats["best_score"] = max(cat_stats["best_score"], self.score)

            # Update best category
            if self.score > stats["best_score"]:
                stats["best_score"] = self.score
                stats["best_category"] = self.category

            # Update difficulty stats
            diff_stats = stats["difficulties"][self.difficulty]
            diff_stats["total"] += len(self.questions)
            diff_stats["correct"] += correct_answers

            # Add to history
            stats["history"].append({
                "date": datetime.now().isoformat(),
                "category": self.category,
                "difficulty": self.difficulty,
                "score": correct_answers,
                "total": len(self.questions),
                "percentage": self.score
            })

            # Save updated stats
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=4)

        except Exception as e:
            logger.error(f"Error saving quiz results: {str(e)}")

    def show_results(self, correct_answers: int):
        """Show the quiz results dialog."""
        # Create results window
        results = ctk.CTkToplevel(self)
        results.title("Quiz Results")
        results.geometry("500x400")
        results.grab_set()  # Make modal

        # Configure grid
        results.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            results,
            text="Quiz Complete!",
            font=("Helvetica", 24, "bold")
        ).grid(row=0, column=0, pady=20)

        # Results frame
        results_frame = ctk.CTkFrame(results)
        results_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Display results
        metrics = [
            ("Category", self.category),
            ("Difficulty", self.difficulty.capitalize()),
            ("Score", f"{correct_answers}/{len(self.questions)}"),
            ("Percentage", f"{self.score:.1f}%"),
            ("Time Taken", f"{self.time_per_question - self.time_left}s")
        ]

        for i, (label, value) in enumerate(metrics):
            ctk.CTkLabel(
                results_frame,
                text=label,
                font=("Helvetica", 14)
            ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            ctk.CTkLabel(
                results_frame,
                text=str(value),
                font=("Helvetica", 14, "bold")
            ).grid(row=i, column=1, padx=10, pady=5, sticky="e")

        # Performance message
        message = "Excellent!" if self.score >= 80 else \
                 "Good job!" if self.score >= 60 else \
                 "Keep practicing!"

        ctk.CTkLabel(
            results,
            text=message,
            font=("Helvetica", 18, "bold"),
            text_color="green" if self.score >= 80 else "orange" if self.score >= 60 else "red"
        ).grid(row=2, column=0, pady=20)

        # Close button
        ctk.CTkButton(
            results,
            text="Continue",
            command=lambda: [results.destroy(), self.on_complete()],
            width=200
        ).grid(row=3, column=0, pady=20)

    def show_error(self, message: str):
        """Show error message in a popup."""
        try:
            dialog = ctk.CTkInputDialog(
                text=message,
                title="Error",
                button_text="OK"
            )
            dialog.geometry("300x150")
            dialog._input_entry.grid_remove()
            dialog.wait_window()
        except Exception as e:
            # Fallback in case CTkInputDialog doesn't support button_text
            logger.error(f"Dialog error: {str(e)}")
            messagebox = ctk.CTkToplevel(self)
            messagebox.title("Error")
            messagebox.geometry("300x150")
            messagebox.grab_set()

            ctk.CTkLabel(
                messagebox,
                text=message,
                wraplength=250
            ).pack(pady=20)

            ctk.CTkButton(
                messagebox,
                text="OK",
                command=messagebox.destroy
            ).pack(pady=10)

            messagebox.wait_window()