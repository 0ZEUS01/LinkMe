from flask import Blueprint, render_template, current_app, session, redirect, url_for, request
import MySQLdb.cursors
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Assuming your data is loaded and vectorized globally
data = pd.read_excel('Job opportunities.xlsx')

# Global variables for user skills and recommended jobs
user_skills = ''
recommended_jobs = pd.DataFrame()  # Initialize as an empty DataFrame
vectorizer = TfidfVectorizer()
top_n_indices=[]


def map_job_keys(job):
    return {
        'Job Title': job['job_title'],
        'Job Description': job['job_description'],
        'Required Skills': job['required_skills'],
        'Salary Range': job['salary_range'],
        'Location': job['location'],
        'Company': job['company'],
        'Experience Level': job['experience_level'],
        'Industry': job['industry'],
        'Job Type': job['job_type'],
        'Date Posted': job['date_posted']
    }

def check_user_skills(user_skills):
    if not user_skills:
        return False
    
    # Fetch skills from the skills table in the database
    skills_query = '''
        SELECT COUNT(*) AS skill_count
        FROM skills
        WHERE skill_name IN %s and skill_id<117
    '''
    skill_names = [skill.strip() for skill in user_skills.split(',')]

    print(skill_names)
    
    cursor = get_mysql_connection()
    cursor.execute(skills_query,[skill_names])
    result = cursor.fetchone()
    cursor.close()
    
    # Check if any skills match
    skill_count = result['skill_count'] if result else 0
    return skill_count > 0

# Modify calculate_recommendations to use check_user_skills
def calculate_recommendations(user_skills):
    global recommended_jobs, vectorizer, top_n_indices

    if user_skills:
        # Check if user skills match any skills in the database
        if not check_user_skills(user_skills):
            recommended_jobs = pd.DataFrame()  # Empty DataFrame if no skills match
            return
        
        combined_skills = data['Required Skills'].apply(lambda x: x.replace(', ', ' ')).tolist()
        combined_skills.insert(0, user_skills.replace(', ', ' '))  # Insert user skills at index 0

        skills_matrix = vectorizer.fit_transform(combined_skills)
        job_skills_matrix = skills_matrix[1:]  # Exclude user skills from the matrix
        user_skills_vector = skills_matrix[0]  # The first vector is the user skills vector

        similarity_scores = cosine_similarity(user_skills_vector, job_skills_matrix)
        top_n_indices = similarity_scores.argsort()[0][-20:][::-1]
        recommended_jobs = data.iloc[top_n_indices]
    else:
        recommended_jobs = pd.DataFrame()

# Blueprint initialization
job_blueprint = Blueprint('job', __name__, url_prefix='/job', static_folder='static', template_folder='templates')

# Helper function to get MySQL connection
def get_mysql_connection():
    return current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

# Before first request, calculate recommendations
# @job_blueprint.before_app_request
def preprocess_recommendations():
    global user_skills
    # Fetch user skills from database
    user_email = session.get("email","")  # Replace with actual user email
    user_skills_query = '''
        SELECT skills.skill_name
        FROM user_skills
        JOIN skills ON user_skills.skill_id = skills.skill_id
        WHERE user_skills.email = %s
    '''
    cursor = get_mysql_connection()
    cursor.execute(user_skills_query, (user_email,))
    skills_results = cursor.fetchall()
    cursor.close()

    # Convert fetched skills into a string format
    user_skills_list = [skill['skill_name'] for skill in skills_results]
    user_skills = ', '.join(user_skills_list) if user_skills_list else ''

    # Calculate recommendations based on fetched user skills
    calculate_recommendations(user_skills)

# Route to list recommended jobs
@job_blueprint.route('/')
def list_jobs():
    preprocess_recommendations()
    if 'email' not in session:
        return redirect(url_for('auth_blueprint.signin'))
    global recommended_jobs

    # Check if recommended_jobs is empty or not
    if not recommended_jobs.empty:
        jobs_list = recommended_jobs.to_dict('records')
        # Create a set of job titles
        jobs_title = (title['Job Title'] for title in jobs_list[1:])
        job_titles_set = list(set(jobs_title))
        # print(job_titles_set)
        return render_template('jobs.html', jobs=recommended_jobs.to_dict('records'), set_jobs = job_titles_set )  # Convert DataFrame to list of dicts
    else:
        return render_template('jobs.html', jobs=None)  # Pass None if recommended_jobs is empty

@job_blueprint.route('/search')
def search_jobs():
    preprocess_recommendations()
    if 'email' not in session:
        return redirect(url_for('auth_blueprint.signin'))
    global user_skills
    global recommended_jobs
    global top_n_indices

    title = request.args.get('title', '')

    if title:
        calculate_recommendations(user_skills)
        if recommended_jobs.empty:
            return render_template('jobs.html', jobs=None)  # Pass None if no titles or ids match


        
        # Filter recommended jobs based on title similarity
        filtered_jobs = recommended_jobs[recommended_jobs['Job Title'].str.contains(title, case=False)]

        # Extract job titles for SQL query
        recommended_job_titles = filtered_jobs['Job Title'].tolist()
        indices = [i+1 for i in top_n_indices]
        print(recommended_job_titles)
        print(indices)

        if recommended_job_titles and indices:
            cursor = get_mysql_connection()

            # Construct the placeholders for job titles and ids
            job_title_placeholders = ', '.join(['%s'] * len(recommended_job_titles))
            id_placeholders = ', '.join(['%s'] * len(indices))
            query = f'''
                SELECT *
                FROM jobs
                WHERE job_title IN ({job_title_placeholders})
                AND id IN ({id_placeholders})
            '''

            # Combine both lists for the cursor execute
            cursor.execute(query, recommended_job_titles + indices)
            jobs = cursor.fetchall()
            cursor.close()
            print(jobs)

            # Map keys before sending to the frontend
            mapped_jobs = [map_job_keys(job) for job in jobs]

            return render_template('jobs.html', jobs=mapped_jobs)
        else:
            return render_template('jobs.html', jobs=None)  # Pass None if no titles or ids match
    else:
        return redirect(url_for('job.list_jobs'))
