from requests_aws4auth import AWS4Auth
import boto3
import requests
import secrets
import string
import yaml

USER_ENDPOINT = '_opendistro/_security/api/internalusers'
ROLE_ENDPOINT = '_opendistro/_security/api/roles'
ROLE_MAPPING_ENDPOINT = '_opendistro/_security/api/rolesmapping'

# Generates a 16 character password with 1 uppercase, 1 lowercase, 1 digit, and 1 symbol
# Credit: https://docs.python.org/3/library/secrets.html#recipes-and-best-practices
def generate_password():
  punctuation = ' '.join(string.punctuation)
  alphabet = string.ascii_letters + string.digits + string.punctuation
  while True:
      password = ''.join(secrets.choice(alphabet) for i in range(16))
      if (any(c.islower() for c in password)
              and any(c.isupper() for c in password)
              and any(c.isdigit() for c in password)
              and any(c in punctuation for c in password)):
          return password

# TODO: try/except
stream = open('./config.yaml', 'r')
config = yaml.safe_load(stream)

URL_BASE = config['url_base']
REGION = config['region']


service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, 'es', session_token=credentials.token)

# TODO: try/except
stream = open('./users.yaml', 'r')
users = yaml.safe_load(stream)

# Iterate over users in YAML file
## If the user exists, continue
## If the user does not exist, create the user and a role for them
## Created users have access to indices matching $username-*
## Newly created users are added to the created_users.yaml file
for user in users:

  url = f"{URL_BASE}/{USER_ENDPOINT}/{user['name']}"
  r = requests.get(url, auth=awsauth)

  # Create the user if they do not exist
  if r.status_code == 404:
    password = generate_password()
    user_payload = {
      'password': password
    }

    # TODO: try/catch failure and return code
    r = requests.put(url, auth=awsauth, json=user_payload)

    # Write out the user at creation time, in case the script crashes
    with open('./created_users.yaml', 'a') as file:
      created_user = [{
        'name': user['name'],
        'password': password
      }]
      yaml.dump(created_user, file)

  # Create a role that grants access to the user's indices
  # TODO: catch error/exception
  url = f"{URL_BASE}/{ROLE_ENDPOINT}/{user['name']}-role"
  role_payload = {
    'cluster_permissions': ['indices:data/write/bulk'],
    'index_permissions': [{
      'index_patterns': [f"{user['name']}-*"],
      'allowed_actions': ['indices_all']
    }]
  }
  r = requests.put(url, auth=awsauth, json=role_payload)

  # Create the role mapping between the role and the user.
  # Note that this removes any existing mappings.
  url = f"{URL_BASE}/{ROLE_MAPPING_ENDPOINT}/{user['name']}-role"
  role_mapping_payload = {
    'users': [user['name']]
  }
  r = requests.put(url, auth=awsauth, json=role_mapping_payload)
