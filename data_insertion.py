import pandas as pd
import mysql.connector

# Database connection details
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'LinkMe'
}

# Connect to the MySQL database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Create the skills table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL
)
""")

# Function to insert skills into the skills table
def insert_skill(skill):
    try:
        cursor.execute("INSERT INTO skills (skill_name) VALUES (%s)", (skill,))
        connection.commit()
    except mysql.connector.IntegrityError:
        # Ignore duplicate entries
        pass

# Read the Excel file and extract skills
file_path = 'Job opportunities.xlsx'
df = pd.read_excel(file_path)

unique_skills = set()
for skills in df['Required Skills']:
    skill_list = skills.split(', ')
    unique_skills.update(skill_list)

# Insert unique skills into the database
for skill in unique_skills:
    insert_skill(skill)

# Close the database connection
cursor.close()
connection.close()

print("Skills have been successfully inserted into the skills table.")
