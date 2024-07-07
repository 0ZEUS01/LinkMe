import MySQLdb
from flask import Blueprint, render_template, session, redirect, url_for
from app import mysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

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
            return render_template('Home.html', job_data=[], job_offers=[])

        potential_jobs = get_potential_jobs(user_skills, all_jobs)
        job_offers = get_job_offers(user_skills, all_jobs)

        return render_template('Home.html', job_data=potential_jobs, job_offers=job_offers)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('Home.html', job_data=[], job_offers=[])

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
        job['similarity'] = similarity * 100  # Convert similarity to percentage

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

    threshold = 0.2  # Adjust the similarity threshold as needed
    top_matching_jobs = []
    for job, similarity in zip(job_data, similarities):
        if similarity >= threshold:
            job['similarity'] = similarity * 100  # Convert similarity to percentage
            top_matching_jobs.append(job)

    return top_matching_jobs


