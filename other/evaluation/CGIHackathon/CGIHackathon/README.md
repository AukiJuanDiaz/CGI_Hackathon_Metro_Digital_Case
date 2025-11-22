# Metro Evaluation Judge (Phase 2)

This project implements an LLM-based "Judge" to evaluate chatbot responses for Metro. It uses Google Vertex AI (Gemini 1.5 Pro) to score answers based on multiple dimensions.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Project ID:**
    Open `metro_judge.py` and update the `PROJECT_ID` variable with your Google Cloud Project ID.
    ```python
    PROJECT_ID = "your-google-cloud-project-id" 
    ```

3.  **Authentication:**
    Ensure you are authenticated with Google Cloud.
    - If running locally: `gcloud auth application-default login`
    - If in a hackathon environment: Ensure your environment variables or service account keys are set.

## Usage

Run the script:

```bash
python metro_judge.py
```

## How it Works

1.  **Input:** The script looks for `metro_test_set.csv` containing `Question`, `Golden_Answer`, and `Actual_Answer`. If it doesn't exist, it creates a dummy one.
2.  **Judging:** It sends each row to Gemini 1.5 Pro with a specific prompt and rubric.
3.  **Rubrics:**
    - **Correctness:** Factual accuracy vs Golden Answer.
    - **Clarity:** Conciseness and readability.
    - **Hospitality_Tonality:** Professional and polite tone suitable for Metro.
    - **Relevance:** Does it answer the specific question asked?
    - **Hallucination:** Does it invent fake info?
4.  **Output:** It saves a detailed report to `metro_evaluation_report.csv` with scores and reasoning for each metric.

## Customization

You can modify the `RUBRICS` dictionary in `metro_judge.py` to change the scoring criteria.
