import re
import ollama
import time

ENGINE = 'Ollama'

def strip_non_unicode_characters(text):
    # Define a pattern that matches all valid Unicode characters.
    pattern = re.compile(r'[^\u0000-\uFFFF]', re.UNICODE)
    # Replace characters not matching the pattern with an empty string.
    cleaned_text = pattern.sub('', text)
    cleaned_text = cleaned_text.encode('cp1252', errors='ignore').decode('cp1252')
    return cleaned_text

class Ollama:
  
  def __init__( self, verbose = False ):
    if verbose:  
      print( f"Benchmark settings with {ENGINE}:")
    return 

  def __str__( self ):
    return f"Running {ENGINE} Models"

  def query( model_name, question, options, image = False ):
    #print(options)
    start_time = time.time()
    options = options
    if image:
        #print(question)
        response = ollama.chat( model=model_name, messages=question )
    else:
        response = ollama.chat( model=model_name, messages=[
                    {
                        'role': 'user',
                        'content': question,
                        'options': options
                    },
                ])
        
    end_time = time.time()
    total_time = time.strftime("%M:%S", time.gmtime(end_time - start_time))
    print( f"Running {ENGINE} Model {model_name} in {total_time}" )
    return strip_non_unicode_characters(response["message"]["content"])