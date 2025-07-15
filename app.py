from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from src.cv_parser import CVParser
from src.job_parser import JobParser
from src.matcher import calculate_similarity, calculate_category_matches, compute_final_score
import numpy as np
import shutil


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


cv_parser = CVParser()
job_parser = JobParser()

import requests

def get_description_from_api(title):
    try:
        resp = requests.get("http://localhost:5001/api/job-description", params={"title": title})
        if resp.status_code == 200:
            return resp.json().get("description", "")
    except Exception as e:
        print(f"API call failed: {e}")
    return ''


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
            job_text = get_description_from_api(job_title)  # à définir plus tard
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
            category_scores = calculate_category_matches(cv_data, job_data)
            required_match = category_scores['required_skills']['score']
            preferred_match = category_scores['preferred_skills']['score']
            experience = cv_data.get('total_experience', 0)
            required_experience = job_data.get('required_experience', 0)

            total_score = compute_final_score(
                similarity,
                required_match,
                preferred_match,
                experience,
                required_experience
            )

            results.append({
    'name': filename,
    'score': total_score,
    'raw_score': similarity,
    'required': required_match,
    'preferred': preferred_match,
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
