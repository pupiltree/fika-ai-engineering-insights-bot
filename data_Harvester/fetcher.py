import requests
from dotenv import load_dotenv
import os
import json

class data_harvester:
    
    def __init__(self, repo_name, repo,access_token=None):
        self.repo_name = repo_name
        self.repo = repo
        self.access_token = access_token
        load_dotenv()
        if not self.access_token:
            self.access_token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    
    def append_to_json(self,data, filename):
        #fika-ai-engineering-insights-bot\data\pull_request.json
        try:
            with open(f"data/{filename}", "r") as f:
                existing = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing = []
        # Create a set of existing SHA values for quick lookup
        existing_shas = {item['sha'] for item in existing if 'sha' in item}
        # Filter out new data that already exists in the file
        new_data = [
            item for item in data 
            if 'sha' in item and item['sha'] not in existing_shas
        ]
        if not new_data:
            print(f"No new data to append to {filename}")
            return
        existing.extend(new_data)
        with open(f"data/{filename}", "w") as f:
            json.dump(existing, f, indent=4)
        print(f"Appended {len(new_data)} new items to {filename}")

    
    def fetch_pull_request_data_save_it_in_json(self, pull_number,state,title,user,created,updated):
        """Fetches pull request files and appends them to a JSON file."""
        
        
        url = f"https://api.github.com/repos/{self.repo_name}/{self.repo}/pulls/{pull_number}/files"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        try: 
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            print("Data Fetched Successfully")
            simplified_data = []
            for item in data:
                simplified_data.append({
                    "sha": item["sha"],
                    "state": state,
                    "title": title,
                    "user": user,
                    "filename": item["filename"],
                    "status": item["status"],
                    "additions": item["additions"],
                    "deletions": item["deletions"],
                    "changes": item["changes"],
                    "created_at":created,
                    "updated_at":created
                })
            self.append_to_json(simplified_data, "pull_request.json")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")    
        except ValueError as e:
            print(f"Error parsing JSON: {e}")

    def fetch_number_of_pull_request(self):
        
        """Fetches the number of pull requests and their details and send them to a fetch_and_post_pull_request_files function to fetch exact values of the files."""
        
        url = f"https://api.github.com/repos/{self.repo_name}/{self.repo}/pulls"
        load_dotenv()
        bear_token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')

        headers = {
            "Authorization": f"Bearer {bear_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        try: 
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            for i in data:
                self.fetch_pull_request_data_save_it_in_json(i['number'],i['state'],i['title'],i['user']['login'],i["created_at"],i["updated_at"])
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")    
        except ValueError as e:
            print(f"Error parsing JSON: {e}") 
            
    def fetch_commit_data(self):
        """Fetches commit data from the repository."""
        
        url = f"https://api.github.com/repos/{self.repo_name}/{self.repo}/commits"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        try: 
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            simplified_data = []
            for i in data:
                simplified_data.append({
                    "sha": i["sha"],
                    "author": i["commit"]["author"]["name"],
                    "date": i["commit"]["author"]["date"],
                    "message": i["commit"]["message"]
                })
            self.append_to_json(simplified_data, "commits.json")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")    
        except ValueError as e:
            print(f"Error parsing JSON: {e}")