import os
import random

resumes = [
    ("Alice Smith", "Python Developer", "5 years experience. ML, NLP, Docker, AWS. Built scalable APIs.", [ "Python", "ML", "NLP", "Docker", "AWS", "REST APIs" ], 1),
    ("Bob Johnson", "Data Scientist", "3 years. Focus on data analysis, pandas, numpy, SQL. Some machine learning.", [ "Python", "SQL", "Pandas", "Machine Learning" ], 0.5),
    ("Charlie Brown", "DevOps Engineer", "10 years. Expert in Docker, Kubernetes, AWS, CI/CD pipelines.", [ "Docker", "Kubernetes", "AWS", "CI/CD", "Linux" ], 0.6),
    ("Diana Prince", "Senior Backend Engineer", "7 years. Python, Java, REST APIs, Microservices, AWS. Strong problem solving.", [ "Python", "Java", "REST APIs", "AWS", "Microservices" ], 0.8),
    ("Evan Wright", "Frontend Developer", "4 years. React, JavaScript, CSS, HTML. UI/UX focus.", [ "React", "JavaScript", "HTML", "CSS" ], 0.1),
    ("Fiona Gallagher", "Fullstack Python Dev", "6 years. Django, React, REST APIs, Docker, AWS. Good teamwork.", [ "Python", "Django", "React", "Docker", "AWS", "REST APIs" ], 0.9),
    ("George Miller", "AI Researcher", "8 years. Deep learning, Transformers, NLP, PyTorch, TensorFlow.", [ "Python", "NLP", "PyTorch", "TensorFlow", "Deep Learning" ], 0.7),
    ("Hannah Abbott", "Project Manager", "5 years managing software projects. Agile, Scrum, Jira. Excellent communication.", [ "Agile", "Scrum", "Jira", "Management" ], 0.2),
    ("Ian Malcolm", "Cloud Architect", "12 years. AWS certified. Terraform, Python scripting, Docker.", [ "AWS", "Terraform", "Python", "Docker" ], 0.6),
    ("Julia Child", "Junior Python Developer", "1 year. Python, Flask, basic REST APIs. Eager to learn.", [ "Python", "Flask", "REST APIs" ], 0.4),
]

output_dir = "/Users/rohangarg/Desktop/AI_Resume_Screening_System/example_resumes/test_batch"

for i, (name, title, exp, skills, score) in enumerate(resumes):
    filename = f"resume_{i+1}_{name.replace(' ', '_').lower()}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as f:
        f.write(f"{name}\n{title}\n\nExperience:\n{exp}\n\nSkills:\n{', '.join(skills)}\n\nSoft Skills: Communication, Problem Solving, Teamwork")
    print(f"Created {filename}")
