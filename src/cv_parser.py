import fitz  # PyMuPDF
import ollama
import os
import json
from dotenv import load_dotenv
from typing import Dict, Any
from sentence_transformers import SentenceTransformer

load_dotenv()

class CVParser:
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_API_HOST')
        self.ollama_model = os.getenv('OLLAMA_MODEL')
        self.embedder = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)
        
    def parse_cv(self, pdf_path: str) -> Dict[str, Any]:
        # Extract raw text from PDF
        doc = fitz.open(pdf_path)
        raw_text = "\n".join(page.get_text() for page in doc)
        
        prompt = f"""
        Analyze this CV and return structured JSON with:
        - Personal info (name, email, phone)
        - All skills (from any section)
        - Work experience
        - Education
        - Calculated total experience
        
        Extraction Rules:
        1. Extract ALL skills mentioned anywhere in the CV
        2. For skills sections: include ALL items (no limit in length of the list) but make it concise (NOT SENTENCES) 
        example: ["Python", "JavaScript", "cloud computing", "machine learning"]
        3. For experience sections: extract technologies/tools used
        4. For education: extract relevant coursework/skills
        5. Return flat lists (no nested groupings)
        
        Output Format:
        {{
            "name": str,
            "email": str,
            "phone": str,
            "skills": List[str],
            "experience": List[{{"company": str, "position": str, "duration": str}}],
            "education": List[{{"degree": str, "institution": str, "year": int}}],
            "total_experience": float
        }}
        
        CV Content:
        {raw_text}
        """
        
        try:
            # Step 1: Extract structured data from LLM
            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                format="json",
                options={
                    "temperature": 0.2,
                    "num_ctx": 8192
                }
            )
            cv_data = json.loads(response['response'])

            # Step 2: Generate embedding only if skills are present
            skills = cv_data.get("skills", [])
            if skills:
                skills_prompt = " | ".join(skills)
                embedding = self.embedder.encode(skills_prompt)
                cv_data["skills_embedding"] = embedding.tolist()
            else:
                cv_data["skills_embedding"] = None

            return cv_data
        
        except Exception as e:
            print(f"CV parsing failed: {e}")
            return {
                'name': '',
                'email': '',
                'phone': '',
                'skills': [],
                'skills_embedding': None,
                'experience': [],
                'education': [],
                'total_experience': 0
            }
