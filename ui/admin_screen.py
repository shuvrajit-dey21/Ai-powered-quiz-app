import customtkinter as ctk
import json
import os
import logging
from typing import Callable, Dict, List

logger = logging.getLogger('QuizApp')

class AdminScreen(ctk.CTkFrame):
    def __init__(self, master, question_manager, on_return: Callable):
        super().__init__(master)
        
        self.question_manager = question_manager
        self.on_return = on_return
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI elements
        self.create_header()
        self.create_tabs()
    
    def create_header(self):
        """Create the admin header."""
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="Admin Panel",
            font=("Helvetica", 28, "bold")
        )
        title.grid(row=0, column=0, pady=10)
        
        return_button = ctk.CTkButton(
            header,
            text="Return to Main Menu",
            command=self.on_return,
            width=200
        )
        return_button.grid(row=0, column=1, padx=20, pady=10)
    
    def create_tabs(self):
        """Create tabbed interface for admin panel."""
        tabview = ctk.CTkTabview(self)
        tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Add tabs
        tabview.add("Question Manager")
        tabview.add("Category Manager")
        tabview.add("Generate Questions")
        
        # Configure tab grids
        for tab in ["Question Manager", "Category Manager", "Generate Questions"]:
            tabview.tab(tab).grid_columnconfigure(0, weight=1)
            tabview.tab(tab).grid_rowconfigure(1, weight=1)
        
        # Populate tabs
        self.create_question_manager_tab(tabview.tab("Question Manager"))
        self.create_category_manager_tab(tabview.tab("Category Manager"))
        self.create_generate_tab(tabview.tab("Generate Questions"))
    
    def create_question_manager_tab(self, parent):
        """Create the question manager tab."""
        # Search frame
        search_frame = ctk.CTkFrame(parent)
        search_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="Search Questions:",
            font=("Helvetica", 14)
        ).grid(row=0, column=0, padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Enter search term"
        )
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_questions,
            width=100
        )
        search_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Questions list
        questions_frame = ctk.CTkScrollableFrame(parent)
        questions_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        questions_frame.grid_columnconfigure(0, weight=1)
        
        self.questions_container = questions_frame
        
        # Load questions
        self.load_questions()
    
    def create_category_manager_tab(self, parent):
        """Create the category manager tab."""
        # Category frame
        category_frame = ctk.CTkFrame(parent)
        category_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(
            category_frame,
            text="Add New Category:",
            font=("Helvetica", 14)
        ).grid(row=0, column=0, padx=10, pady=10)
        
        self.category_entry = ctk.CTkEntry(
            category_frame,
            width=200,
            placeholder_text="Enter category name"
        )
        self.category_entry.grid(row=0, column=1, padx=10, pady=10)
        
        add_button = ctk.CTkButton(
            category_frame,
            text="Add Category",
            command=self.add_category,
            width=120
        )
        add_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Categories list
        categories_frame = ctk.CTkScrollableFrame(parent)
        categories_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        categories_frame.grid_columnconfigure(0, weight=1)
        
        self.categories_container = categories_frame
        
        # Load categories
        self.load_categories()
    
    def create_generate_tab(self, parent):
        """Create the question generation tab."""
        # Configuration frame
        config_frame = ctk.CTkFrame(parent)
        config_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        config_frame.grid_columnconfigure((0,1), weight=1)
        
        # Category selection
        ctk.CTkLabel(
            config_frame,
            text="Category:",
            font=("Helvetica", 14)
        ).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.category_dropdown = ctk.CTkOptionMenu(
            config_frame,
            values=self.question_manager.get_categories()
        )
        self.category_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Difficulty selection
        ctk.CTkLabel(
            config_frame,
            text="Difficulty:",
            font=("Helvetica", 14)
        ).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        self.difficulty_dropdown = ctk.CTkOptionMenu(
            config_frame,
            values=self.question_manager.get_difficulties()
        )
        self.difficulty_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Number of questions
        ctk.CTkLabel(
            config_frame,
            text="Number of Questions:",
            font=("Helvetica", 14)
        ).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        self.num_questions = ctk.CTkEntry(
            config_frame,
            width=100,
            placeholder_text="Count"
        )
        self.num_questions.insert(0, "5")
        self.num_questions.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Generate button
        generate_button = ctk.CTkButton(
            config_frame,
            text="Generate Questions",
            command=self.generate_questions,
            width=200,
            height=40,
            font=("Helvetica", 14, "bold")
        )
        generate_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Status area
        self.status_frame = ctk.CTkScrollableFrame(parent)
        self.status_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to generate questions...",
            font=("Helvetica", 14),
            wraplength=500
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=10)
    
    def load_questions(self, search_term=None):
        """Load and display questions, optionally filtered by search term."""
        # Clear existing content
        for widget in self.questions_container.winfo_children():
            widget.destroy()
        
        # Get questions
        questions = self.question_manager.questions
        
        if search_term:
            search_term = search_term.lower()
            questions = [q for q in questions if 
                         search_term in q.get('question', '').lower() or 
                         search_term in q.get('category', '').lower() or
                         search_term in q.get('difficulty', '').lower()]
        
        # Display questions or message if none
        if questions:
            for i, question in enumerate(questions):
                self.create_question_item(i, question)
        else:
            ctk.CTkLabel(
                self.questions_container,
                text="No questions found",
                font=("Helvetica", 14)
            ).grid(row=0, column=0, padx=10, pady=10)
    
    def create_question_item(self, index, question):
        """Create a display item for a question."""
        frame = ctk.CTkFrame(self.questions_container)
        frame.grid(row=index, column=0, sticky="ew", padx=10, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        
        # Question info
        q_text = f"{question.get('question', '')} ({question.get('category', '')}, {question.get('difficulty', '')})"
        
        question_label = ctk.CTkLabel(
            frame,
            text=q_text,
            font=("Helvetica", 12),
            wraplength=500,
            justify="left"
        )
        question_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Delete button
        delete_button = ctk.CTkButton(
            frame,
            text="Delete",
            command=lambda q=question: self.delete_question(q),
            width=80,
            fg_color="red"
        )
        delete_button.grid(row=0, column=1, padx=10, pady=5)
    
    def search_questions(self):
        """Search questions based on input."""
        search_term = self.search_entry.get().strip()
        self.load_questions(search_term)
    
    def delete_question(self, question):
        """Delete a question and reload the list."""
        try:
            self.question_manager.remove_question(question)
            self.load_questions()
        except Exception as e:
            logger.error(f"Error deleting question: {str(e)}")
            self.show_error("Failed to delete question")
    
    def load_categories(self):
        """Load and display categories."""
        # Clear existing content
        for widget in self.categories_container.winfo_children():
            widget.destroy()
        
        # Get categories
        categories = self.question_manager.get_categories()
        
        # Display categories or message if none
        if categories:
            for i, category in enumerate(categories):
                frame = ctk.CTkFrame(self.categories_container)
                frame.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
                
                category_label = ctk.CTkLabel(
                    frame,
                    text=category,
                    font=("Helvetica", 14)
                )
                category_label.grid(row=0, column=0, padx=20, pady=10)
        else:
            ctk.CTkLabel(
                self.categories_container,
                text="No categories found",
                font=("Helvetica", 14)
            ).grid(row=0, column=0, padx=10, pady=10)
    
    def add_category(self):
        """Add a new category."""
        category = self.category_entry.get().strip()
        
        if not category:
            self.show_error("Please enter a category name")
            return
        
        # Create a mock question to add the category
        mock_question = {
            "question": f"Example question for {category}",
            "options": ["Correct", "Wrong 1", "Wrong 2", "Wrong 3"],
            "correct_answer": "Correct",
            "category": category,
            "difficulty": "medium"
        }
        
        try:
            self.question_manager.add_question(mock_question)
            self.category_entry.delete(0, 'end')
            self.load_categories()
            
            # Update category dropdown
            self.category_dropdown.configure(
                values=self.question_manager.get_categories()
            )
        except Exception as e:
            logger.error(f"Error adding category: {str(e)}")
            self.show_error("Failed to add category")
    
    def generate_questions(self):
        """Generate questions with the specified settings."""
        try:
            category = self.category_dropdown.get()
            difficulty = self.difficulty_dropdown.get()
            
            try:
                num_questions = int(self.num_questions.get().strip())
                if num_questions <= 0:
                    raise ValueError("Number must be positive")
            except ValueError:
                self.show_error("Please enter a valid number of questions")
                return
            
            # Update status
            self.status_label.configure(
                text=f"Generating {num_questions} {difficulty} questions for {category}..."
            )
            
            # Generate questions (this might take time)
            self.after(100, lambda: self._do_generate_questions(category, difficulty, num_questions))
            
        except Exception as e:
            logger.error(f"Error in generate_questions: {str(e)}")
            self.show_error("An error occurred during question generation")
    
    def _do_generate_questions(self, category, difficulty, num_questions):
        """Do the actual question generation (potentially time-consuming)."""
        try:
            # Generate questions
            questions = self.question_manager.regenerate_questions(category, difficulty, num_questions)
            
            # Update status
            self.status_label.configure(
                text=f"Successfully generated {len(questions)} {difficulty} questions for {category}!"
            )
            
            # Reload questions list
            self.load_questions()
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            self.status_label.configure(
                text=f"Error: {str(e)}"
            )
    
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