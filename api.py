from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock job title database
job_db = {
"python developer": "REQUIREMENTS:3+ years Python experience - Web framework experience (Django/Flask) - Cloud platform knowledge\nPREFERRED:- Machine Learning- Docker/Kubernetes",
"data analyst": "REQUIREMENTS:Proficiency in SQL and data visualization tools - Strong analytical skills - Experience with Python or R\nPREFERRED:- Knowledge of machine learning concepts- Familiarity with big data technologies",
"devops engineer": "REQUIREMENTS:Experience with CI/CD pipelines - Strong knowledge of cloud platforms (AWS, Azure, GCP) - Proficiency in scripting languages (Python, Bash)PREFERRED:- Containerization technologies (Docker, Kubernetes)- Infrastructure as code (Terraform, CloudFormation)"
}

@app.route('/api/job-description')
def get_description():
    title = request.args.get('title', '').lower()
    desc = job_db.get(title)
    if desc:
        return jsonify({"job_title": title, "description": desc})
    return jsonify({"error": "Job title not found"}), 404

if __name__ == '__main__':
    app.run(port=5001)
