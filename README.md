# Healthcare JIRA Story Generator

This project uses Google ADK (Application Development Kit) with Gemini LLM to automatically generate structured JIRA user stories from a healthcare Product Requirements Document (PRD).

---

## Features

- Extracts text from a PDF PRD document.
- Runs multiple specialized agents in parallel, each focusing on a healthcare subdomain:
  - Claims Processing
  - Eligibility Verification
  - Pre-authorization Workflows
  - Provider Data Management
  - System Rules & General Business Requirements
- Merges the outputs into a single structured JSON report with JIRA user stories.
- Saves the final output as a JSON file locally.

---

## Prerequisites

- Python 3.10+
- Google ADK and Gemini API access with valid API keys.
- Required Python packages:
  - `google-adk`
  - `google-genai`
  - `PyPDF2`
  - `python-dotenv`

---

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd <repo-folder>
