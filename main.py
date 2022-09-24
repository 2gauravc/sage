
# Make the API call to OpenAI codex API 

import os
import openai
import getopt, sys

def main(argv): 
    try: 
        opts, args = getopt.getopt(argv,"q:", ["query="])
    except getopt.GetoptError:
        print("Usage: python3 main.py --query=<query_path>")
        sys.exit(2)
    
    req_options = 0
    for opt, arg in opts:
        if opt == '--query':
            query_file = arg
            req_options = 1

    if (req_options == 0):
        print("Usage: python3 main.py --query=<query_path>")
        sys.exit(2)
    
    ## Get the API key  
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Read the table structure 
    with open(query_file) as f:
        query_text = f.readlines()
    print (query_text)
    #sys.exit() 

    response = openai.Completion.create(model="code-davinci-002",
    prompt=query_text,
    temperature=0,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,presence_penalty=0,
    stop=["#", ";"]
    )
    print (response)


if __name__ == "__main__":
   main(sys.argv[1:])