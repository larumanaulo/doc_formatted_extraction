import json
import os
from openai import OpenAI
from config import BASE_PROMPT, COVERAGE_DATA_EXTRACTION_PROMPT, DRIVER_SCHEDULE_DATA_EXTRACTION_PROMPT, VEHICLE_SCHEDULE_DATA_EXTRACTION_PROMPT, EVALUATION_PROMPT, REFINEMENT_PROMPT
from schema import COVERAGE_OUTPUT_SCHEMA, DRIVER_SCHEDULE_OUTPUT_SCHEMA, VEHICLE_SCHEDULE_OUTPUT_SCHEMA, EVALUATION_OUTPUT_SCHEMA, REFINEMENT_OUTPUT_SCHEMA
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def formatted_extraction_api(data, action):

    if action == "coverage":
        schema = COVERAGE_OUTPUT_SCHEMA
        prompt = COVERAGE_DATA_EXTRACTION_PROMPT.replace("{{data}}", data)
    elif action == "driver_schedule":
        schema = DRIVER_SCHEDULE_OUTPUT_SCHEMA
        prompt = DRIVER_SCHEDULE_DATA_EXTRACTION_PROMPT.replace("{{data}}", data)
    elif action == "vehicle_schedule":
        schema = VEHICLE_SCHEDULE_OUTPUT_SCHEMA
        prompt = VEHICLE_SCHEDULE_DATA_EXTRACTION_PROMPT.replace("{{data}}", data)
    else:
        raise ValueError("Invalid action specified")

    messages = [
        { "role": "system", "content": BASE_PROMPT },
        { "role": "user", "content": prompt }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            response_format={ 
                "type": "json_schema", 
                "json_schema": {
                    "name": schema["name"],
                    "description": schema["description"],
                    "schema": schema,
                }
            }
        )

        content = response.choices[0].message.content
        extracted_data = json.loads(content)
        return extracted_data
    except Exception as e:
        print(f"API call failed: {e}")
    return None


def evaluate_extraction(document_text, extracted_json):
    prompt = EVALUATION_PROMPT.replace("{{DOCUMENT_TEXT}}", document_text)
    prompt = prompt.replace("{{EXTRACTED_JSON}}", json.dumps(extracted_json, indent=2))

    messages = [
        {"role": "system", "content": "You are a QA evaluator."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            response_format={ 
                    "type": "json_schema", 
                    "json_schema": {
                        "name": EVALUATION_OUTPUT_SCHEMA["name"],
                        "description": EVALUATION_OUTPUT_SCHEMA["description"],
                        "schema": EVALUATION_OUTPUT_SCHEMA,
                    }
                }
        )
        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print(f"Error calling OpenAI API (evaluate_extraction): {e}")
        return {
            "score": 0,
            "summary": "Evaluation failed due to API error.",
            "issues": [str(e)]
        }


def suggest_prompt_improvements(action, evaluation_summary, issues):

    if action == "coverage":
        original_prompt = COVERAGE_DATA_EXTRACTION_PROMPT
    elif action == "driver_schedule":
        original_prompt = DRIVER_SCHEDULE_DATA_EXTRACTION_PROMPT
    elif action == "vehicle_schedule":
        original_prompt = VEHICLE_SCHEDULE_DATA_EXTRACTION_PROMPT
    else:
        raise ValueError("Invalid action specified")
    

    prompt = REFINEMENT_PROMPT\
        .replace("{{EVALUATION_SUMMARY}}", evaluation_summary)\
        .replace("{{ISSUE_LIST}}", json.dumps(issues, indent=2))\
        .replace("{{ORIGINAL_PROMPT}}", original_prompt)

    messages = [
        {"role": "system", "content": "You are a prompt refinement expert."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            response_format={
                "type": "json_schema", 
                "json_schema": {
                    "name": REFINEMENT_OUTPUT_SCHEMA["name"],
                    "description": REFINEMENT_OUTPUT_SCHEMA["description"],
                    "schema": REFINEMENT_OUTPUT_SCHEMA,
                }
            }
        )
        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print(f"Error calling OpenAI API (suggest_prompt_improvements): {e}")
        return {
            "suggestions": [f"Failed to generate suggestions: {str(e)}"]
        }