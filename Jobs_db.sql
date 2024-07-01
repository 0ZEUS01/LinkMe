DROP DATABASE IF EXISTS LinkMe;
create database LinkMe;
use LinkMe;

CREATE TABLE users (
    username VARCHAR(100),
    email VARCHAR(100) PRIMARY KEY,
    password VARCHAR(100)
);
CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL
);
CREATE TABLE user_skills (
    email VARCHAR(100),
    skill_id INT,
    PRIMARY KEY (email, skill_id),
    FOREIGN KEY (email) REFERENCES users(email),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);
CREATE TABLE experiences (
    experience_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100),
    title VARCHAR(255),
    description TEXT,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (email) REFERENCES users(email)
);
CREATE TABLE profile_pictures (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100),
    profile_pic_path VARCHAR(255),
    FOREIGN KEY (email) REFERENCES users(email)
);
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT,
    required_skills TEXT,
    salary_range VARCHAR(100),
    location VARCHAR(100),
    company VARCHAR(100),
    experience_level VARCHAR(50),
    industry VARCHAR(100),
    job_type VARCHAR(50),
    date_posted DATE
);

