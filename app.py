from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from src.cv_parser import CVParser
from src.job_parser import JobParser
from src.matcher import calculate_similarity, calculate_score_skills, compute_final_score
import numpy as np
from src.odoo import get_job_description


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


cv_parser = CVParser()
job_parser = JobParser()

import requests


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    job_text = ""
    
    if request.method == 'POST':
        print("Received POST request")

        job_title = request.form.get('job_title', '').strip()
        job_text = request.form.get('job_description', '').strip()

        # ---  Si la description est vide, on va chercher via titre ---
        if not job_text and job_title:
            job_text = get_job_description(job_title)
            print(f"Fetched job description for '{job_title}': {job_text}")

        # Ensuite on parse comme avant
        job_data = job_parser.parse_job_description(job_text)

        print("parse job_description done")
        uploaded_files = request.files.getlist('cv_files')
        temp_file_paths = []

        for f in uploaded_files:
            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)
            temp_file_paths.append(path)  # track for deletion later

            cv_data = cv_parser.parse_cv(path)
            print(f"parse cv {filename} done")
            if not cv_data.get('skills_embedding'):
                continue

            similarity = calculate_similarity(cv_data['skills_embedding'], job_data['skills_embedding'])
            skills_score = calculate_score_skills(cv_data, job_data)
            experience = cv_data.get('total_experience', 0)
            required_experience = job_data.get('required_experience', 0)

            total_score = compute_final_score(
                similarity,
                skills_score,
                experience,
                required_experience
            )

            results.append({
    'name': filename,
    'score': total_score,
    'similarity': similarity,
    'skills_score': skills_score,
    'experience': experience,
    'candidate_name': cv_data.get('name', 'N/A name'),
    'email': cv_data.get('email', 'no-email@example.com'),
    'phone': cv_data.get('phone', 'N/A phone')
})
        # Sort results by score in descending order
        if results:     
            results = sorted(results, key=lambda r: r['score'], reverse=True)

 # 🔥 Delete uploaded files
        for path in temp_file_paths:
            try:
                os.remove(path)
            except Exception as e:
                print(f"Failed to delete file {path}: {e}")

    return render_template("index.html", results=results, job_text=job_text)

if __name__ == '__main__':
    app.run(debug=True)
