import MySQLdb
from flask import Blueprint, current_app, render_template, session, redirect, url_for, request
from app import mysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

job_blueprint = Blueprint('job', __name__, template_folder='templates')

def get_user_skills(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        SELECT s.skill_name
        FROM user_skills us
        JOIN skills s ON us.skill_id = s.skill_id
        WHERE us.id = %s
    """
    cursor.execute(query, (user_id,))
    skills = cursor.fetchall()
    cursor.close()
    return " ".join(skill['skill_name'] for skill in skills)

def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    return countries

def get_all_jobs():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    cursor.close()
    return jobs

@job_blueprint.route('/jobs')
def jobs():
    try:
        user_id = session.get('id')

        if not user_id:
            return redirect(url_for('auth_blueprint.signin'))

        user_skills = get_user_skills(user_id)
        all_jobs = get_all_jobs()

        if not user_skills or not all_jobs:
            return render_template('jobs.html', job_data=[], job_offers=[], countries=get_countries())

        potential_jobs = get_potential_jobs(user_skills, all_jobs)
        job_offers = get_job_offers(user_skills, all_jobs)

        return render_template('jobs.html', job_data=potential_jobs, job_offers=job_offers, countries=get_countries())

    except Exception as e:
        print(f"Error: {e}")
        return render_template('jobs.html', job_data=[], job_offers=[], countries=get_countries())


def get_potential_jobs(user_skills, all_jobs):
    job_data = []
    job_titles_seen = set()

    for job in all_jobs:
        job_title = job['job_title']
        if job_title not in job_titles_seen:
            job_titles_seen.add(job_title)
            required_skills = job['required_skills']
            required_skill_list = required_skills.split(', ')
            
            user_skill_set = set(user_skills.split())
            required_skill_set = set(required_skill_list)
            
            if user_skill_set.intersection(required_skill_set):
                job_data.append(job)

    vectorizer = TfidfVectorizer(stop_words='english')
    job_descriptions = [job['required_skills'] for job in job_data]
    job_vectors = vectorizer.fit_transform(job_descriptions)
    user_vector = vectorizer.transform([user_skills])

    similarities = cosine_similarity(user_vector, job_vectors).flatten()

    for job, similarity in zip(job_data, similarities):
        job['similarity'] = similarity * 100 

    return job_data

def get_job_offers(user_skills, all_jobs):
    job_data = []
    job_descriptions = []

    for job in all_jobs:
        required_skills = job['required_skills']
        required_skill_list = required_skills.split(', ')
        
        user_skill_set = set(user_skills.split())
        required_skill_set = set(required_skill_list)
        
        if user_skill_set.intersection(required_skill_set):
            job_data.append(job)
            job_descriptions.append(required_skills)

    vectorizer = TfidfVectorizer(stop_words='english')
    job_vectors = vectorizer.fit_transform(job_descriptions)
    user_vector = vectorizer.transform([user_skills])

    similarities = cosine_similarity(user_vector, job_vectors).flatten()

    threshold = 0.0  
    top_matching_jobs = []
    for job, similarity in zip(job_data, similarities):
        if similarity >= threshold:
            job['similarity'] = similarity * 100 
            top_matching_jobs.append(job)

    return top_matching_jobs

@job_blueprint.route('/jobs/search')
def search_jobs():
    try:
        user_id = session.get('id')
        if not user_id:
            return redirect(url_for('auth_blueprint.signin'))

        user_skills = get_user_skills(user_id)
        query = request.args.get('query', '').strip().lower()

        if not query:
            return redirect(url_for('job.jobs'))

        all_jobs = get_all_jobs()
        filtered_jobs = filter_jobs(all_jobs, user_skills, query)

        no_results = len(filtered_jobs) == 0

        return render_template('jobs.html', job_data=filtered_jobs, job_offers=[], no_results=no_results)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('jobs.html', job_data=[], job_offers=[], no_results=False)

def filter_jobs(all_jobs, user_skills, query):
    job_data = []

    for job in all_jobs:
        job_title = job['job_title'].lower()
        required_skills = job['required_skills'].lower()

        if query in job_title or query in required_skills:
            required_skill_list = required_skills.split(', ')
            
            user_skill_set = set(user_skills.split())
            required_skill_set = set(required_skill_list)
            
            if user_skill_set.intersection(required_skill_set):
                job_data.append(job)

    return job_data
