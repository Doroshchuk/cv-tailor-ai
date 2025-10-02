---
layout: post
title: "Project Update — Introduced Rescanning Workflow + SDET Repo Separation"
---

✅ Learning Progress
1. Completed the **Data Structures Crash Course** on AlgoExpert and solved 14 easy algo tasks, reinforcing foundational problem-solving skills.   
2. Created a dedicated repo — [SDET Framework Lab](https://github.com/Doroshchuk/sdet-framework-lab) — to keep CV Tailor AI focused purely on product development.  
   - **Note:** further updates on my **SDET upskilling journey** (AlgoExpert, LeetCode, framework design exercises, SQL drills) will be shared in the SDET Framework Lab repo and on its GitHub Pages site.

💻 Project Progress
1. 🔧 **Refactoring & Componentization**
- Refactored `DashboardPage` to delegate scan functionality to the new `NewScanComponent`, improving clarity and code reuse.  
- Introduced `NewScanComponent` to encapsulate resume upload and scanning logic.  
- Enhanced `MatchReportPage` with `NewScanComponent` integration and streamlined metric processing.  

2. 🕒 **Reliability Improvements**
- Increased timeout duration for visibility checks in `JobscanReportModal` from 3000ms to 5000ms. 
- Added wait functionality for loading overlay in `NewScanComponent` to ensure stable scanning workflow.  
- Added `Session` class for better resource handling during browser interactions.  

3. 📄 **Resume Tailoring Enhancements**
- Refactored `write_to_file` in `TailoredResumeLite` to return a `Path` object for consistency.  
- Fixed `SkillsAnalyzerComponent` to include whitelisted skills in support checks, improving accuracy.  
- Reintroduced `professional_development_list` in `Resume` and `TailoredResumeLite` classes.  
- Added `ResumeExporter` class for exporting resumes to **DOCX/PDF**.  
- Added `FileFormat` enum for cleaner output handling.  

4. 🧠 **Workflow Overhaul**
- Updated `JobscanScraper` to shift from resume scanning → resume tailoring workflow.  
- Integrated `TailorAIService` directly into the flow for end-to-end tailored resume generation.  
- Improved `main.py` to leverage new exporting, session management, and tailored workflow features.  
- Enhanced prompt instructions + resume model to track **keyword coverage**, ensuring all job requirements are met.  

🔄 What’s Next
1. **Improve the rescan process** — extend current workflow to allow multiple rescans until a minimum target score is reached, making the tailoring loop more reliable.  
2. **Review and refactor existing functionality** for maintainability and consistency across the tailoring and scraping pipeline.  