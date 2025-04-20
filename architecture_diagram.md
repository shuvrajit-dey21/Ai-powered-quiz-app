# Quiz App Architecture

```
quiz_app/
├── main.py                  # Main entry point
├── ui/                      # UI components
│   ├── main_window.py       # Main application window
│   ├── quiz_screen.py       # Quiz interface
│   ├── admin_screen.py      # Admin panel
│   ├── splash_screen.py     # Splash screen
│   ├── statistics_screen.py # Statistics screen
│   ├── login_screen.py      # Login screen
│   └── signup_screen.py     # Signup screen
├── core/                    # Core functionality
│   ├── question_manager.py  # Question management
│   ├── ai_generator.py      # AI question generation
│   ├── category_manager.py  # NEW: Category management
│   └── user_manager.py      # User management
├── data/                    # Data storage
│   ├── questions.json       # Question database
│   ├── categories.json      # NEW: Category definitions
│   ├── user_history.json    # NEW: User question history
│   └── backup/              # Automatic backups
├── assets/                  # UI assets
└── utils/                   # Utilities
    └── logger.py            # Logging configuration
```

## Component Interactions

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   UI Layer      │◄────┤  Core Layer     │◄────┤  Data Layer     │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       ▲                       ▲                       ▲
       │                       │                       │
       │                       │                       │
       │                       │                       │
       │                       │                       │
       │                       │                       │
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Interface │     │ Business Logic  │     │  Data Storage   │
│  - Quiz Screen  │     │ - Question Mgr  │     │ - questions.json│
│  - Admin Screen │     │ - AI Generator  │     │ - categories.json│
│  - Main Window  │     │ - Category Mgr  │     │ - user_history  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## AI Integration

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  AI Generator   │◄────┤  Local Models   │     │  External APIs  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       ▲                       ▲                       ▲
       │                       │                       │
       │                       │                       │
       │                       │                       │
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Question Manager│     │ Transformers    │     │ Open Trivia DB  │
│ - Generate      │     │ - distilgpt2    │     │ - Fallback      │
│ - Filter        │     │ - flan-t5-small │     │ - Supplementary │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```
