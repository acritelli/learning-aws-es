from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import yaml
import logging
import faker
import datetime
import random

logger = logging.getLogger('create_roles')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

logger.addHandler(console_handler)

try:
  stream = open('./config.yaml', 'r')
  config = yaml.safe_load(stream)
except Exception:
  logger.critical('Unable to open and load ./config.yaml. Exiting.')
  quit()

HOST = config['host']
# REGION = config['region']

# service = 'es'
# credentials = boto3.Session().get_credentials()
# awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, 'es', session_token=credentials.token)

try:
  stream = open('./created_users.yaml', 'r')
  users = yaml.safe_load(stream)
except Exception:
  logger.critical('Unable to open and load ./users.yaml. Exiting.')
  quit()

fake = faker.Faker()

for user in users:
  index = f"{user['name']}-{datetime.date.today().strftime('%Y-%m-%d')}"

  logger.debug(f"Creating documents for user {user['name']} and index {index}")

  try:
    es = Elasticsearch(
        hosts = [{'host': HOST, 'port': 443}],
        http_auth = f"{user['name']}:{user['password']}",
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
  except Exception:
    logger.error(f"Unable to create Elasticsearch object for user {user['name']}. Skipping.")
    continue

  for i in range(0, random.randrange(1, 25)):
    document = {
      'order_id': fake.uuid4(),
      'customer_id': fake.uuid4(),
      'invoice_email': fake.ascii_email(),
      'barcode': fake.ean(),
    }

    try:
      es.index(index=index, doc_type="_doc", id=document['order_id'], body=document)
      logger.debug(f"Indexed document with ID {document['order_id']} to index {index}")
    except Exception:
      logger.error(f"Failed to index document with ID {document['order_id']} to index {index}")
      continue

