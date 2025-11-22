import pandas as pd
import requests
import json
import time
import os
from typing import Dict, List

# --- CONFIGURATION ---
# TODO: REPLACE WITH YOUR ACTUAL API KEY
API_KEY = "AIzaSyDDV0d_bh3QNav9qD4VDFi3BsItUbmDLQA" 
MODEL_NAME = "gemini-2.0-flash"       # Use Gemini 2.0 Flash for the Judge

# --- GEMINI API CLIENT (Raw HTTP) ---
class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate_content(self, model_name, prompt, temperature=0.1, response_mime_type="text/plain"):
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print("⚠️  WARNING: API_KEY is not set. Please update it.")
            return None

        url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "response_mime_type": response_mime_type
            }
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Extract text from response
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                print(f"Error parsing response: {result}")
                return None
                
        except Exception as e:
            print(f"API Request Error: {e}")
            if response.text:
                print(f"Response details: {response.text}")
            return None

# --- INITIALIZE CLIENT ---
client = None
def init_gemini():
    global client
    client = GeminiClient(API_KEY)
    print(f"✅ Gemini Client initialized (using raw HTTP)")

# --- THE JUDGE RUBRICS ---
RUBRICS = {
    "Correctness": """
        Compare the ACTUAL ANSWER with the GOLDEN ANSWER. 
        - Score 5: The factual content matches perfectly.
        - Score 1: The answer contains dangerous or completely false information.
    """,
    "Clarity": """
        Is the answer easy for a busy restaurant owner to read?
        - Score 5: concise, bullet points where needed, no jargon.
        - Score 1: Wall of text, confusing grammar.
    """,
    "Hospitality_Tonality": """
        Metro serves the hospitality industry. The tone should be 'Professional Partner'.
        - Score 5: Polite, helpful, respectful (e.g., "Here is the information for your order").
        - Score 1: Rude, dismissive, or overly robotic (e.g., "Data not found").
    """,
    "Relevance": """
        Does the answer directly address the user's specific question?
        - Score 5: Directly answers the question without fluff.
        - Score 1: Answers a related but different question, or pivots to a generic topic.
    """,
    "Hallucination": """
        Does the ACTUAL ANSWER invent products or policies not found in the GOLDEN ANSWER?
        - Score 5: No hallucination (strictly sticks to facts).
        - Score 1: Invents discount codes, return policies, or products that don't exist.
    """
}

class MetroBot:
    """A simple bot to generate answers if they are missing (Phase 1 simulation)."""
    def __init__(self):
        self.model_name = "gemini-2.0-flash" # Use Gemini 2.0 Flash for speed

    def generate_answer(self, question):
        prompt = f"""
        You are a helpful customer service assistant for Metro (a food wholesaler).
        Answer the following question politely and concisely in German (or the language of the question).
        
        Question: {question}
        """
        return client.generate_content(self.model_name, prompt)

class MetroJudge:
    def __init__(self):
        self.model_name = MODEL_NAME

    def _construct_judge_prompt(self, question, answer, actual_answer):
        """Builds the prompt for the LLM Judge."""
        rubric_text = "\n".join([f"- {k}: {v}" for k, v in RUBRICS.items()])
        
        return f"""
        You are an expert QA Judge for Metro (a leading international food wholesaler). 
        Your job is to evaluate a Chatbot's response against a verified Golden Answer.

        ### CONTEXT
        Question: {question}
        
        ### GOLDEN ANSWER (Ground Truth)
        {answer}
        
        ### ACTUAL ANSWER (Chatbot Output)
        {actual_answer}
        
        ### SCORING RUBRIC
        {rubric_text}

        ### INSTRUCTIONS
        Evaluate the ACTUAL ANSWER on the dimensions above. 
        Provide a JSON output with a score (1-5) and a short reasoning for each.
        
        Expected JSON Format:
        {{
            "Correctness": {{ "score": int, "reasoning": "string" }},
            "Clarity": {{ "score": int, "reasoning": "string" }},
            "Hospitality_Tonality": {{ "score": int, "reasoning": "string" }},
            "Relevance": {{ "score": int, "reasoning": "string" }},
            "Hallucination": {{ "score": int, "reasoning": "string" }}
        }}
        """

    def evaluate_row(self, row):
        """Evaluates a single row of data."""
        prompt = self._construct_judge_prompt(
            row['Question'], 
            row['Answer'], 
            row['Actual_Answer']
        )

        response_text = client.generate_content(
            self.model_name, 
            prompt, 
            response_mime_type="application/json"
        )

        if response_text:
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {response_text}")
                return None
        return None

    def run_batch_evaluation(self, file_path, output_path):
        print(f"Loading data from {file_path}...")
        
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"Error: Could not find {file_path}")
            return

        # Normalize columns
        column_map = {
            'Questions': 'Question',
            'Answers': 'Answer'
        }
        df = df.rename(columns=column_map)

        # Limit to 5 rows for testing
        df = df.head(5)

        # Check for required columns
        if 'Question' not in df.columns or 'Answer' not in df.columns:
            print(f"Error: CSV/Excel must have 'Question' and 'Answer' columns. Found: {df.columns}")
            return

        # If 'Actual_Answer' is missing, generate it using the Bot
        if 'Actual_Answer' not in df.columns:
            print("Generating answers using MetroBot (Phase 1 Simulation)...")
            bot = MetroBot()
            actual_answers = []
            for index, row in df.iterrows():
                print(f"Generating answer for Q{index+1}...")
                ans = bot.generate_answer(row['Question'])
                actual_answers.append(ans)
                time.sleep(1) # Rate limit safety
            df['Actual_Answer'] = actual_answers

        results = []
        
        print(f"Starting evaluation of {len(df)} test cases...")
        for index, row in df.iterrows():
            print(f"Judging Item {index + 1}/{len(df)}...")
            eval_result = self.evaluate_row(row)
            
            if eval_result:
                # Flatten the JSON result into the row for the CSV
                flat_result = row.to_dict()
                for metric, data in eval_result.items():
                    flat_result[f"{metric}_Score"] = data['score']
                    flat_result[f"{metric}_Reason"] = data['reasoning']
                results.append(flat_result)
            else:
                print(f"Skipping row {index} due to error.")
                
            # Sleep briefly to avoid rate limits if using free tier
            time.sleep(1)

        # Calculate Averages
        if results:
            results_df = pd.DataFrame(results)
            print("\n--- EVALUATION SUMMARY ---")
            for metric in RUBRICS.keys():
                if f"{metric}_Score" in results_df.columns:
                    avg = results_df[f"{metric}_Score"].mean()
                    print(f"{metric} Average: {avg:.2f}/5.0")

            results_df.to_csv(output_path, index=False)
            print(f"Detailed report saved to {output_path}")
        else:
            print("No results generated.")

# --- MOCK DATA GENERATOR (FOR TESTING) ---
def create_dummy_csv(filename="metro_test_set.csv"):
    data = {
        "Question": [
            "What is the return policy for fresh fish?", 
            "Do you deliver on Sundays?",
            "How do I reset my password?"
        ],
        "Golden_Answer": [
            "Fresh fish must be returned within 24 hours of delivery with original packaging. Please contact customer support immediately.",
            "No, standard delivery is Monday to Saturday. Sunday delivery is available only for 'Ultra' tier partners.",
            "Go to the settings page, click 'Security', and select 'Reset Password'."
        ],
        "Actual_Answer": [
            "You can return fish whenever you want, just bring it back.", # Incorrect, Hallucination
            "We deliver Monday to Saturday. Sunday is for Ultra partners.", # Correct, Good Tone
            "IDK man, check the settings." # Correct info, Bad Tonality
        ]
    }
    pd.DataFrame(data).to_csv(filename, index=False)
    print(f"Created dummy file: {filename}")

if __name__ == "__main__":
    init_gemini()
    
    # 1. Check for input file
    input_file = "faqs_metro_german2.xlsx"
    if not os.path.exists(input_file):
        print(f"Note: {input_file} not found. Creating dummy CSV for testing.")
        create_dummy_csv()
        input_file = "metro_test_set.csv"
    
    # 2. Run the Judge
    judge = MetroJudge()
    judge.run_batch_evaluation(input_file, "metro_evaluation_report.csv")
