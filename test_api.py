import requests
import time
import os

BASE_URL = 'http://127.0.0.1:5000'
session = requests.Session()

# 1. Login
session.post(f"{BASE_URL}/login", data={"email":"demo@example.com", "password":"demo123"})

# 2. Upload
test_dir = "/Users/rohangarg/Desktop/AI_Resume_Screening_System/example_resumes/test_batch"
files = []
for filename in os.listdir(test_dir):
    if filename.endswith(".txt"):
        files.append(('resumes', open(os.path.join(test_dir, filename), 'rb')))

data = {
    "job_description": "Looking for a Senior Python Developer with experience in machine learning, NLP, REST APIs, Docker, and AWS. Must have strong problem solving and communication skills."
}

print("Uploading 10 distinct resumes...")
res = session.post(f"{BASE_URL}/upload", data=data, files=files)

# 3. Start Analysis
print("Starting analysis...")
res = session.post(f"{BASE_URL}/start-analysis")
job_id = res.json()['job_id']

# 4. Poll
while True:
    status_res = session.get(f"{BASE_URL}/analysis-status/{job_id}").json()
    print(status_res['message'])
    if status_res['status'] in ['done', 'error']:
        break
    time.sleep(1)

# 5. Get Results
print("\nFinal Results from server (proving distinct scores):")
# The server stores results in the _job_store dict. Instead of parsing HTML, we can just print it.
# Wait, the best way to see the html is to just fetch the results page and find the scores.
res = session.get(f"{BASE_URL}/results")
html = res.text
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
rows = soup.find_all('tr')
for row in rows[1:]: # skip header
    cols = row.find_all('td')
    if len(cols) >= 3:
        name = cols[1].text.strip()
        score = cols[2].text.strip()
        skills = cols[3].text.strip()
        print(f"{name.ljust(30)} | Score: {score.ljust(10)} | {skills}")
