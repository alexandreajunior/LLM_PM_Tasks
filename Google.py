
import re
import requests
import time

ENGINE = 'Google'

def strip_non_unicode_characters(text):
    # Define a pattern that matches all valid Unicode characters.
    pattern = re.compile(r'[^\u0000-\uFFFF]', re.UNICODE)
    # Replace characters not matching the pattern with an empty string.
    cleaned_text = pattern.sub('', text)
    cleaned_text = cleaned_text.encode('cp1252', errors='ignore').decode('cp1252')
    return cleaned_text

class Google:
  
  def __init__( self, verbose = False ):
    if verbose:  
      print( f"Benchmark settings with {ENGINE}:")
    return 

  def __str__( self ):
    return f"Running {ENGINE} Models"

  def query( url, model_name, question, api_key, options, image = False ):
   
    #url = url.format(model_name=model_name, api_key=api_key)
  
    #print(model_name, url, question, options)
    start_time = time.time()

    payload = {
        "contents": [
            {"parts": [
                {"text": question}
            ]}
        ]
    }
    
    if image: 
        payload["contents"]["parts"]["inline_data"] = { "mime_type": "image/png", "data": base64_image }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
   
    response = requests.post(url, headers=headers, json=payload).json()
    #dump_response(response, "answers_pm/" + model_name + ".json")
    
    try:
        response_message = response["candidates"][0]["content"]["parts"][0]["text"]
        #print(response_message)
    except Exception as e:
            raise Exception(str(response))

    end_time = time.time()
    total_time = time.strftime("%M:%S", time.gmtime(end_time - start_time))
    print( f"Running {ENGINE} Model {model_name} in {total_time}" )
    return strip_non_unicode_characters(response_message)
