import customtkinter as ctk
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger('QuizApp')

class StatisticsScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Store reference to master (MainWindow)
        self.master = master

        # Load stats
        self.stats = self.load_statistics()

        # Get question counts if available
        self.question_counts = {}
        if hasattr(self.master, 'question_manager'):
            self.question_counts = self.master.question_manager.get_category_question_counts()

        # Create UI elements
        self.create_header()
        self.create_tabs()

    def load_statistics(self) -> Dict:
        """Load statistics from JSON file."""
        try:
            stats_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'stats.json'
            )

            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    return json.load(f)
            else:
                logger.info("No statistics file found")
        except Exception as e:
            logger.error(f"Error loading statistics: {str(e)}")

        # Return default stats if file doesn't exist or has error
        return {
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

    def create_header(self):
        """Create the statistics header with delete history button."""
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)  # Title takes most space
        header.grid_columnconfigure(1, weight=0)  # Button takes minimal space

        # Title
        title = ctk.CTkLabel(
            header,
            text="Quiz Statistics",
            font=("Helvetica", 28, "bold")
        )
        title.grid(row=0, column=0, pady=10, sticky="w")

        # Add a prominent delete history button
        delete_btn = ctk.CTkButton(
            header,
            text="🗑️ Delete History",
            command=self.clear_history,
            fg_color="#E74C3C",  # Red color
            hover_color="#C0392B",  # Darker red on hover
            text_color="white",
            width=180,
            height=40,
            corner_radius=10,
            font=("Helvetica", 14, "bold")
        )
        delete_btn.grid(row=0, column=1, padx=20, pady=10, sticky="e")

    def create_tabs(self):
        """Create tabbed interface for statistics."""
        tabview = ctk.CTkTabview(self)
        tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Add tabs
        tabview.add("Overview")
        tabview.add("History")
        tabview.add("Categories")
        tabview.add("Difficulty")

        # Configure tab grids
        for tab in ["Overview", "History", "Categories", "Difficulty"]:
            tabview.tab(tab).grid_columnconfigure(0, weight=1)
            tabview.tab(tab).grid_rowconfigure(0, weight=1)

        # Populate tabs
        self.create_overview_tab(tabview.tab("Overview"))
        self.create_history_tab(tabview.tab("History"))
        self.create_categories_tab(tabview.tab("Categories"))
        self.create_difficulty_tab(tabview.tab("Difficulty"))

    def create_overview_tab(self, parent):
        """Create the overview statistics tab."""
        overview_frame = ctk.CTkScrollableFrame(parent)
        overview_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        overview_frame.grid_columnconfigure(0, weight=1)

        # Calculate stats
        total_quizzes = self.stats.get("total_quizzes", 0)
        total_questions = self.stats.get("total_questions", 0)
        correct_answers = self.stats.get("correct_answers", 0)
        average_score = self.stats.get("average_score", 0)
        best_category = self.stats.get("best_category", "None")
        best_score = self.stats.get("best_score", 0)

        # Display overall stats
        stats_frame = ctk.CTkFrame(overview_frame)
        stats_frame.grid(row=0, column=0, sticky="ew", pady=10)

        metrics = [
            ("Total Quizzes Taken", str(total_quizzes)),
            ("Total Questions Answered", str(total_questions)),
            ("Correct Answers", str(correct_answers)),
            ("Average Score", f"{average_score:.1f}%"),
            ("Best Category", best_category),
            ("Best Score", f"{best_score:.1f}%")
        ]

        for i, (label, value) in enumerate(metrics):
            ctk.CTkLabel(
                stats_frame,
                text=label,
                font=("Helvetica", 14)
            ).grid(row=i, column=0, padx=20, pady=5, sticky="w")

            ctk.CTkLabel(
                stats_frame,
                text=value,
                font=("Helvetica", 14, "bold")
            ).grid(row=i, column=1, padx=20, pady=5, sticky="e")

        # Add visualizations if there's data
        if total_quizzes > 0:
            self.add_overview_charts(overview_frame)
        else:
            ctk.CTkLabel(
                overview_frame,
                text="No quiz data available yet. Take some quizzes to see statistics!",
                font=("Helvetica", 16)
            ).grid(row=1, column=0, pady=30)

    def add_overview_charts(self, parent):
        """Add charts to the overview tab using custom visualizations."""
        # Performance by difficulty visualization (bar chart)
        diff_chart_frame = ctk.CTkFrame(parent)
        diff_chart_frame.grid(row=1, column=0, sticky="ew", pady=10)
        diff_chart_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            diff_chart_frame,
            text="Performance by Difficulty",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, pady=10)

        # Get difficulty data
        difficulties = self.stats.get("difficulties", {})
        diff_data = []

        for diff in ["easy", "medium", "hard"]:
            data = difficulties.get(diff, {})
            total = data.get("total", 0)
            correct = data.get("correct", 0)

            if total > 0:
                score = (correct / total) * 100
                diff_data.append((diff.capitalize(), score))

        # Create bar chart using progress bars
        if diff_data:
            bars_frame = ctk.CTkFrame(diff_chart_frame)
            bars_frame.grid(row=1, column=0, padx=20, pady=10)

            # Colors for different difficulties
            colors = {
                "Easy": "green",
                "Medium": "orange",
                "Hard": "red"
            }

            for i, (label, value) in enumerate(diff_data):
                # Label
                ctk.CTkLabel(
                    bars_frame,
                    text=label,
                    font=("Helvetica", 14),
                    text_color=colors.get(label, "white")
                ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

                # Progress bar
                progress = ctk.CTkProgressBar(
                    bars_frame,
                    width=300,
                    height=15,
                    progress_color=colors.get(label, "blue")
                )
                progress.grid(row=i, column=1, padx=10, pady=5)
                progress.set(value / 100)

                # Value label
                ctk.CTkLabel(
                    bars_frame,
                    text=f"{value:.1f}%",
                    font=("Helvetica", 14, "bold")
                ).grid(row=i, column=2, padx=10, pady=5, sticky="e")

        # Performance trend visualization
        trend_frame = ctk.CTkFrame(parent)
        trend_frame.grid(row=2, column=0, sticky="ew", pady=10)
        trend_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            trend_frame,
            text="Recent Performance Trend",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, pady=10)

        # Get history data
        history = self.stats.get("history", [])
        if history:
            # Get the last 5 quizzes
            recent_history = history[-5:]

            # Create trend visualization
            trend_data_frame = ctk.CTkFrame(trend_frame)
            trend_data_frame.grid(row=1, column=0, padx=20, pady=10)

            # Headers
            ctk.CTkLabel(
                trend_data_frame,
                text="Quiz",
                font=("Helvetica", 14, "bold")
            ).grid(row=0, column=0, padx=10, pady=5)

            ctk.CTkLabel(
                trend_data_frame,
                text="Category",
                font=("Helvetica", 14, "bold")
            ).grid(row=0, column=1, padx=10, pady=5)

            ctk.CTkLabel(
                trend_data_frame,
                text="Score",
                font=("Helvetica", 14, "bold")
            ).grid(row=0, column=2, padx=10, pady=5)

            # Data rows
            for i, quiz in enumerate(reversed(recent_history), 1):
                # Quiz number
                ctk.CTkLabel(
                    trend_data_frame,
                    text=f"#{i}",
                    font=("Helvetica", 14)
                ).grid(row=i, column=0, padx=10, pady=5)

                # Category
                ctk.CTkLabel(
                    trend_data_frame,
                    text=quiz.get("category", "Unknown"),
                    font=("Helvetica", 14)
                ).grid(row=i, column=1, padx=10, pady=5)

                # Score with visual indicator
                score = quiz.get("percentage", 0)
                score_color = "green" if score >= 80 else \
                             "orange" if score >= 60 else \
                             "red"

                ctk.CTkLabel(
                    trend_data_frame,
                    text=f"{score:.1f}%",
                    font=("Helvetica", 14, "bold"),
                    text_color=score_color
                ).grid(row=i, column=2, padx=10, pady=5)

    def create_history_tab(self, parent):
        """Create the quiz history tab."""
        # Create a container frame for the tab content
        container_frame = ctk.CTkFrame(parent, fg_color="transparent")
        container_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        container_frame.grid_columnconfigure(0, weight=1)
        container_frame.grid_rowconfigure(1, weight=1)

        # Add a clear history button at the top
        button_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        button_frame.grid_columnconfigure(0, weight=1)

        clear_button = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear History",
            command=self.clear_history,
            fg_color="#E74C3C",  # Red color
            hover_color="#C0392B",  # Darker red on hover
            text_color="white",
            width=150,
            height=35,
            corner_radius=8,
            font=("Helvetica", 14, "bold")
        )
        clear_button.grid(row=0, column=0, sticky="e", padx=10, pady=5)

        # Create the scrollable frame for history content
        history_frame = ctk.CTkScrollableFrame(container_frame)
        history_frame.grid(row=1, column=0, sticky="nsew")
        history_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        # Headers
        headers = ["Date", "Category", "Difficulty", "Score", "Percentage"]

        for i, header in enumerate(headers):
            ctk.CTkLabel(
                history_frame,
                text=header,
                font=("Helvetica", 16, "bold")
            ).grid(row=0, column=i, padx=10, pady=(0, 10))

        # Quiz history
        history = self.stats.get("history", [])

        if history:
            # Sort by date (newest first)
            history.sort(key=lambda x: x.get("date", ""), reverse=True)

            for i, quiz in enumerate(history, 1):
                date_str = quiz.get("date", "")
                try:
                    date = datetime.fromisoformat(date_str)
                    date_display = date.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    date_display = date_str

                category = quiz.get("category", "Unknown")
                difficulty = quiz.get("difficulty", "Unknown").capitalize()
                score = f"{quiz.get('score', 0)}/{quiz.get('total', 0)}"
                percentage = f"{quiz.get('percentage', 0):.1f}%"

                # Set color based on difficulty
                diff_color = "green" if difficulty.lower() == "easy" else \
                            "orange" if difficulty.lower() == "medium" else \
                            "red"

                ctk.CTkLabel(
                    history_frame,
                    text=date_display,
                    font=("Helvetica", 14)
                ).grid(row=i, column=0, padx=10, pady=5)

                ctk.CTkLabel(
                    history_frame,
                    text=category,
                    font=("Helvetica", 14)
                ).grid(row=i, column=1, padx=10, pady=5)

                ctk.CTkLabel(
                    history_frame,
                    text=difficulty,
                    font=("Helvetica", 14),
                    text_color=diff_color
                ).grid(row=i, column=2, padx=10, pady=5)

                ctk.CTkLabel(
                    history_frame,
                    text=score,
                    font=("Helvetica", 14)
                ).grid(row=i, column=3, padx=10, pady=5)

                ctk.CTkLabel(
                    history_frame,
                    text=percentage,
                    font=("Helvetica", 14, "bold")
                ).grid(row=i, column=4, padx=10, pady=5)
        else:
            ctk.CTkLabel(
                history_frame,
                text="No quiz history available yet. Take some quizzes to see your history!",
                font=("Helvetica", 16)
            ).grid(row=1, column=0, columnspan=5, pady=30)

    def create_categories_tab(self, parent):
        """Create the categories statistics tab."""
        categories_frame = ctk.CTkScrollableFrame(parent)
        categories_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        categories_frame.grid_columnconfigure(0, weight=1)

        categories = self.stats.get("categories", {})

        # Add question counts section
        if self.question_counts:
            self.create_question_counts_section(categories_frame)

        if categories:
            # Sort categories by best score
            sorted_categories = sorted(
                categories.items(),
                key=lambda x: x[1].get("best_score", 0),
                reverse=True
            )

            # Title
            ctk.CTkLabel(
                categories_frame,
                text="Category Performance",
                font=("Helvetica", 18, "bold")
            ).grid(row=0, column=0, pady=10)

            # List all categories with details
            details_frame = ctk.CTkFrame(categories_frame)
            details_frame.grid(row=1, column=0, sticky="ew", pady=10)
            details_frame.grid_columnconfigure((0,1,2,3), weight=1)

            # Headers
            headers = ["Category", "Quizzes Taken", "Best Score", "Accuracy"]

            for i, header in enumerate(headers):
                ctk.CTkLabel(
                    details_frame,
                    text=header,
                    font=("Helvetica", 16, "bold")
                ).grid(row=0, column=i, padx=10, pady=(0, 10))

            for i, (category, data) in enumerate(sorted_categories, 1):
                quizzes = data.get("total", 0)
                best_score = f"{data.get('best_score', 0):.1f}%"

                accuracy = 0
                if quizzes > 0:
                    accuracy = (data.get("correct", 0) / data.get("total", 1)) * 100

                ctk.CTkLabel(
                    details_frame,
                    text=category,
                    font=("Helvetica", 14, "bold")
                ).grid(row=i, column=0, padx=10, pady=5)

                ctk.CTkLabel(
                    details_frame,
                    text=str(quizzes),
                    font=("Helvetica", 14)
                ).grid(row=i, column=1, padx=10, pady=5)

                ctk.CTkLabel(
                    details_frame,
                    text=best_score,
                    font=("Helvetica", 14)
                ).grid(row=i, column=2, padx=10, pady=5)

                ctk.CTkLabel(
                    details_frame,
                    text=f"{accuracy:.1f}%",
                    font=("Helvetica", 14)
                ).grid(row=i, column=3, padx=10, pady=5)

            # Top categories visualization
            if sorted_categories:
                top_frame = ctk.CTkFrame(categories_frame)
                top_frame.grid(row=2, column=0, sticky="ew", pady=20)
                top_frame.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    top_frame,
                    text="Best Categories",
                    font=("Helvetica", 16, "bold")
                ).grid(row=0, column=0, pady=10)

                # Create visual representation
                top_cats = sorted_categories[:5]  # Top 5 categories

                bars_frame = ctk.CTkFrame(top_frame)
                bars_frame.grid(row=1, column=0, padx=20, pady=10)

                for i, (category, data) in enumerate(top_cats):
                    best_score = data.get("best_score", 0)

                    # Label
                    ctk.CTkLabel(
                        bars_frame,
                        text=category,
                        font=("Helvetica", 14)
                    ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

                    # Progress bar
                    progress = ctk.CTkProgressBar(
                        bars_frame,
                        width=300,
                        height=15,
                        progress_color="blue"
                    )
                    progress.grid(row=i, column=1, padx=10, pady=5)
                    progress.set(best_score / 100)

                    # Value label
                    ctk.CTkLabel(
                        bars_frame,
                        text=f"{best_score:.1f}%",
                        font=("Helvetica", 14, "bold")
                    ).grid(row=i, column=2, padx=10, pady=5, sticky="e")
        else:
            ctk.CTkLabel(
                categories_frame,
                text="No category data available yet. Take some quizzes to see category statistics!",
                font=("Helvetica", 16)
            ).grid(row=0, column=0, pady=30)

    def create_difficulty_tab(self, parent):
        """Create the difficulty statistics tab."""
        difficulty_frame = ctk.CTkScrollableFrame(parent)
        difficulty_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        difficulty_frame.grid_columnconfigure(0, weight=1)

        difficulties = self.stats.get("difficulties", {})

        if any(difficulties.get(diff, {}).get("total", 0) > 0 for diff in ["easy", "medium", "hard"]):
            # Calculate performance metrics
            diff_metrics = {}

            for diff, data in difficulties.items():
                total = data.get("total", 0)
                correct = data.get("correct", 0)

                if total > 0:
                    accuracy = (correct / total) * 100
                    diff_metrics[diff] = {
                        "total": total,
                        "correct": correct,
                        "accuracy": accuracy
                    }

            # Title
            ctk.CTkLabel(
                difficulty_frame,
                text="Difficulty Level Analysis",
                font=("Helvetica", 18, "bold")
            ).grid(row=0, column=0, pady=10)

            # Create distribution visualization
            dist_frame = ctk.CTkFrame(difficulty_frame)
            dist_frame.grid(row=1, column=0, sticky="ew", pady=20)
            dist_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                dist_frame,
                text="Questions by Difficulty",
                font=("Helvetica", 16, "bold")
            ).grid(row=0, column=0, pady=10)

            # Create difficulty distribution
            totals = [diff_metrics.get(diff, {}).get("total", 0) for diff in ["easy", "medium", "hard"]]
            total_sum = sum(totals)

            if total_sum > 0:
                dist_bars_frame = ctk.CTkFrame(dist_frame)
                dist_bars_frame.grid(row=1, column=0, padx=20, pady=10)

                for i, diff in enumerate(["easy", "medium", "hard"]):
                    data = diff_metrics.get(diff, {})
                    total = data.get("total", 0)
                    percentage = (total / total_sum) * 100 if total_sum > 0 else 0

                    diff_color = "green" if diff == "easy" else \
                                "orange" if diff == "medium" else \
                                "red"

                    # Label
                    ctk.CTkLabel(
                        dist_bars_frame,
                        text=diff.capitalize(),
                        font=("Helvetica", 14),
                        text_color=diff_color
                    ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

                    # Progress bar for percentage
                    progress = ctk.CTkProgressBar(
                        dist_bars_frame,
                        width=250,
                        height=20,
                        progress_color=diff_color
                    )
                    progress.grid(row=i, column=1, padx=10, pady=5)
                    progress.set(percentage / 100)

                    # Count and percentage
                    ctk.CTkLabel(
                        dist_bars_frame,
                        text=f"{total} ({percentage:.1f}%)",
                        font=("Helvetica", 14)
                    ).grid(row=i, column=2, padx=10, pady=5, sticky="e")

            # Detailed stats
            details_frame = ctk.CTkFrame(difficulty_frame)
            details_frame.grid(row=2, column=0, sticky="ew", pady=10)

            for i, (diff, data) in enumerate(sorted(diff_metrics.items())):
                diff_color = "green" if diff == "easy" else \
                            "orange" if diff == "medium" else \
                            "red"

                diff_box = ctk.CTkFrame(details_frame)
                diff_box.grid(row=0, column=i, padx=10, pady=10)

                ctk.CTkLabel(
                    diff_box,
                    text=diff.capitalize(),
                    font=("Helvetica", 18, "bold"),
                    text_color=diff_color
                ).grid(row=0, column=0, pady=5)

                stats_text = (
                    f"Questions: {data['total']}\n"
                    f"Correct: {data['correct']}\n"
                    f"Accuracy: {data['accuracy']:.1f}%"
                )

                ctk.CTkLabel(
                    diff_box,
                    text=stats_text,
                    font=("Helvetica", 14),
                    justify="left"
                ).grid(row=1, column=0, padx=20, pady=10)
        else:
            ctk.CTkLabel(
                difficulty_frame,
                text="Try quizzes at all difficulty levels to see comparative statistics!",
                font=("Helvetica", 16)
            ).grid(row=0, column=0, pady=30)

    def create_question_counts_section(self, parent):
        """Create a section showing question counts by category and difficulty."""
        # Create a frame for the question counts
        counts_frame = ctk.CTkFrame(parent)
        counts_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        counts_frame.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            counts_frame,
            text="Available Questions by Category",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, pady=10)

        # Create a table for the counts
        table_frame = ctk.CTkFrame(counts_frame)
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Headers
        headers = ["Category", "Easy", "Medium", "Hard", "Total"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                table_frame,
                text=header,
                font=("Helvetica", 16, "bold")
            ).grid(row=0, column=i, padx=10, pady=(0, 10))

        # Sort categories alphabetically
        sorted_categories = sorted(self.question_counts.keys())

        # Add rows for each category
        for i, category in enumerate(sorted_categories, 1):
            difficulty_counts = self.question_counts[category]

            # Calculate total
            total = sum(difficulty_counts.values())

            # Category name
            ctk.CTkLabel(
                table_frame,
                text=category,
                font=("Helvetica", 14, "bold")
            ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            # Difficulty counts
            for j, difficulty in enumerate(["easy", "medium", "hard"]):
                count = difficulty_counts.get(difficulty, 0)
                ctk.CTkLabel(
                    table_frame,
                    text=str(count),
                    font=("Helvetica", 14)
                ).grid(row=i, column=j+1, padx=10, pady=5)

            # Total count
            ctk.CTkLabel(
                table_frame,
                text=str(total),
                font=("Helvetica", 14, "bold")
            ).grid(row=i, column=4, padx=10, pady=5)

    def clear_history(self):
        """Clear the quiz history."""
        # Show confirmation dialog
        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title("Confirm Clear History")
        confirm_dialog.geometry("400x200")
        confirm_dialog.grab_set()
        confirm_dialog.transient(self)

        # Center the dialog
        confirm_dialog.update_idletasks()
        width = confirm_dialog.winfo_width()
        height = confirm_dialog.winfo_height()
        x = (confirm_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (confirm_dialog.winfo_screenheight() // 2) - (height // 2)
        confirm_dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Warning icon and message
        warning_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        warning_frame.pack(pady=(20, 10))

        warning_icon = ctk.CTkLabel(
            warning_frame,
            text="⚠️",
            font=("Helvetica", 36)
        )
        warning_icon.pack()

        ctk.CTkLabel(
            confirm_dialog,
            text="Are you sure you want to clear all quiz history?",
            font=("Helvetica", 14, "bold"),
            wraplength=350
        ).pack(pady=5)

        ctk.CTkLabel(
            confirm_dialog,
            text="This action cannot be undone.",
            font=("Helvetica", 12),
            text_color="gray60",
            wraplength=350
        ).pack(pady=(0, 15))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        buttons_frame.pack(pady=10)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=confirm_dialog.destroy,
            fg_color="gray70",
            hover_color="gray50",
            width=100
        )
        cancel_btn.grid(row=0, column=0, padx=10)

        # Confirm button
        confirm_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear History",
            command=lambda: self._perform_clear_history(confirm_dialog),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=100
        )
        confirm_btn.grid(row=0, column=1, padx=10)

    def _perform_clear_history(self, dialog):
        """Actually perform the history clearing operation."""
        try:
            # Close the confirmation dialog
            dialog.destroy()

            # Clear history in stats
            self.stats["history"] = []

            # Reset category stats
            for category in self.stats.get("categories", {}):
                self.stats["categories"][category] = {
                    "total": 0,
                    "correct": 0,
                    "best_score": 0
                }

            # Reset difficulty stats
            for difficulty in self.stats.get("difficulties", {}):
                self.stats["difficulties"][difficulty] = {
                    "total": 0,
                    "correct": 0
                }

            # Reset overall stats
            self.stats["total_quizzes"] = 0
            self.stats["total_questions"] = 0
            self.stats["correct_answers"] = 0
            self.stats["average_score"] = 0
            self.stats["best_category"] = "None"
            self.stats["best_score"] = 0

            # Save the updated stats
            self._save_stats()

            # Show success message
            success_dialog = ctk.CTkToplevel(self)
            success_dialog.title("Success")
            success_dialog.geometry("300x150")
            success_dialog.grab_set()
            success_dialog.transient(self)

            ctk.CTkLabel(
                success_dialog,
                text="History cleared successfully!",
                font=("Helvetica", 14)
            ).pack(pady=20)

            ctk.CTkButton(
                success_dialog,
                text="OK",
                command=lambda: self._refresh_after_clear(success_dialog),
                width=100
            ).pack(pady=10)

        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            self.show_error(f"Failed to clear history: {str(e)}")

    def _save_stats(self):
        """Save statistics to JSON file."""
        try:
            stats_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'stats.json'
            )

            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=4)

            logger.info("Statistics saved successfully")
        except Exception as e:
            logger.error(f"Error saving statistics: {str(e)}")

    def _refresh_after_clear(self, dialog):
        """Refresh the statistics screen after clearing history."""
        dialog.destroy()

        # Reload stats
        self.stats = self.load_statistics()

        # Recreate all tabs
        for widget in self.winfo_children():
            widget.destroy()

        self.create_header()
        self.create_tabs()

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