Project Title

AI Resume Analyzer – AI-Powered ATS Resume Screening System

Project Description

The AI Resume Analyzer is a full-stack web application that helps job seekers evaluate their resumes against a job description (JD). It automatically extracts text from uploaded PDF resumes, compares the resume with the job description, calculates an ATS (Applicant Tracking System) score, identifies missing skills, and provides AI-powered suggestions to improve the resume.

The application also includes secure user authentication, resume analysis history, MongoDB integration, and AI support for generating personalized recommendations.

Problem Statement

Many candidates are rejected because their resumes are not optimized for Applicant Tracking Systems (ATS). This project helps users understand how well their resume matches a specific job description and what improvements they can make before applying.

Objectives
Analyze resumes automatically.
Compare resumes with job descriptions.
Calculate an ATS compatibility score.
Identify missing skills and keywords.
Provide AI-generated improvement suggestions.
Store user history for future reference.
Tech Stack
Frontend
HTML5
CSS3
JavaScript
Backend
Python
FastAPI
Database
MongoDB
AI
OpenAI API (optional)
Local AI fallback
Other Libraries
Uvicorn
PDF parsing library (such as PyPDF2 or pdfplumber)
JWT authentication
REST APIs
System Architecture
User
   ↓
Frontend (HTML/CSS/JavaScript)
   ↓
FastAPI Backend
   ↓
Resume PDF Extraction
   ↓
Resume Text Processing
   ↓
Job Description Processing
   ↓
ATS Matching Algorithm
   ↓
AI Recommendation Engine
   ↓
MongoDB Database
   ↓
Frontend Dashboard
Project Workflow
Step 1

User registers and logs into the application.

↓

Step 2

User uploads a PDF resume.

↓

Step 3

Backend extracts text from the PDF.

↓

Step 4

User pastes the Job Description (JD).

↓

Step 5

Backend compares the resume and JD.

↓

Step 6

ATS score is calculated.

↓

Step 7

Missing skills are identified.

↓

Step 8

AI generates resume improvement suggestions.

↓

Step 9

Analysis results are displayed.

↓

Step 10

Results are stored in MongoDB for future reference.

Key Features
User Registration
Login Authentication
PDF Resume Upload
Resume Text Extraction
ATS Score Calculation
Resume and JD Comparison
Missing Skill Detection
AI Resume Suggestions
Resume Analysis Dashboard
Analysis History
MongoDB Storage
REST API
Responsive UI
ATS Score Calculation

The application extracts skills from the resume and compares them with the required skills in the job description.

Example:

Resume Skills

Python
JavaScript
MongoDB
FastAPI

Job Description

Python
FastAPI
React
Docker
Git

Matched Skills

Python
FastAPI

Missing Skills

React
Docker
Git

The ATS score is calculated using the ratio of matched required skills to the total required skills. More advanced implementations can also consider education, experience, certifications, and keyword relevance.

Database

MongoDB stores:

User Accounts
Login Information
Resume Analysis History
ATS Scores
Uploaded Resume Metadata
AI Recommendations
REST APIs

Typical APIs include:

User Registration
User Login
Resume Upload
Resume Analysis
ATS Score Retrieval
Dashboard History
Security
JWT Authentication
Password Hashing
Input Validation
File Type Validation
Secure REST APIs
Folder Structure
AI Resume Analyzer
│
├── app
│   ├── main.py
│   ├── routes
│   ├── models
│   ├── services
│   ├── static
│   └── templates
│
├── requirements.txt
├── README.md
├── .env
└── .venv
Future Enhancements
Resume ranking for multiple candidates
Multi-language resume analysis
Voice-based interview preparation
AI interview question generation
LinkedIn profile analysis
Job recommendation system
Cloud deployment
Email reports
Admin dashboard
Analytics charts
