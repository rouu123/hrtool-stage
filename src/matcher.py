
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

def calculate_category_matches(cv_data, job_data):
    """Compare embedded skill categories against CV skills"""
    results = {
        'required_skills': {'score': 0},
        'preferred_skills': {'score': 0}
    }
    
    # Get all embeddings
    cv_skills_embedding = cv_data.get('skills_embedding')
    req_embedding = job_data.get('required_skills_embedding')
    pref_embedding = job_data.get('preferred_skills_embedding')
    
    # Compare required skills category
    if cv_skills_embedding and req_embedding:
        results['required_skills']['score'] = calculate_similarity(
        cv_skills_embedding,
        req_embedding
        )

    # Compare preferred skills category
    if cv_skills_embedding and pref_embedding:
        results['preferred_skills']['score'] = calculate_similarity(
            cv_skills_embedding,
            pref_embedding
        )

    return results

def compute_final_score(similarity, required, preferred, experience, required_experience, weights=None):
    if weights is None:
        weights = {'embedding': 0.5, 'required': 0.25, 'preferred': 0.15 , 'experience': 0.1}
    
    return (
        weights['embedding'] * similarity +
        weights['required'] * required +
        weights['preferred'] * preferred +
        weights['experience'] * (1 if float(experience or 0) >= float(required_experience or 0) else 0)
    )