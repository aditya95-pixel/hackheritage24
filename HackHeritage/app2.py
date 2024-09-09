import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('career_recommendations.db')

# Create a cursor object
cursor = conn.cursor()

# Create the table to store career recommendations
cursor.execute('''
    CREATE TABLE IF NOT EXISTS career_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interest TEXT NOT NULL,
        careers TEXT NOT NULL
    )
''')

# Insert the career recommendations for each interest
career_data = [
    ('science', 'Biologist, Chemist, Physicist, Environmental Scientist, Doctor, Microbiologist, Geneticist, Astronomer'),
    ('math', 'Mathematician, Statistician, Data Analyst, Economist, Engineer, Actuary, Operations Research Analyst, Cryptographer'),
    ('art', 'Graphic Designer, Animator, Fashion Designer, Architect, Art Director, Photographer, Interior Designer, Illustrator'),
    ('technology', 'Software Developer, Web Developer, Data Scientist, Cybersecurity Expert, AI Engineer, Network Administrator, Robotics Engineer, Cloud Architect'),
    ('literature', 'Journalist, Author, Editor, Content Writer, Librarian, Translator, Public Relations Specialist, Copywriter'),
    ('business', 'Entrepreneur, Marketing Manager, Financial Analyst, Human Resources Manager, Consultant, Project Manager, Investment Banker, Sales Manager')
]

# Insert the data into the table
cursor.executemany('''
    INSERT INTO career_recommendations (interest, careers)
    VALUES (?, ?)
''', career_data)
cursor.execute('select * from career_recommendations')

# Commit and close the connection
conn.commit()
conn.close()
