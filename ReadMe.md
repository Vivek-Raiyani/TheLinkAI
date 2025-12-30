# Requirements
Python

Python 3.9+

# Virtual Environment
`
python -m venv venv
venv\Scripts\activate
`

# Setup Envfile
`
GEMINI_API_KEY = "Your_API_KEY"
`

# Python Dependencies
Install all dependencies using:
`
pip install -r requirements.txt
`

# Running the Application
`
uvicorn app.main:app --reload

http://127.0.0.1:8000/docs
`
