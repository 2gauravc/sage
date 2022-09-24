
# Make the API call to OpenAI codex API 

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)

response = openai.Completion.create(
  model="code-davinci-002",
  prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to list the names of the departments which employed more than 10 employees in the last 3 months\nSELECT",
  temperature=0,
  max_tokens=150,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0,
  stop=["#", ";"]
)
print (response)