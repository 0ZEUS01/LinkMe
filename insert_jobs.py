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

# Read data from Excel file
file_path = 'Job opportunities.xlsx'
jobs_df = pd.read_excel(file_path)

# Insert data into MySQL table
for index, row in jobs_df.iterrows():
    job_title = row['Job Title']
    job_description = row['Job Description']
    required_skills = row['Required Skills']
    salary_range = row['Salary Range']
    location = row['Location']
    company = row['Company']
    experience_level = row['Experience Level']
    industry = row['Industry']
    job_type = row['Job Type']
    date_posted = row['Date Posted']
    
    # Insert into MySQL table
    cursor.execute('''
        INSERT INTO jobs (job_title, job_description, required_skills, salary_range, location,
                          company, experience_level, industry, job_type, date_posted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (job_title, job_description, required_skills, salary_range, location,
          company, experience_level, industry, job_type, date_posted))

# Commit changes and close connection
connection.commit()
cursor.close()
connection.close()

print("Jobs have been successfully inserted into the jobs table.")
