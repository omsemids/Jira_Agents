# from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
# from dotenv import load_dotenv
# import pdfplumber
# import os

# load_dotenv()

# def extract_prd_text() -> dict:
#     file_path = "Healthcare_PRD.pdf"
#     text = ""
#     if not os.path.exists(file_path):
#         print(f"File '{file_path}' not found in {os.getcwd()}")
#         return {"prd_text": ""}
#     with pdfplumber.open(file_path) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return {"prd_text": text}

# claims_processing_agent = LlmAgent(
#     name="ClaimsProcessingAgent",
#     model="gemini-1.5-flash",
#     instruction="""
# You are a JIRA story writing assistant for the product team.
# Focus ONLY on **Claims Processing** requirements in the PRD below (claims intake, payment integrity, etc).
# Write 2-3 well-structured JIRA user stories in this format (but do NOT use JSON):

# ---
# **Story {n}: {Title}**

# - **Description:** As a {persona}, I want to {do something} so that {business value}.
# - **Acceptance Criteria:**
#   1. ...
#   2. ...
# - **Stakeholders:** ...
# - **Regulatory Reference:** ...
# - **Priority:** High/Medium/Low

# ---

# Do not invent features, and do not include requirements from other domains.
# Write the stories as markdown or plain text for humans to read. Output only the stories.

# PRD TEXT:
# {prd_text}
# """,
#     tools=[extract_prd_text],
#     output_key="claims_processing_stories"
# )



# eligibility_agent = LlmAgent(
#     name="EligibilityAgent",
#     model="gemini-1.5-flash",
#     instruction="""
# You are a JIRA story writing assistant for the product team.
# Focus ONLY on **Eligibility Verification** requirements in the PRD below (insurance/member eligibility, 270/271).
# Write 2-3 well-structured JIRA user stories in this format (but do NOT use JSON):

# ---
# **Story {n}: {Title}**

# - **Description:** As a {persona}, I want to {do something} so that {business value}.
# - **Acceptance Criteria:**
#   1. ...
#   2. ...
# - **Stakeholders:** ...
# - **Regulatory Reference:** ...
# - **Priority:** High/Medium/Low

# ---

# Do not invent features, and do not include requirements from other domains.
# Write the stories as markdown or plain text for humans to read. Output only the stories.

# PRD TEXT:
# {prd_text}
# """,
#     tools=[extract_prd_text],
#     output_key="eligibility_stories"
# )



# preauth_agent = LlmAgent(
#     name="PreAuthAgent",
#     model="gemini-1.5-flash",
#     instruction="""
# You are a JIRA story writing assistant for the product team.
# Focus ONLY on **Pre-authorization Workflows** in the PRD below (clinical review, authorization codes, etc).
# Write 2-3 well-structured JIRA user stories in this format (but do NOT use JSON):

# ---
# **Story {n}: {Title}**

# - **Description:** As a {persona}, I want to {do something} so that {business value}.
# - **Acceptance Criteria:**
#   1. ...
#   2. ...
# - **Stakeholders:** ...
# - **Regulatory Reference:** ...
# - **Priority:** High/Medium/Low

# ---

# Do not invent features, and do not include requirements from other domains.
# Write the stories as markdown or plain text for humans to read. Output only the stories.

# PRD TEXT:
# {prd_text}
# """,
#     tools=[extract_prd_text],
#     output_key="preauth_stories"
# )



# provider_data_agent = LlmAgent(
#     name="ProviderDataAgent",
#     model="gemini-1.5-flash",
#     instruction="""
# You are a JIRA story writing assistant for the product team.
# Focus ONLY on **Provider Data Management** requirements in the PRD below (onboarding, credentialing, NPI validation, taxonomy codes).
# Write 2-3 well-structured JIRA user stories in this format :

# ---
# **Story {n}: {Title}**

# - **Description:** As a {persona}, I want to {do something} so that {business value}.
# - **Acceptance Criteria:**
#   1. ...
#   2. ...
# - **Stakeholders:** ...
# - **Regulatory Reference:** ...
# - **Priority:** High/Medium/Low

# ---

# Do not invent features, and do not include requirements from other domains.
# Write the stories as markdown or plain text for humans to read. Output only the stories.

# PRD TEXT:
# {prd_text}
# """,
#     tools=[extract_prd_text],
#     output_key="provider_data_stories"
# )



# system_rules_agent = LlmAgent(
#     name="SystemRulesAgent",
#     model="gemini-1.5-flash",
#     instruction="""
# You are a JIRA story writing assistant for the product team.
# Focus ONLY on **System Rules & General Business Requirements** in the PRD below (business logic, security, access, non-functional requirements).
# Write 2-3 well-structured JIRA user stories in this format (but do NOT use JSON):

# ---
# **Story {n}: {Title}**

# - **Description:** As a {persona}, I want to {do something} so that {business value}.
# - **Acceptance Criteria:**
#   1. ...
#   2. ...
# - **Stakeholders:** ...
# - **Regulatory Reference:** ...
# - **Priority:** High/Medium/Low

# ---

# Do not invent features, and do not include requirements from other domains.
# Write the stories as markdown or plain text for humans to read. Output only the stories.

# PRD TEXT:
# {prd_text}
# """,
#     tools=[extract_prd_text],
#     output_key="system_rules_stories"
# )



# parallel_healthcare_agent = ParallelAgent(
#     name="HealthcareParallelAgent",
#     sub_agents=[
#         claims_processing_agent,
#         eligibility_agent,
#         preauth_agent,
#         provider_data_agent,
#         system_rules_agent
#     ],
#     description="Runs healthcare subdomain agents in parallel to generate specialized JIRA stories."
# )

# merger_agent = LlmAgent(
#     name="SynthesisAgent",
#     model="gemini-1.5-flash",
#     instruction="""
# Combine all the JIRA user stories below into a **single, well-structured report** for a healthcare product team. 
# Group stories under bold markdown headings for each subdomain.

# # JIRA User Stories for Healthcare PRD

# ## Claims Processing
# {claims_processing_stories}

# ## Eligibility Verification
# {eligibility_stories}

# ## Pre-authorization Workflows
# {preauth_stories}

# ## Provider Data Management
# {provider_data_stories}

# ## System Rules & Business Requirements
# {system_rules_stories}

# Do not invent any content. Only output the structured, human-readable report.
# """,
#     description="Combines JIRA user stories from all healthcare subdomains into a single readable report."
# )

# root_agent = SequentialAgent(
#     name="HealthcareJiraPipeline",
#     sub_agents=[parallel_healthcare_agent, merger_agent],
#     description="Coordinates parallel healthcare JIRA story generation and merges them into a human-friendly output."
# )

import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

pdf_text = extract_text_from_pdf('Health_PRD.pdf')
print(pdf_text)
