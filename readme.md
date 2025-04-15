## Project Summary

The main idea of this prompt strategy is that we analyze each section one at a time **coverage, drivers, and vehicles** in order to be as precise as possible in what we are asking the LLM to extract. The model is given full context (the entire document text), but is asked to perform only a single specific task at a time to maintain focus and avoid diluted or mixed data extraction.

For each section, we run a base system prompt and a section-specific user prompt. This executes the extraction task for that section.
To ensure the information is accurate and complete, the result of each extraction is evaluated against the target schema. This evaluation returns:
- a score from 0 to 100
- a summary describing completeness and correctness
- a list of specific issues found

Based on the evaluation output, the system uses a second LLM call to suggest prompt improvements tailored to the issues encountered. These suggestions are used to enhance the prompt, and the extraction is re-run. This cycle repeats until either:
- the score meets or exceeds a defined threshold (e.g., 75), or
- the maximum number of retries is reached

If the threshold is not met within the allowed retries, the best-scoring result from all attempts is retained.

This process runs independently for each of the three sections (coverage, drivers, vehicles), and for every document. Once all sections are extracted and validated, the final result is written to a JSON file in the results directory, one file per document.

 - **Prompts Directory** : `./config.py`
 - **Schemas Directory** : `./schema.py`
 - **Example Improvement Logs Directory**: `./logs`



## Prompt Engineering Approach

### 1. **Base Prompt**
Can be found in `./config.py` under **BASE_PROMPT**
- Defines general task and quality standards:
```text
    You are an expert insurance document extraction assistant.

    Your task is to extract structured data from Business Auto insurance documents that vary in layout, terminology, and formatting.

    Instructions:
    - Focus only on the "Business Auto" section (may also be labeled "Automobile").
    - Ignore all other coverages (e.g., Commercial Property, Workers Compensation).
    - Handle variations in terminology (e.g., “Liability Limit” vs. “Business Auto Liability Limit”).
    - Handle optional fields gracefully: if a value is not found, return `null`.
    - Do not infer values only extract what is explicitly stated.
    - Output must conform exactly to the field names and structure provided in the user prompt.
```

### 2. **Data Extraction Prompts**
Each section (coverage, vehicle, driver) has its own prompt, optimized for terminology and layout variations:
- **Coverage Prompt:**
Can be found in `./config.py` under **COVERAGE_DATA_EXTRACTION_PROMPT**
```text
    Task: 
    From this document: 
    -----------------------------------------------------------------
    {{data}}
    -----------------------------------------------------------------

    Extract coverage information from the provided Business Auto Coverage section. Use domain knowledge to handle variations in terminology and layout. 

    Return a JSON object with the following fields:
    - liabilityInsuranceLimit: Liability limit
    - liabilityInsuranceSymbol: Liability symbol
    - medicalPaymentsLimit: Medical Payments limit
    - medicalPaymentsSymbol: Medical Payments symbol
    - uninsuredMotoristLimit: Uninsured Motorist limit
    - uninsuredMotoristSymbol: Uninsured Motorist symbol
    - underinsuredMotoristLimit: Underinsured Motorist limit
    - underinsuredMotoristSymbol: Underinsured Motorist symbol
    - personalInjuryProtectionLimit: Personal Injury Protection limit
    - personalInjuryProtectionSymbol: Personal Injury Protection symbol
    - hiredAutoLimit: Hired Auto limit
    - hiredAutoSymbol: Hired Auto symbol
    - nonOwnedAutoLiabilityLimit: Non-Owned Auto Liability limit
    - nonOwnedAutoLiabilitySymbol: Non-Owned Auto Liability symbol
    - collisionLimit: Collision limit
    - collisionDeductible: Collision deductible
    - comprehensiveLimit: Comprehensive limit
    - comprehensiveDeductible: Comprehensive deductible

    Important Terminology Notes:
    - Liability: May appear as “Combined Single Limit”, “Auto Liability”, “Business Auto Liability”
    - Medical Payments: May be listed as “Med Pay”, “Medical Pay”
    - Uninsured/Underinsured Motorist: May be abbreviated as “UM” and “UIM”
    - Personal Injury Protection: May appear as “PIP”
    - Collision & Comprehensive: May appear as “Physical Damage”, “Other Than Collision”, or “OTC”
    - Symbols may be listed separately from the coverages

    If no coverage or symbol is found for a field, return null.
```
- **Driver Prompt:** 
Can be found in `./config.py` under **DRIVER_SCHEDULE_DATA_EXTRACTION_PROMPT**
```text
    Task: 
    From this document: 
    -----------------------------------------------------------------
    {{data}}
    -----------------------------------------------------------------
    Extract the driver schedule from the provided Business Auto document text.

    Return a JSON object with a key "driverSchedule" which is an array of driver objects with the following fields:
    - fullName: Driver’s full name
    - dateOfBirth: Date of birth
    - licenseNumber: Driver’s license number

    Instructions:
    - Extract all listed drivers.
    - If date of birth or license number are redacted or suppressed, return the value `null`.
    - Section may be titled:
    - “Driver Schedule”
    - “Schedule of Drivers”
    - “Drivers”
    - Do not infer values. Only extract what is explicitly written.
    - If no drivers are listed or the section is blank, return `"driverSchedule": []`.
```
- **Vehicle Prompt:** 
Can be found in `./config.py` under **VEHICLE_SCHEDULE_DATA_EXTRACTION_PROMPT**
```text
    Task: 
    From this document: 
    -----------------------------------------------------------------
    {{data}}
    -----------------------------------------------------------------
    Extract the vehicle schedule from the provided Business Auto document text.

    Return a JSON object with a key "vehicleSchedule" which is an array of vehicle objects with the following fields:

    - year: vehicle year (e.g., "2020")
    - make: vehicle make (e.g., "FORD")
    - model: vehicle model (e.g., "F150")
    - vin: Vehicle Identification Number
    - vehiclePremium: premium associated with this vehicle
    - vehicleCost: vehicle's cost or value

    Instructions:
    - Extract all vehicles listed not just a sample.
    - Return `null` for any missing values (e.g., VIN not listed).
    - Vehicle schedules may appear under different section titles like:
    - “Vehicle Schedule”
    - “Schedule of Autos”
    - “Covered Autos”
    - Some vehicles may appear in tabular form or as blocks of text.
    - Do not infer values. Only return those explicitly listed.
```

---

## Prompt Recursive Evaluation
1. Each section is extracted using a schema-bound prompt.
2. The extracted result is evaluated by the model using a separate QA prompt.
3. The model returns a score 0–100, a list of issues, and a summary.
4. If the score is below threshold (eg, 75), a refinement prompt generates prompt improvement suggestions.
5. The system applies suggested prompt fixes, retries extraction, and re-evaluates, up to a maximum number of retries (eg, 3).
6. After all retries, the result with the highest score is selected.

Can be found in `./config.py` under **EVALUATION_PROMPT**
```text
    You are a senior QA analyst specializing in Business Auto insurance document extraction.

    Your task is to **critically evaluate** whether the structured JSON output accurately reflects the source insurance document text which may use inconsistent layouts, terminology, or abbreviations.

    You are evaluating the extraction based on:

    1. **Completeness** Are all required fields present (even if null)?
    2. **Accuracy** Do the extracted values (e.g., limits, deductibles, VINs) exactly match those in the text?
    3. **Structure** Does the JSON follow the correct schema structure, including nesting and naming?

    Your domain knowledge should include:
    - Common variations in field names (e.g., "Combined Single Limit", "CSL", "Auto Liability")
    - Tabular layouts with or without headers
    - Optional fields like UM/UIM, Medical Payments, or PIP that may be redacted or suppressed
    - Vehicle and driver schedules listed in nonstandard formats

    ### Instructions:
    - Do **not guess or infer** any values evaluate only what is present.
    - Use **minor tolerance** for OCR formatting differences (e.g., "$5000" vs. "5000").
    - Treat missing fields, inaccurate values, or extra hallucinated values as **explicit issues**.
    - Be very specific when reporting mismatches or omissions.

    ### Output Format:
    Return a strict JSON object:
    {
    "score": 0-100,
    "issues": [
        "Missing Field: medicalPaymentsSymbol not extracted.",
        "Mismatch: liabilityInsuranceLimit is $100,000 but should be $1,000,000.",
        "Extra Field: UninsuredMotoristLimit was returned but not found in the document."
    ],
    "summary": "The extraction was structurally valid and mostly complete, but it missed symbols and slightly mismatched liability limits."
    }

    Document Text:
    ---------------------------------------------
    {{DOCUMENT_TEXT}}
    ---------------------------------------------

    Extracted JSON:
    ----------------------------------------------
    {{EXTRACTED_JSON}}
    ----------------------------------------------
```

### Recursive Scoring ExampleRefinement Evaluation
```text
    doc_1.pdf
    Attempt 1 | Score: 65
    Summary: Missed personal injury protection. Wrong liability limit. Extracted extra fields.
    Suggestions:
    - Add: 'CSL' as a synonym for 'Combined Single Limit'.
    - Clarify: 'Symbols may be listed in separate tables.'

    Attempt 2 | Score: 70
    Summary: Still missing some optional fields, but structure improved.
    Suggestions:
    - Add: 'Hired Auto should only be extracted if explicitly stated.'
    - Clarify: 'Driver schedule may appear under various headings.'

    Attempt 3 | Score: 70
    Summary: Symbol mismatches fixed, but limits still not exact.
    ** Best score retained.
```

### Example Refinement Prompt:
Can be found in `./config.py` under **REFINEMENT_PROMPT**
Takes in consideration original Prompt, the evaluation summary and the evaluation issues and generated a new enhanced prompt
```text
    You are a senior prompt engineer specializing in insurance document extraction optimization.

    Task:
    Based on the summary and issue list from an evaluation of a failed extraction attempt, suggest **targeted improvements** to the original extraction prompt that could help the model perform better in future runs.

    Your suggestions must:
    - Focus on **clarifying ambiguous language**, **adding layout hints**, and **expanding terminology coverage**
    - Be **short, specific, and actionable**
    - Be **grounded in the actual issues observed** don’t suggest changes unless they relate to a real problem from the evaluation

    You may include suggestions like:
    - Adding synonyms or formatting variations for key fields
    - Clarifying how to handle table structures or missing headers
    - Telling the model how to treat redacted or suppressed data
    - Reinforcing the importance of null values over guessed data

    Output Format (JSON object):
    {
    "suggestions": [
        "Add: 'CSL' as a synonym for 'Combined Single Limit' under liability coverage terms.",
        "Clarify: 'Vehicle rows may span multiple lines if VIN or cost data is long always parse full line.'",
        "Emphasize: 'If Medical Payments, UM/UIM, or PIP are missing entirely, return null instead of omitting.'",
        "Add: 'Driver license fields may be labeled as 'Lic. No.', 'DL#', or may be suppressed entirely.'"
    ]
    }

    Evaluation Summary:
    ----------------------------------------------
    {{EVALUATION_SUMMARY}}
    ----------------------------------------------

    Issues:
    ----------------------------------------------
    {{ISSUES}}
    ----------------------------------------------

    Original Prompt:
    -----------------------------------------------
    {{ORIGINAL_PROMPT}}
    ----------------------------------------------
```

---

## Result Evaluation
### Defined via prompt:
- Measures **completeness**, **accuracy**, and **schema compatibility**.
- Score range: 0–100.

### Example:
```json
{
  "score": 70,
  "summary": "Symbols and vehicle cost incorrect",
  "issues": ["Mismatch: comprehensiveDeductible is null but document shows 1000"]
}
```

---

## Adptability
- Prompt handles **layout variance** and **terminology synonyms**
- Easy to introduce new fields into the schema or new prompt sections

### Summary

 - Prompts: Robust against document variation and layout
 - Evaluation: Self-contained LLM-powered QA system (score + issues)
 - Retry Mechanism: Recursive with max attempts and suggestions
 - Schema: Unified JSON with strict format, supports nulls
 - Readability: Prompts and schemas are modular, documented, and extensible

