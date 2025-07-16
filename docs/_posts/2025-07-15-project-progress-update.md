---
layout: post
title: "Project Progress Update: CV Tailor AI"
---

Over the past week, I’ve made significant improvements to the project’s structure, configuration management, and maintainability. These changes lay a strong foundation for future features and easier collaboration.

## 🗂️ Project Structure Refactor
- Reorganized the codebase into logical packages (`core/`, `utils/`, `models/`, etc.) for better scalability.
- Adopted a modular structure to make it easier to add new features and maintain the code as the project grows.

## ⚙️ Centralized Configuration
- Introduced a `settings.json` file for all major configuration options (file paths, parsing rules, etc.).
- Implemented a Singleton-based `ConfigManager` to ensure consistent configuration access throughout the app.
- Added support for environment variables via a `.env` file.

## 🧩 Improved Maintainability
- Replaced hardcoded values with configuration-driven logic.
- Enhanced type safety and validation using Pydantic models.
- Improved logging and error handling for easier debugging.

## 🔜 Next Steps
- **Upskill in Playwright:**  
  I am currently taking a Playwright course to strengthen my skills in browser automation and testing. This knowledge will be instrumental in developing scraping functionality for LinkedIn and Jobscan, allowing for automated data extraction to enhance the resume tailoring process.
