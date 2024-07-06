import MySQLdb
import logging
from flask import Blueprint, render_template, session, redirect, url_for, flash
from app import mysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

job_blueprint = Blueprint('job', __name__, template_folder='templates')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_user_skills(user_id):
    try:
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
    except Exception as e:
        logging.error(f"Error fetching user skills: {e}")
        return None

def get_all_jobs():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()
        cursor.close()
        return jobs
    except Exception as e:
        logging.error(f"Error fetching jobs: {e}")
        return None

@job_blueprint.route('/jobs')
def jobs():
    user_id = session.get('id')

    if not user_id:
        flash('You need to sign in first.', 'warning')
        return redirect(url_for('auth_blueprint.signin'))

    try:
        user_skills = get_user_skills(user_id)
        jobs = get_all_jobs()

        if user_skills is None or jobs is None:
            flash('Error retrieving data.', 'danger')
            return render_template('Home.html', job_data=[], job_offers=[])

        if not user_skills or not jobs:
            flash('No skills or jobs found.', 'info')
            return render_template('Home.html', job_data=[], job_offers=jobs)

        job_descriptions = [job['job_description'] for job in jobs]
        job_ids = [job['id'] for job in jobs]

        vectorizer = TfidfVectorizer(stop_words='english')
        job_vectors = vectorizer.fit_transform(job_descriptions)
        user_vector = vectorizer.transform([user_skills])

        similarities = cosine_similarity(user_vector, job_vectors).flatten()
        job_similarity_df = pd.DataFrame({'job_id': job_ids, 'similarity': similarities})
        job_similarity_df = job_similarity_df.sort_values(by='similarity', ascending=False)

        top_matching_jobs = []
        for _, row in job_similarity_df.iterrows():
            job_id = row['job_id']
            top_matching_jobs.append(next(job for job in jobs if job['id'] == job_id))

        return render_template('Home.html', job_data=top_matching_jobs, job_offers=jobs)

    except Exception as e:
        logging.error(f"Error in job matching process: {e}")
        flash('An error occurred while processing your request.', 'danger')
        return render_template('Home.html', job_data=[], job_offers=[])
