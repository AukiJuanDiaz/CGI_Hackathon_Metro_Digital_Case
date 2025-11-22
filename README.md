# README Metro Case

## Run the front end

```bash
streamlit run Hello.py
```

## Front end
The front end is built using Streamlit and provides an interface for evaluating chatbot responses based on various metrics. It allows users to select different chatbot models, view evaluation reports, and analyze worst-performing questions.

The actual front end code is in page `1_📊_Evaluation.py`.

## Image of FrontEnd
![FrontEndStart](docs/Metro_Frontend_start.png)

There you can select the evaluation data of the models you want to compare.
The data is retrieved from CSV files stored in the `evaldata` folder.

After clicking the "Load Data" button, the evaluation results are displayed in radar charts, and the worst-performing questions for each model are shown in tables.

![FrontEndLoaded](docs/Metro_Frontend_selected.png)

## Backend
# In the folder BackendCode are the folling scripts that result in the final evaluation data.
# IonosAccess.py : Class which allows to Access to the Ionos Api and to send the request. It allows manage the choice of the IA model

# RAG.py : Class wich allows to create different version of our AIAgent with the combinaison of a Ionoss AI model and the provided FAQ data from Metro thanks to a RAG

# MetroJudge.py : Class wich create the model which evaluate the answers given by the AIAgent. We use to achieve it the Ionos Api

#generate_variations : Script to generate variations of the FAQ questions, thanks to a AI model, to test our different AIAgents.

## Data

The FAQ from Metro with the golden answers to the question was provided
test_fragen.csv : the variations of the questions in the FAQ provided wich are used to test our AIAgents.
critical_faqs_metro_german.csv : a list of "tricky" question wich we established to test the AIAgents.

