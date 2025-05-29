import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import PyPDF2
import json

load_dotenv()

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# ---- CONFIG ----
PDF_PATH = "Health_PRD.pdf"
MAX_PRD_LEN = 10000
APP_NAME = "jira_pipeline"
USER_ID = "test_user"
SESSION_ID = "jira_session"

# ---- Extracting and Truncate PRD ----
prd_text = extract_text_from_pdf(PDF_PATH)
print(f"Extracted {len(prd_text)} characters from PRD.")

if len(prd_text) > MAX_PRD_LEN:
    prd_text = prd_text[:MAX_PRD_LEN]


# Defining output formate
json_format_str = """
[
  {
    "number": <number, integer>,
    "title": "<Concise story title>",
    "description": "<User story (as a persona, I want... so that...)>",
    "acceptance_criteria": [
      "<criteria 1>",
      "<criteria 2>",
      "... (as many as present)"
    ],
    "stakeholders": "<key stakeholders, comma separated>",
    "regulatory_reference": "<regulatory or compliance codes, if any>",
    "priority": "<High|Medium|Low>"
  }
]
"""

agent_common_instructions = f"""
- Your output must be a single, valid JSON array of user stories (do not wrap in markdown, do not include any extra explanation, do not use trailing commas, do not add comments).
- Every object in the array must have all the fields as in the schema.
- If no stories are present for this subdomain, return an empty JSON array: []
- Do not invent features.
- Only extract actual requirements from the PRD.
- DO NOT output any text before or after the array.
- Format field values as plain strings (do not use markdown in values).
- Acceptance criteria must be a list of strings.

JSON schema (strictly follow this):
{json_format_str}
"""

def build_subagent_instruction(domain_description, prd_text):
    return f"""
You are a JIRA story writing assistant for a healthcare product team.
Extract ONLY {domain_description} requirements from the PRD.
{agent_common_instructions}

PRD CONTENT:
{prd_text}
"""

claims_processing_agent = LlmAgent(
    name="ClaimsProcessingAgent",
    model="gemini-1.5-flash",
    instruction=build_subagent_instruction(
        "Claims Processing (claims intake, payment integrity, claims adjudication, etc)",
        prd_text
    ),
    output_key="claims_processing_stories"
)

eligibility_agent = LlmAgent(
    name="EligibilityAgent",
    model="gemini-1.5-flash",
    instruction=build_subagent_instruction(
        "Eligibility Verification (member insurance eligibility, EDI 270/271, etc)",
        prd_text
    ),
    output_key="eligibility_stories"
)

preauth_agent = LlmAgent(
    name="PreAuthAgent",
    model="gemini-1.5-flash",
    instruction=build_subagent_instruction(
        "Pre-authorization Workflows (clinical review, auth codes, preauth business rules, etc)",
        prd_text
    ),
    output_key="preauth_stories"
)

provider_data_agent = LlmAgent(
    name="ProviderDataAgent",
    model="gemini-1.5-flash",
    instruction=build_subagent_instruction(
        "Provider Data Management (provider onboarding, credentialing, NPI validation, taxonomy codes)",
        prd_text
    ),
    output_key="provider_data_stories"
)

system_rules_agent = LlmAgent(
    name="SystemRulesAgent",
    model="gemini-1.5-flash",
    instruction=build_subagent_instruction(
        "System Rules & General Business Requirements (business logic, security, access, audit, non-functional requirements)",
        prd_text
    ),
    output_key="system_rules_stories"
)

# ---- PARALLEL AGENT ----
parallel_healthcare_agent = ParallelAgent(
    name="HealthcareParallelAgent",
    sub_agents=[
        claims_processing_agent,
        eligibility_agent,
        preauth_agent,
        provider_data_agent,
        system_rules_agent
    ],
    description="Runs healthcare subdomain agents in parallel to generate specialized JIRA stories."
)

# ---- MERGE AGENT ----
merger_agent = LlmAgent(
    name="SynthesisAgent",
    model="gemini-1.5-flash",
    instruction="""
You are an expert JIRA pipeline agent.
Combine all the JIRA user stories below into a SINGLE, valid JSON object (do not wrap in markdown, do not add extra explanation).
The format must be:

{
  "Claims Processing": <claims_processing_stories>,
  "Eligibility Verification": <eligibility_stories>,
  "Pre-authorization Workflows": <preauth_stories>,
  "Provider Data Management": <provider_data_stories>,
  "System Rules & Business Requirements": <system_rules_stories>
}

Where each value is a JSON array of stories as specified in the schema. If a subdomain is empty, use [].

**Rules:**
- Do NOT include any prose or text before/after.
- Do NOT use comments or markdown.
- Output strictly valid JSON.
- Do not invent any stories.

START OUTPUT NOW.
""",
    description="Combines JIRA user stories from all healthcare subdomains into a single JSON object."
)

# ---- ROOT PIPELINE ----
root_agent = SequentialAgent(
    name="HealthcareJiraPipeline",
    sub_agents=[parallel_healthcare_agent, merger_agent],
    description="Coordinates parallel healthcare JIRA story generation and merges them into a JSON output."
)

# ---- SESSION SETUP ----
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

# ---- AGENT CALLER ----
def call_agent():
    content = types.Content(role='user', parts=[types.Part(text="Generate JIRA stories for all healthcare subdomains in strict valid JSON only. Do not add markdown or explanation. All subdomains must be present as arrays.")])
    events = runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    )
    for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text
            print("\n==== Final Agent JSON Response ====\n")
            print(response_text)
            try:
                structured_json = json.loads(response_text)
                with open("jira_output.json", "w", encoding="utf-8") as f:
                    json.dump(structured_json, f, ensure_ascii=False, indent=2)
                print("Saved output to jira_output.json")
            except Exception as e:
                print("Error parsing JSON output! Saving as text.")
                with open("jira_output_raw.txt", "w", encoding="utf-8") as f:
                    f.write(response_text)

if __name__ == "__main__":
    call_agent()
