import json
import os
from tools import extract_text_from_pdf, save_results
from api_client import formatted_extraction_api, evaluate_extraction, suggest_prompt_improvements

class InsuranceDocumentExtractor:
    def __init__(self):
        self.threshold = 75
        self.max_retries = 3

    def extract_with_evaluation(self, document_text, action):
        attempt = 0
        best_score = -1
        best_result = None
        best_eval = None
        suggestions = None

        while attempt < self.max_retries:
            result = formatted_extraction_api(document_text, action)
            eval_result = evaluate_extraction(document_text, result)

            print(f"Attempt {attempt + 1} | Score: {eval_result['score']}")
            print("Summary:", eval_result["summary"])

            # Track best result regardless of whether it meets the threshold
            if eval_result["score"] > best_score:
                best_score = eval_result["score"]
                best_result = result
                best_eval = eval_result

            if eval_result["score"] >= self.threshold:
                return result, eval_result, None

            suggestions = suggest_prompt_improvements(
                action=action,
                evaluation_summary=eval_result["summary"],
                issues=eval_result["issues"]
            )

            print("Suggestions to improve the prompt:")
            for s in suggestions["suggestions"]:
                print(" -", s)

            attempt += 1

        # Return the best scoring result after all retries
        return best_result, best_eval, suggestions

    def extract_data_from_document(self, document_path):
        """
            Extract structured data from an insurance document
        """
        # Extract text from the document
        document_text = extract_text_from_pdf(document_path)
        
        if not document_text:
            print(f"Failed to extract text from {document_path}")
            return self.output_schema
        
        # Get model response
        try:
            # Extract coverage section
            coverage_result, coverage_eval, coverage_suggestions = self.extract_with_evaluation(document_text, "coverage")
            drivers_result, drivers_eval, drivers_suggestions = self.extract_with_evaluation(document_text, "driver_schedule")
            vehicles_result, vehicles_eval, vehicles_suggestions = self.extract_with_evaluation(document_text, "vehicle_schedule")

            print(f"Coverage extraction result: {drivers_result}")
            extracted_data = coverage_result
            extracted_data["driverSchedule"] = drivers_result.get("drivers", [])
            extracted_data["vehicleSchedule"] = vehicles_result.get("vehicles", [])


            if not extracted_data:
                print(f"No response from API for {document_path}")
            
            # Extract JSON from the response
            try:
                print(f"Successfully extracted data from {document_path}")
                
                return extracted_data
                
            except Exception as e:
                print(f"Error parsing JSON from response: {e}")
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
    
    def process_documents(self, document_paths):
        results = {}
        
        for path in document_paths:
            print(f"Processing document: {path}")
            initial_extraction = self.extract_data_from_document(path)
            results[path] = initial_extraction
            
        return results


def main():
    input_dir = "./data"
    output_dir = "./results"
    # Initialize extractor
    extractor = InsuranceDocumentExtractor()
    
    # Process all PDFs in the directory
    if not os.path.exists(input_dir):
        print(f"Directory not found: {input_dir}")
        return
            
    # Get list of PDF files
    pdf_files = [
        os.path.join(input_dir, f) 
        for f in os.listdir(input_dir) 
        if f.lower().endswith('.pdf')
    ]
        
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
        
    # Process documents
    results = extractor.process_documents(pdf_files)
        
    # Save results
    save_results(results, output_dir)
    print(f"Extraction complete. Results saved to {output_dir}")

if __name__ == "__main__":
    main()