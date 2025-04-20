import customtkinter as ctk
import logging
from typing import Callable, List
import random

logger = logging.getLogger('QuizApp')

class CategoryManagerScreen(ctk.CTkFrame):
    """Screen for managing quiz categories."""
    
    def __init__(self, master, question_manager, on_back: Callable):
        """Initialize the category manager screen.
        
        Args:
            master: The parent widget
            question_manager: The question manager instance
            on_back: Callback function to return to previous screen
        """
        super().__init__(master)
        
        self.question_manager = question_manager
        self.on_back = on_back
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Create UI elements
        self.create_header()
        self.create_add_category_section()
        self.create_categories_list()
        
        # Load categories
        self.load_categories()
        
    def create_header(self):
        """Create the header with title and back button."""
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(
            header,
            text="Category Manager",
            font=("Helvetica", 24, "bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Back button
        back_button = ctk.CTkButton(
            header,
            text="← Back",
            command=self.on_back,
            width=100
        )
        back_button.grid(row=0, column=1, padx=10)
        
    def create_add_category_section(self):
        """Create the section for adding new categories."""
        add_frame = ctk.CTkFrame(self)
        add_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        add_frame.grid_columnconfigure(1, weight=1)
        
        # Label
        ctk.CTkLabel(
            add_frame,
            text="Add New Category:",
            font=("Helvetica", 16)
        ).grid(row=0, column=0, padx=10, pady=15)
        
        # Entry
        self.category_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="Enter category name",
            width=300
        )
        self.category_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        # Add button
        add_button = ctk.CTkButton(
            add_frame,
            text="Add Category",
            command=self.add_category,
            width=150
        )
        add_button.grid(row=0, column=2, padx=10, pady=15)
        
    def create_categories_list(self):
        """Create the list of existing categories."""
        # Container frame
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        ctk.CTkLabel(
            list_frame,
            text="Existing Categories",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # Scrollable list
        self.categories_container = ctk.CTkScrollableFrame(list_frame)
        self.categories_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.categories_container.grid_columnconfigure(0, weight=1)
        
    def load_categories(self):
        """Load and display existing categories."""
        # Clear existing items
        for widget in self.categories_container.winfo_children():
            widget.destroy()
            
        # Get categories
        categories = self.question_manager.get_categories()
        default_categories = self.question_manager.default_categories
        
        # Display categories
        for i, category in enumerate(sorted(categories)):
            # Create frame for category item
            is_default = category in default_categories
            self.create_category_item(i, category, is_default)
            
    def create_category_item(self, index: int, category: str, is_default: bool):
        """Create a display item for a category.
        
        Args:
            index: The row index
            category: The category name
            is_default: Whether this is a default category
        """
        # Generate a random color for custom categories
        colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c", "#d35400", "#c0392b"]
        color = colors[index % len(colors)] if not is_default else "#7f8c8d"
        
        # Create frame
        frame = ctk.CTkFrame(self.categories_container, fg_color=color, corner_radius=8)
        frame.grid(row=index, column=0, sticky="ew", padx=5, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        
        # Category name
        name_label = ctk.CTkLabel(
            frame,
            text=category,
            font=("Helvetica", 16, "bold"),
            text_color="white"
        )
        name_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Default badge
        if is_default:
            badge = ctk.CTkLabel(
                frame,
                text="Default",
                font=("Helvetica", 12),
                fg_color="#34495e",
                corner_radius=5,
                text_color="white",
                width=80,
                height=25
            )
            badge.grid(row=0, column=1, padx=10)
            
        # Delete button (only for custom categories)
        if not is_default:
            delete_button = ctk.CTkButton(
                frame,
                text="Delete",
                command=lambda c=category: self.delete_category(c),
                fg_color="#e74c3c",
                hover_color="#c0392b",
                width=80,
                height=30
            )
            delete_button.grid(row=0, column=2, padx=10, pady=10)
            
    def add_category(self):
        """Add a new category."""
        category_name = self.category_entry.get().strip()
        
        if not category_name:
            self.show_message("Please enter a category name", "error")
            return
            
        # Add category
        success = self.question_manager.add_category(category_name)
        
        if success:
            self.show_message(f"Category '{category_name}' added successfully", "success")
            self.category_entry.delete(0, 'end')  # Clear entry
            self.load_categories()  # Refresh list
        else:
            self.show_message(f"Category '{category_name}' already exists", "warning")
            
    def delete_category(self, category: str):
        """Delete a category.
        
        Args:
            category: The category to delete
        """
        # Confirm deletion
        confirm = ctk.CTkInputDialog(
            text=f"Are you sure you want to delete the category '{category}'?\nThis will not delete existing questions.",
            title="Confirm Deletion"
        )
        result = confirm.get_input()
        
        if result and result.lower() in ["yes", "y"]:
            # Remove from categories
            if category in self.question_manager.categories:
                self.question_manager.categories.remove(category)
                self.question_manager.save_categories()
                self.show_message(f"Category '{category}' deleted", "success")
                self.load_categories()  # Refresh list
                
    def show_message(self, message: str, message_type: str = "info"):
        """Show a message to the user.
        
        Args:
            message: The message to show
            message_type: The type of message (info, success, warning, error)
        """
        # Colors for different message types
        colors = {
            "info": "#3498db",
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
        
        # Create message dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Message")
        dialog.geometry("400x150")
        dialog.grab_set()  # Make modal
        
        # Configure grid
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
        
        # Message frame
        frame = ctk.CTkFrame(dialog)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        
        # Message label
        ctk.CTkLabel(
            frame,
            text=message,
            font=("Helvetica", 14),
            wraplength=300
        ).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # OK button
        ctk.CTkButton(
            frame,
            text="OK",
            command=dialog.destroy,
            fg_color=colors.get(message_type, colors["info"]),
            width=100
        ).grid(row=1, column=0, pady=(10, 20))
