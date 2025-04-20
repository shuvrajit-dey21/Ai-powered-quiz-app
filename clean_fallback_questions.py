import json
import re
import os

def clean_fallback_questions():
    """Remove sample questions from fallback_questions.json"""
    print("Cleaning fallback_questions.json...")
    
    # Create a new file with real questions
    real_questions = {
        "Science": {
            "easy": [
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
            ],
            "medium": [
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
            ],
            "hard": [
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
        },
        "History": {
            "easy": [
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
            ],
            "medium": [
                {
                    "question": "Which ancient civilization built the Machu Picchu complex in Peru?",
                    "options": ["Inca", "Maya", "Aztec", "Olmec"],
                    "correct_answer": "Inca",
                    "category": "History",
                    "difficulty": "medium"
                },
                {
                    "question": "Who was the first woman to win a Nobel Prize?",
                    "options": ["Marie Curie", "Rosalind Franklin", "Dorothy Hodgkin", "Irène Joliot-Curie"],
                    "correct_answer": "Marie Curie",
                    "category": "History",
                    "difficulty": "medium"
                }
            ],
            "hard": [
                {
                    "question": "In which year did the Chernobyl disaster occur?",
                    "options": ["1986", "1979", "1992", "1975"],
                    "correct_answer": "1986",
                    "category": "History",
                    "difficulty": "hard"
                },
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
                },
                {
                    "question": "Which is the largest ocean on Earth?",
                    "options": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"],
                    "correct_answer": "Pacific Ocean",
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
                },
                {
                    "question": "Which country has the most natural lakes?",
                    "options": ["Canada", "United States", "Russia", "Finland"],
                    "correct_answer": "Canada",
                    "category": "Geography",
                    "difficulty": "medium"
                }
            ],
            "hard": [
                {
                    "question": "Which mountain range separates Europe from Asia?",
                    "options": ["Ural Mountains", "Alps", "Himalayas", "Andes"],
                    "correct_answer": "Ural Mountains",
                    "category": "Geography",
                    "difficulty": "hard"
                },
                {
                    "question": "What is the driest place on Earth?",
                    "options": ["Atacama Desert", "Sahara Desert", "Death Valley", "Antarctic Dry Valleys"],
                    "correct_answer": "Antarctic Dry Valleys",
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
                },
                {
                    "question": "Which book features the character Harry Potter?",
                    "options": ["Harry Potter and the Philosopher's Stone", "The Lord of the Rings", "The Chronicles of Narnia", "The Hunger Games"],
                    "correct_answer": "Harry Potter and the Philosopher's Stone",
                    "category": "Literature",
                    "difficulty": "easy"
                }
            ],
            "medium": [
                {
                    "question": "Who wrote 'Pride and Prejudice'?",
                    "options": ["Jane Austen", "Charlotte Brontë", "Emily Brontë", "Virginia Woolf"],
                    "correct_answer": "Jane Austen",
                    "category": "Literature",
                    "difficulty": "medium"
                },
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
                },
                {
                    "question": "Which Russian author wrote 'War and Peace'?",
                    "options": ["Leo Tolstoy", "Fyodor Dostoevsky", "Anton Chekhov", "Ivan Turgenev"],
                    "correct_answer": "Leo Tolstoy",
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
                },
                {
                    "question": "Which actor played Iron Man in the Marvel Cinematic Universe?",
                    "options": ["Robert Downey Jr.", "Chris Evans", "Chris Hemsworth", "Mark Ruffalo"],
                    "correct_answer": "Robert Downey Jr.",
                    "category": "Movies",
                    "difficulty": "easy"
                }
            ],
            "medium": [
                {
                    "question": "Which film won the Academy Award for Best Picture in 1994?",
                    "options": ["Schindler's List", "The Fugitive", "The Piano", "The Remains of the Day"],
                    "correct_answer": "Schindler's List",
                    "category": "Movies",
                    "difficulty": "medium"
                },
                {
                    "question": "Who directed the 'Lord of the Rings' trilogy?",
                    "options": ["Peter Jackson", "James Cameron", "Steven Spielberg", "Christopher Nolan"],
                    "correct_answer": "Peter Jackson",
                    "category": "Movies",
                    "difficulty": "medium"
                }
            ],
            "hard": [
                {
                    "question": "Which actor has won the most Academy Awards for Best Actor?",
                    "options": ["Daniel Day-Lewis", "Jack Nicholson", "Marlon Brando", "Tom Hanks"],
                    "correct_answer": "Daniel Day-Lewis",
                    "category": "Movies",
                    "difficulty": "hard"
                },
                {
                    "question": "Which film is considered the first feature-length animated film?",
                    "options": ["Snow White and the Seven Dwarfs", "Pinocchio", "Fantasia", "Bambi"],
                    "correct_answer": "Snow White and the Seven Dwarfs",
                    "category": "Movies",
                    "difficulty": "hard"
                }
            ]
        },
        "Sports": {
            "easy": [
                {
                    "question": "In which sport would you perform a slam dunk?",
                    "options": ["Basketball", "Volleyball", "Tennis", "Football"],
                    "correct_answer": "Basketball",
                    "category": "Sports",
                    "difficulty": "easy"
                },
                {
                    "question": "How many players are there in a standard soccer team?",
                    "options": ["11", "9", "10", "12"],
                    "correct_answer": "11",
                    "category": "Sports",
                    "difficulty": "easy"
                }
            ],
            "medium": [
                {
                    "question": "Which country won the FIFA World Cup in 2018?",
                    "options": ["France", "Croatia", "Brazil", "Germany"],
                    "correct_answer": "France",
                    "category": "Sports",
                    "difficulty": "medium"
                },
                {
                    "question": "In which sport would you use a 'shuttlecock'?",
                    "options": ["Badminton", "Tennis", "Table Tennis", "Squash"],
                    "correct_answer": "Badminton",
                    "category": "Sports",
                    "difficulty": "medium"
                }
            ],
            "hard": [
                {
                    "question": "Who holds the record for the most Grand Slam tennis titles?",
                    "options": ["Novak Djokovic", "Rafael Nadal", "Roger Federer", "Serena Williams"],
                    "correct_answer": "Novak Djokovic",
                    "category": "Sports",
                    "difficulty": "hard"
                },
                {
                    "question": "In which year were the first modern Olympic Games held?",
                    "options": ["1896", "1900", "1904", "1908"],
                    "correct_answer": "1896",
                    "category": "Sports",
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
                },
                {
                    "question": "What does 'HTTP' stand for?",
                    "options": ["Hypertext Transfer Protocol", "Hypertext Transit Protocol", "Hypertext Transfer Process", "Hypertext Transit Process"],
                    "correct_answer": "Hypertext Transfer Protocol",
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
                },
                {
                    "question": "Who is considered the father of modern computer science?",
                    "options": ["Alan Turing", "Bill Gates", "Steve Jobs", "Tim Berners-Lee"],
                    "correct_answer": "Alan Turing",
                    "category": "Technology",
                    "difficulty": "medium"
                }
            ],
            "hard": [
                {
                    "question": "What was the name of the first computer virus that spread in the wild?",
                    "options": ["Brain", "Creeper", "Melissa", "ILOVEYOU"],
                    "correct_answer": "Brain",
                    "category": "Technology",
                    "difficulty": "hard"
                },
                {
                    "question": "Which programming language was developed by Bjarne Stroustrup?",
                    "options": ["C++", "Java", "Python", "Ruby"],
                    "correct_answer": "C++",
                    "category": "Technology",
                    "difficulty": "hard"
                }
            ]
        },
        "Music": {
            "easy": [
                {
                    "question": "Who sang 'Thriller'?",
                    "options": ["Michael Jackson", "Prince", "Madonna", "Whitney Houston"],
                    "correct_answer": "Michael Jackson",
                    "category": "Music",
                    "difficulty": "easy"
                },
                {
                    "question": "Which instrument has 88 keys?",
                    "options": ["Piano", "Guitar", "Violin", "Drums"],
                    "correct_answer": "Piano",
                    "category": "Music",
                    "difficulty": "easy"
                }
            ],
            "medium": [
                {
                    "question": "Which band released the album 'The Dark Side of the Moon'?",
                    "options": ["Pink Floyd", "The Beatles", "Led Zeppelin", "The Rolling Stones"],
                    "correct_answer": "Pink Floyd",
                    "category": "Music",
                    "difficulty": "medium"
                },
                {
                    "question": "Who composed the 'Four Seasons'?",
                    "options": ["Antonio Vivaldi", "Johann Sebastian Bach", "Wolfgang Amadeus Mozart", "Ludwig van Beethoven"],
                    "correct_answer": "Antonio Vivaldi",
                    "category": "Music",
                    "difficulty": "medium"
                }
            ],
            "hard": [
                {
                    "question": "Which composer was deaf when he wrote his Ninth Symphony?",
                    "options": ["Ludwig van Beethoven", "Wolfgang Amadeus Mozart", "Johann Sebastian Bach", "Franz Schubert"],
                    "correct_answer": "Ludwig van Beethoven",
                    "category": "Music",
                    "difficulty": "hard"
                },
                {
                    "question": "In which year was the first Grammy Awards ceremony held?",
                    "options": ["1959", "1965", "1970", "1955"],
                    "correct_answer": "1959",
                    "category": "Music",
                    "difficulty": "hard"
                }
            ]
        }
    }
    
    # Save the cleaned data
    with open('data/fallback_questions.json', 'w') as f:
        json.dump(real_questions, f, indent=4)
    
    print(f"Created new fallback_questions.json with {sum(len(real_questions[cat][diff]) for cat in real_questions for diff in real_questions[cat])} real questions")

if __name__ == "__main__":
    clean_fallback_questions()
