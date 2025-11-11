# Databricks notebook source
# MAGIC %md
# MAGIC # Leverage Genie Conversation API
# MAGIC
# MAGIC Here we will be creating a Genie Space and interact with it via Conversation API.

# COMMAND ----------

# MAGIC
# MAGIC %md
# MAGIC ### Loading the configurations
# MAGIC
# MAGIC Attach the notebook to the `Serverless` cluster and run the following cells.

# COMMAND ----------

databricks_host = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
space_id = "01f001b1fbc417899f22e8fb835e9e2b"  
genie_space_url = f"{databricks_host}/api/2.0/genie/spaces/{space_id}"
print("genie_space_url: ", genie_space_url, sep="")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query the Genie Space via Conversation API:
# MAGIC We can use API calls to call Genie space's Conversation APIs using [PublicPreview docs](https://docs.google.com/document/d/1377caJzV6T5fXSjkt0DXGNmfDizPEe-Fs-2MjhSGzms/edit?tab=t.0#heading=h.5nn4ybsm5z0g):
# MAGIC
# MAGIC 1. Start a Conversation: Use the endpoint `POST /api/2.0/genie/spaces/{space_id}/start-conversation` with the content of your initial question in the body.
# MAGIC
# MAGIC 2. Create Conversation Message: For follow-up questions, use `POST /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages`.
# MAGIC
# MAGIC 3. Get Conversation Message: Track the status and retrieve the generated SQL using `GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}`.
# MAGIC
# MAGIC 4. Fetch SQL Results: Retrieve results of an executed SQL query using `GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/query-result`.
# MAGIC

# COMMAND ----------

import requests

# COMMAND ----------

# Get a token for authentication
api_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# COMMAND ----------

def do_api_call(endpoint, payload, headers, method):
    try:
        # Send a GET/POST request to the API
        if method == "GET":
            response = requests.get(endpoint, headers=headers)
        elif method == "POST":
            response = requests.post(endpoint, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
            print("API call successful!")
            print("API Response:", response.json())  # Display the API response
        else:
            print(f"API call failed with status code {response.status_code}")
            print("Response:", response.text)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC #### 1. Start a conversation

# COMMAND ----------

user_input = "Get 10 top opportunities by amount?" # Put a prompt to the Genie Space here

payload = {'content': user_input}

headers = { 'Authorization': f'Bearer {api_token}', 'Content-Type': 'application/json' }

submit_message_res = do_api_call(f'{genie_space_url}/start-conversation', payload, headers, "POST")
display(submit_message_res)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2. Check the status of the query
# MAGIC
# MAGIC We need to wait until the query status is `COMPLETED`. After, we can retrieve the results.

# COMMAND ----------

conversation_id = submit_message_res['conversation_id']
message_id = submit_message_res['message_id']
print(f"conversation_id: {conversation_id}")
print(f"message_id: {message_id}")

for _ in range(1000):
    message_status = do_api_call(f'{genie_space_url}/conversations/{conversation_id}/messages/{message_id}', None, headers, "GET")
    print(f"message status res: {message_status}")
    
    if message_status:
        curr_status = message_status["status"]
        print(f"Status: {curr_status}")
        
        if curr_status == "COMPLETED":
            break

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3. Fetch results
# MAGIC
# MAGIC Now, when the query is completed, we can fetch the results
# MAGIC

# COMMAND ----------

message_result = do_api_call(f'{genie_space_url}/conversations/{conversation_id}/messages/{message_id}/query-result', None, headers, "GET")

# Check if message_result is empty - in this case Genie was not able to process the prompt and is asking for more details.
if not message_result:
    print("Genie Space API Response:", message_status["attachments"])
else:
    data = message_result['statement_response']['result']
    meta = message_result['statement_response']['manifest']
    
    rows = [[value['str'] for value in row['values']] for row in data['data_typed_array']]
    columns = [col['name'] for col in meta['schema']['columns']]
    
    df = spark.createDataFrame(rows, schema=columns)
    display(df)

# COMMAND ----------

