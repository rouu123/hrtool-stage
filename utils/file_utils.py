import tempfile
import os

def save_temp_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name

def delete_temp_file(path):
    try:
        os.unlink(path)
    except Exception:
        pass
