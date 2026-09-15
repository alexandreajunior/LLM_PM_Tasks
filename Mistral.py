
import re
import requests
import time

ENGINE = 'Mistral'

def strip_non_unicode_characters(text):
    # Define a pattern that matches all valid Unicode characters.
    pattern = re.compile(r'[^\u0000-\uFFFF]', re.UNICODE)
    # Replace characters not matching the pattern with an empty string.
    cleaned_text = pattern.sub('', text)
    cleaned_text = cleaned_text.encode('cp1252', errors='ignore').decode('cp1252')
    return cleaned_text

class Mistral:
  
  def __init__( self, verbose = False ):
    if verbose:  
      print( f"Benchmark settings with {ENGINE}:")
    return 

  def __str__( self ):
    return f"Running {ENGINE} Models"

  def query( url, model_name, question, api_key, options, image = False ):
    #print(model_name, url, question, options)
    start_time = time.time()
    payload = {
        "model": model_name
    }

    if image: 
        payload["messages"] = question
        payload["max_tokens"] = options
    else:
        payload["messages"] = [{"role": "user", "content": question}]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
   
    response = requests.post(url, headers=headers, json=payload).json()
    #dump_response(response, "answers_pm/" + model_name + ".json")
    try:
        response_message = response["choices"][0]["message"]["content"]
    except Exception as e:
            raise Exception(str(response))
    
    end_time = time.time()
    total_time = time.strftime("%M:%S", time.gmtime(end_time - start_time))
    print( f"Running {ENGINE} Model {model_name} in {total_time}" )
    return strip_non_unicode_characters(response_message)
