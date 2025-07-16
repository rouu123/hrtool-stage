
import numpy as np
from src.cv_parser import CVParser
from src.job_parser import JobParser
import json
import glob
import os

def calculate_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    vec1 = vec1 / np.linalg.norm(vec1)
    vec2 = vec2 / np.linalg.norm(vec2)
    return np.dot(vec1, vec2)

def calculate_score_skills(cv_data, job_data):
    """Compare embedded skill categories against CV skills"""
    cv_skills_embedding = cv_data.get('skills_embedding')
    wanted_embedding = job_data.get('wanted_skills_embedding')
    
    # Compare wanted skills category
    if cv_skills_embedding and wanted_embedding:
        return calculate_similarity(cv_skills_embedding,wanted_embedding)
    print("missing skills embedding ")
    return 0.0


def compute_final_score(similarity, wanted, experience, required_experience, weights=None):
    if weights is None:
        weights = {'embedding': 0.5, 'wanted': 0.35, 'experience': 0.15}

    return (
        weights['embedding'] * similarity +
        weights['wanted'] * wanted +
        weights['experience'] * (1 if float(experience or 0) >= float(required_experience or 0) else 0)
    )