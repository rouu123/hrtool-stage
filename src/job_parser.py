import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import ollama

load_dotenv()

class JobParser:
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_API_HOST')
        self.ollama_model = os.getenv('OLLAMA_MODEL')
        self.embedder = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

    def parse_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Extract structured data and embed skills from job description"""
        prompt = f"""
        Analyze this job description and extract the following as JSON:
        {{
            "job_title": str,
            "wanted skills": List[str],
            "required_experience": float
        }}

        Rules:
        1. Return only the JSON object, no other text
        2. For skills sections: DO NOT give me FULL SENTENCES INSTEAD EXTRACT THE SKILLS from the text and return them as a flat list.
         include ALL items (no limit in length of the list) but make it concise (NOT SENTENCES)
        example: for 'Experience with machine learning frameworks (e.g., scikit-learn, TensorFlow*)', return ["machine learning","scikit-learn", "TensorFlow"]
        3. For grouped skills like "web frameworks (Django, Flask)", return ["Django", "Flask"]
        4. required_experience should be a float with only one number after the decimal (e.g., 3.0 or 3.5)
        5. Extract ALL information available, ALL specific skills, the lists are not limited in length

        

        Job Description:
        {jd_text}
        """
        try:
            # Get structured data
            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                format="json",
                options={
                    "temperature": 0.2,
                    "num_ctx": 8192
                }
            )
            job_data = json.loads(response['response'])            
            # Generate all required embeddings
            job_data = self._generate_embeddings(job_data)

            return job_data

        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON")
            return self._empty_job_data()
        except Exception as e:
            print(f"Job parsing failed: {str(e)}")
            return self._empty_job_data()

    def _generate_embeddings(self, job_data: Dict) -> Dict:
        """Generate all required embeddings using nomic-embed-text"""
        def embed(skills: List[str]) -> List[float] | None:
            if not skills:
                return None
            text = " | ".join(skills)
            return self.embedder.encode(text).tolist()

        job_data['wanted_skills_embedding'] = embed(job_data['wanted skills'])

        return job_data

    def _empty_job_data(self) -> Dict[str, Any]:
        """Return empty job data structure"""
        return {
            'job_title': '',
            'wanted skills': [],
            'required_experience': 0.0,
            'wanted_skills_embedding': None,
        }
