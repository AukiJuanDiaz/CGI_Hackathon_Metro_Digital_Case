from dotenv import load_dotenv
import os
import requests

class IonosAccess:
    def __init__(self, number=None):
        self.Ionos_api_token = self.registration()
        self.endpoint = "https://openai.inference.de-txl.ionos.com/v1/chat/completions"
        self.model = self.ChooseChatBot(number)

    def registration(self):
        load_dotenv()
        Ionos_api_token = os.getenv('IONOS_API_TOKEN')

        #check if the file with token exists
        print("IONOS_API_TOKEN: ", Ionos_api_token[:10], "\n")

        if Ionos_api_token is None:
            print("ERROR Token")
            print("Path .env :", load_dotenv(dotenv_path='.env'))
            exit()
        return Ionos_api_token

    def ChooseChatBot(self, number):

        endpoint = "https://openai.inference.de-txl.ionos.com/v1/models"

        header = {
            "Authorization": f"Bearer {self.Ionos_api_token}", 
            "Content-Type": "application/json"
        }

        response = requests.get(endpoint, headers=header).json()
        models = response.get('data', [])

        if not models:
            print("No model available")
            exit()

        if number is not None :
            model_name = models[number-1]['id']
        
        else :
            print("Models available :")
            for i, model in enumerate(models, start=1):
                print(f"{i}. {model['id']}")

            try:
                choix = int(input("\nEnter the number of the model to be used : "))
                if choix < 1 or choix > len(models):
                    print("Invalid number")
                    exit()
                model_name = models[choix-1]['id']
            except ValueError:
                print("Please enter a valid number")
                exit()

        print(f"\nYou choose : {model_name}\n")
            
        return model_name
    
    def generate_content(self, prompt_user, temperature=0, system_content="Sie sind ein hilfsbereiter Assistent."):

        headers = {
            "Authorization": f"Bearer {self.Ionos_api_token}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": (system_content)},
                {"role": "user", "content": prompt_user}
            ],
            "temperature": temperature 
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

            # Extraction of the answers
            try:
                return result['choices'][0]['message']['content']
            except (KeyError, IndexError) as e:
                print(f"Error parsing response: {result}")
                return None

        except Exception as e:
            print(f"API Request Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response details: {e.response.text}")
            return None