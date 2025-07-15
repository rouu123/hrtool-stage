import numpy as np
from src.cv_parser import CVParser
from src.job_parser import JobParser
import json
import glob
import os
from src.matcher import calculate_similarity, calculate_category_matches ,compute_final_score


def main():
    # Initialize parsers
    print("Initializing parsers...")
    cv_parser = CVParser()
    job_parser = JobParser()

    # File paths (replace with your actual files)
    cv_files = glob.glob("./ar/*.pdf")
    jd_text = str("""


📢 مدير وسائل التواصل الاجتماعي
✅ المتطلبات الأساسية:
خبرة لا تقل عن سنتين

خبرة في إدارة وسائل التواصل الاجتماعي

معرفة ببرنامجي Adobe Photoshop وAdobe Illustrator

مهارات في إنشاء المحتوى

استخدام Google Analytics

⭐ المهارات المفضلة:
مهارات في تحرير الفيديو

خبرة في التصوير السينمائي



""")


    # Parse job description

    print("\nParsing Job Description...")
    job_data = job_parser.parse_job_description(jd_text)
    print("Job Data:")
    print("Required Skills:", json.dumps(job_data.get('required_skills', []), indent=2))
    print("Preferred Skills:", json.dumps(job_data.get('preferred_skills', []), indent=2))

    # Parse cvs

    all_results = []

    for cv_path in cv_files:
        print(f"\nParsing CV: {cv_path}")
        cv_data = cv_parser.parse_cv(cv_path)
        print(json.dumps(cv_data['skills'], indent=2)) 

        if not cv_data.get('skills_embedding'):
            print(f"⚠️ Skipping {cv_path} - no skills embedding")
            continue



    # Calculate matches
        if cv_data.get('skills_embedding') and job_data.get('skills_embedding'):
            similarity = calculate_similarity(
                cv_data['skills_embedding'],
                job_data['skills_embedding']
            )
            print(f"\n📊 Skills Embedding Similarity: {similarity:.1%}")

            category_matches = calculate_category_matches(cv_data, job_data)
            required_match = category_matches['required_skills']['score']
            preferred_match = category_matches['preferred_skills']['score']

            experience= cv_data.get('total_experience', 0)
            required_experience = job_data.get('required_experience', 0)

            weighted_score = compute_final_score(similarity, required_match, preferred_match, experience, required_experience)
            all_results.append({
                'name': cv_data.get('name', 'N/A name'),
                'cv_path': cv_path,
                'similarity': similarity,
                'score': weighted_score,
                'required_match': required_match,
                'preferred_match': preferred_match,
                'experience': experience
        })

    ranked = sorted(all_results, key=lambda x: x['score'], reverse=True)
    print("\n📋 Ranked CVs:")
    for i, result in enumerate(ranked, 1):
        print(f"{i}. {os.path.basename(result['cv_path'])}")
        print(f"   🔹 Total Score: {result['score']:.1%}")
        print(f"   🔸 similarity: {result['similarity']:.1%}")
        print(f"   🔸 Required Skills Match: {result['required_match']:.1%}")
        print(f"   🔸 Preferred Skills Match: {result['preferred_match']:.1%}")
        print(f"   🔸 Experience: {result['experience']} years\n")
        print("--------------------------------------------------")
        print("\n")

if __name__ == "__main__":
    main()