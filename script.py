import requests
import json
import time
import pandas as pd

GITHUB_TOKEN = 'api_token_key' 
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# function for cleaning the company name

def clean_company(company):
  if company:
    company=company.strip().lstrip('@').upper()
  return company

#Function for changing the True to true and False to false

def format_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'  # Convert booleans to lowercase strings
    return value if value is not None else ''

# Function call to get the details for a particular user

def get_user_detail(username):
  url = f'https://api.github.com/users/{username}'
  try:
    response = requests.get(url = url , headers = headers)
    response.raise_for_status()
    user_data=response.json()
    return {
            'login': user_data.get('login'),
            'name': format_value(user_data.get('name')),
            'company': format_value(clean_company((user_data.get('company')))),
            'location': format_value(user_data.get('location')),
            'email': format_value(user_data.get('email')),
            'hireable': format_value(user_data.get('hireable')),
            'bio': format_value(user_data.get('bio')),
            'public_repos': format_value(user_data.get('public_repos')),
            'followers': format_value(user_data.get('followers')),
            'following': format_value(user_data.get('following')),
            'created_at': format_value(user_data.get('created_at'))
        }
  except requests.exceptions.RequestException as e:
        print(f"Error fetching details for {username}: {e}")
        return None

  # Function call for getting the users in Zurich by the given conditions

def fetch_users_in_zurich():
    users = []
    page = 1
    while True:
        try:
            url = f'https://api.github.com/search/users?q=location:Zurich followers:>50&page={page}&per_page=100'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if 'items' not in data or not data['items']:
                break

            for user in data['items']:
                details = get_user_detail(user['login'])
                if details:
                    users.append(details)

            page += 1
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching users on page {page}: {e}")
            break

    return users

# Function for save and calling the above functions.
def save_to_csv(users_data, filename='users.csv'):
    df = pd.DataFrame(users_data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Run and Save Data
users_data = fetch_users_in_zurich()
save_to_csv(users_data)

# Now another Api call to Github for getting the repositories for a particular user.

# Function to get users in the form of list by using pandas library
def load_user_logins(filename='users.csv'):
  try:
    users_df = pd.read_csv(filename)
    return users_df['login'].tolist()
  except Exception as e:
    print(f'error reading {filename}: {e}')
    return []
# Function call to get the repository for a particular user

def get_user_repos(login , max_repos=500):
  repos =  []
  page = 1
  per_page = 100
  while (len(repos)< max_repos):
    try:
      url = f'https://api.github.com/users/{login}/repos?page={page}&per_page={per_page}&sort=pushed'
      response = requests.get(url , headers=headers)
      response.raise_for_status()
      data = response.json()

      if not data:
        break
      for repo in data:
        if len(repos) >= max_repos:
          break
        repos.append({
                    'login': login,
                    'full_name': format_value(repo.get('full_name')),
                    'created_at':format_value(repo.get('created_at')),
                    'stargazers_count': format_value(repo.get('stargazers_count')),
                    'watchers_count': format_value(repo.get('watchers_count')),
                    'language': format_value(repo.get('language')),
                    'has_projects': format_value(repo.get('has_projects')),
                    'has_wiki': format_value(repo.get('has_wiki')),
                   'license_name': format_value(repo.get('license')['key']) if repo.get('license') else ''


                })
      page+=1
      time.sleep(1)
    except requests.exceptions.RequestException as e:
      print(f'Error fetching repos for {login} on {page} : {e}')
      break
  return repos

# function for call all the users.

def fetch_repos_for_all_users():
  users=load_user_logins()
  all_repos = []

  for login in users:
    user_repos = get_user_repos(login)
    all_repos.extend(user_repos)

  return all_repos

# function for saving and calling the above functions.

def save_repos_file(repos_data,filename = 'repository.csv'):
  df = pd.DataFrame(repos_data)
  df.to_csv(filename, index = False)
  print(f"repository data saved to {filename}")

repos_data = fetch_repos_for_all_users()
save_repos_file(repos_data)

