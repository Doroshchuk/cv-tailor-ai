---
layout: post
title: "Project Update — AI-Powered Resume Tailoring"
---

✅ Learning Progress
1. Advanced through more than half of the Software Engineering Tools section in the ProgrammingExpert course.

💻 Project Progress
🔹 Refactor: Migration to Pydantic Models & Improved Resume Parsing
1. Added a structured Resume model with Pydantic classes (Header, ProfessionalSummary, ProfessionalExperience, Education, Degree).
2. Refactored ResumeParser to use Pydantic models instead of raw dictionaries.
3. Updated settings.json field names (path_to_positions_file → positions_file, path_to_job_details_file → job_details_file).
4. Moved ConfigManager from utils to services directory.
5. Added new path utilities for resume and Jobscan file management.
6. Updated imports to use absolute paths across the codebase.
7. Enhanced JobscanMatchReport with improved file writing using path utilities.
8. Simplified main.py to use the new parsing workflow with structured models.
9. Added OpenAI API key support to ConfigManager.
10. Updated helper functions to use Path objects instead of strings.

🔹 Implemented AI-Powered Resume Tailoring with OpenAI Integration
1. Added a complete CV tailoring pipeline with TailorAIService and OpenAI client.
2. Created a privacy-safe resume model hierarchy (ResumeLite, TailoredResumeLite).
3. Integrated Jobscan keyword analysis into the AI tailoring workflow.
4. Added comprehensive ATS-optimized prompt instructions system.
5. Implemented structured JSON schema validation for AI responses.
6. Added configurable prompt management with external JSON instructions.
7. Updated the main workflow to include AI tailoring after Jobscan analysis.
8. New AI workflow: Parse Resume → Jobscan Analysis → Extract Keywords → AI Tailor → Output
9. Note: This is a basic version, pending debugging & refactor.

🔄 What’s Next
1. Debug and refactor the AI tailoring workflow to stabilize the pipeline.
2. Finalize the Software Engineering Tools section in the ProgrammingExpert course.
3. Expand prompt schema and tailoring logic to support more nuanced keyword coverage and optional additions.
4. Implement rescanning to validate tailored CV versions against Jobscan and measure improvements.