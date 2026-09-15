import os
import re
import time
import json
import base64
import pandas as pd
from pathlib import Path
from Ollama import Ollama as ol
from ChatGPT import ChatGPT as gpt
from HF import HF as hf
from Anthropic import Anthropic as anth
from Google import Google as google
from Mistral import Mistral as mistral
from DeepInfra import DeepInfra as di
from openpyxl import load_workbook
import warnings
warnings.simplefilter(action = "ignore") 
pd.set_option('display.max_colwidth', None)
pd.options.display.float_format = '{:.3f}'.format

SUPPORTED_ENGINES = ['Ollama', 'ChatGPT', 'HF', 'Anthropic', 'Google', 'Mistral', 'DeepInfra']
ENGINE_NOT_SUPPORTED = "Engine not supported"
MODEL_NOT_VISUAL = "Model not supported for image input"
VISUAL_QUESTION = "Can you describe the provided visualization?"

columns = ['model', 'projectID', 'questionID', 'answer']
df_answers = pd.DataFrame(columns=columns)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def dump_payload(payload, target_file):
    if "answers" in target_file:
        target_file = target_file.replace("answers", "json_payload")
        # print(target_file)
        try:
            json.dump(payload, open(target_file, "w"), indent=2)
        except:
            print("payload dumping failed")

def save_row_to_excel(file_path, row_data, sheet_name='Sheet1'):
    
    if isinstance(row_data, dict):
        new_df = pd.DataFrame([row_data])
    elif isinstance(row_data, list):
        new_df = pd.DataFrame([row_data], columns=['model', 'projectID', 'questionID', 'answer'])  # Customize columns
    else:
        raise ValueError("row_data must be a dict or list")

    if not os.path.exists(file_path):
        # File doesn't exist: create new Excel file
        new_df.to_excel(file_path, index=False, sheet_name=sheet_name)
    else:
        # File exists: load and append
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            # Load existing sheet into DataFrame to get current size
            existing_df = pd.read_excel(file_path, sheet_name=sheet_name)
            startrow = len(existing_df) + 1

            new_df.to_excel(writer, index=False, header=False, startrow=startrow, sheet_name=sheet_name)

def dump_response(response, target_file): 
    target_file = re.split(r"[\\/]", target_file)[-1] 
    fields = target_file.split("_")
    print(fields)  
    model=fields[0]
    question=fields[-1]
    question = question.rsplit('.', 1)[0]
    project = '_'.join(fields[1:-1])
    row = {'model': model, 'projectID': project, 'questionID': question, 'answer' : response}
    #save_row_to_excel('data.xlsx', row)
    df_answers.loc[len(df_answers)] = row
    F = open(target_file, "w")
    F.write(response)
    F.close()
        
    #if "answers" in target_file:
    #    target_file = target_file.replace("answers", "json_resp")
        #print(target_file)
        
    #    try:
    #        json.dump(response, open(target_file, "w"), indent=2)
    #    except:
    #        print("Response dumping failed")

class Benchmark:
  
  def __init__( self, settings_file = "settings.xlsx", verbose = False ):
    #benchmark_settings = pd.read_excel( settings_file )
    self.settings = pd.read_excel( settings_file )
    self.settings = self.settings.query("ENABLED == 'T' | ENABLED == 't'")
    if verbose:  
      print( "Benchmark settings with the following columns: ", list(self.settings.columns) )
      #print( "Benchmark settings: ", self.settings )
    return 
      
  def __str__( self ):
    return self.settings.to_csv( index = False )

  def output_to_latex( self, filename, caption="Legend", label="tab:results", verbose = False ):
    latex_table = self.output.to_latex(caption=caption, label=label, position='H', escape=True, index=False, header=True)
    # Make the first row bold
    for column in list(self.output.columns):
        latex_table = latex_table.replace(column, f"\\textbf{{{column}}}")
    # Save to a .tex file
    with open( filename, "w") as f:
        f.write( latex_table )
    return

  def prepareQuestions( self, questions_file, output_folder = "./more_questions", verbose = False ):
    document_settings = pd.read_excel( questions_file )
    for pq in document_settings.iterrows():
        result = ""
        project = open( pq[1]['FILE'], "r", encoding="utf-8").read()
        #result +=  pq[1]['PREAMBLE'] + "\n\n" + store.query( prompt = project )['documents'][0][0] + "\n\n" + pq[1]['QUESTION'] + "\n\n"
        result +=  pq[1]['PREAMBLE'] + "\n\n" + project + "\n\n" + pq[1]['CONTEXT'] + "\n\n" + pq[1]['QUESTION'] + "\n\n"
        F = open( output_folder +  "/Q" + str(pq[1]['ID']) + "_" + pq[1]['FILE'].split('/')[-1] , "w" )
        F.write( result )
        F.close()
    return
  
  def runBenchmarks( self, questioning=True, judging=False, verbose = False ):
    start_time = time.time()
    self.output = []
    for benchmark_setting in self.settings.iterrows():
        if (questioning): self.runSingleQuestioning( benchmark_setting, verbose = verbose)
        if (judging): self.runSingleJudging( benchmark_setting, verbose = verbose)
    self.output = pd.DataFrame( self.output )
    end_time = time.time()
    total_time = end_time - start_time
    if ( verbose ): print("Total time:", total_time / 60, "minutes")
    df_answers.to_excel('output.xlsx', index=False)
    df_answers.drop (df_answers.index,inplace=True)
    return
  
  def runSingleQuestioning( self, benchmark_setting, verbose = False ):

    #Set the environment variable for the remote Ollama server
    os.environ["OLLAMA_API_BASE_URL"] = benchmark_setting[1]['URL']
    ENGINE = benchmark_setting[1]['ENGINE']
    URL = benchmark_setting[1]['URL']
    MODELS = benchmark_setting[1]['MODELS'].split(",")
    VISUAL_MODELS = benchmark_setting[1]['VISUAL_MODELS'].split(",")
    QUESTIONS_PATH = benchmark_setting[1]['QUESTIONS_PATH']
    ANSWERS_PATH = benchmark_setting[1]['ANSWERS_PATH']
    #JUDGINGS_PATH = benchmark_setting[1]['EVALUATIONS_PATH']
    Path(ANSWERS_PATH + "/" + ENGINE ).mkdir(parents=True, exist_ok=True)
    OPTIONS = benchmark_setting[1]['OPTIONS']
    API_KEY = benchmark_setting[1]['API_KEY']

    if  ( ENGINE in SUPPORTED_ENGINES ):
        for MODEL_NAME in MODELS:
            questions = [x for x in os.listdir( QUESTIONS_PATH ) if x.endswith(".txt") or x.endswith(".png")]
            for q in questions:
                question_path = os.path.join( QUESTIONS_PATH , q)
                answer_path = os.path.join(ANSWERS_PATH + "/" + ENGINE, MODEL_NAME.replace("/", "").replace(":", "") + "_" + q).replace(".png", ".txt")
                if question_path.endswith(".txt"):
                    question = open(question_path, "r", encoding="utf-8").read()
                    if ( ENGINE == "Ollama" ):
                        response_message = ol.query( MODEL_NAME, question, options=OPTIONS )
                        #response_message = runOllama( MODEL_NAME, question, options=OPTIONS )
                    elif ( ENGINE == "ChatGPT" ):
                        response_message = gpt.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( ENGINE == "HF" ):
                        response_message = hf.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( ENGINE == "Anthropic" ):
                        response_message = anth.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( ENGINE == "Google" ):
                        response_message = google.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( ENGINE == "Mistral" ):
                        response_message = mistral.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( ENGINE == "DeepInfra" ):
                        response_message = di.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    else:
                        response_message = ENGINE_NOT_SUPPORTED
                else:
                    if ( MODEL_NAME not in VISUAL_MODELS ):
                        response_message = MODEL_NOT_VISUAL
                    else:
                        base64_image = encode_image(question_path)
                        if ( ENGINE == "Ollama" ):
                            question = [{"role": "user", 'images': [ base64_image ], "content":  VISUAL_QUESTION }]
                            response_message = ol.query( MODEL_NAME, question, options=OPTIONS, image=True )
                            #response_message = runOllama( MODEL_NAME, question, options=OPTIONS, image=True )
                        elif ( ENGINE == "ChatGPT" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": VISUAL_QUESTION}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = gpt.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( ENGINE == "HF" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": VISUAL_QUESTION}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = hf.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( ENGINE == "Anthropic" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": VISUAL_QUESTION}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = anth.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( ENGINE == "Google" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": VISUAL_QUESTION}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = google.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( ENGINE == "Mistral" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": VISUAL_QUESTION}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = mistral.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( ENGINE == "DeepInfra" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": VISUAL_QUESTION}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = di.query( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        else:
                            response_message = ENGINE_NOT_SUPPORTED
                
                dump_response(response_message, answer_path)
                output = { 'Engine': ENGINE, 'Model Name': MODEL_NAME, 'Answer Path': answer_path }
                self.output.append( output )
                if ( verbose ): print("Written in:", answer_path)
    return
  
  def runSingleJudging( self, benchmark_setting, verbose = False ):

    #Set the environment variable for the remote Ollama server
    os.environ["OLLAMA_API_BASE_URL"] = benchmark_setting[1]['URL']
    ENGINE = benchmark_setting[1]['ENGINE']
    URL = benchmark_setting[1]['URL']
    MODELS = benchmark_setting[1]['MODELS'].split(",")
    VISUAL_MODELS = benchmark_setting[1]['VISUAL_MODELS'].split(",")
    QUESTIONS_PATH = benchmark_setting[1]['QUESTIONS_PATH']
    ANSWERS_PATH = benchmark_setting[1]['ANSWERS_PATH']
    JUDGING = benchmark_setting[1]['JUDGING']
    JUDGING_URL = benchmark_setting[1]['JUDGING_URL']
    JUDGING_MODEL = benchmark_setting[1]['JUDGING_MODELS'] #.split(",")
    JUDGING_PATH = benchmark_setting[1]['JUDGING_PATH']
    JUDGING_OPTIONS = benchmark_setting[1]['JUDGING_OPTIONS']
    JUDGING_API_KEY = benchmark_setting[1]['JUDGING_API_KEY']
    Path(ANSWERS_PATH + "/" + ENGINE ).mkdir(parents=True, exist_ok=True)
    Path(JUDGING_PATH + "/" + ENGINE + "/" + JUDGING ).mkdir(parents=True, exist_ok=True)
    OPTIONS = benchmark_setting[1]['OPTIONS']
    API_KEY = benchmark_setting[1]['API_KEY']

    if  ( ENGINE in SUPPORTED_ENGINES ):
        for MODEL_NAME in MODELS:
            questions = [x for x in os.listdir( QUESTIONS_PATH ) if x.endswith(".txt") or x.endswith(".png")]
            for q in questions:
                question_path = os.path.join( QUESTIONS_PATH , q)
                answer_path = os.path.join(ANSWERS_PATH + "/" + ENGINE, MODEL_NAME.replace("/", "").replace(":", "") + "_" + q).replace(".png", ".txt")
                judging_path = os.path.join(JUDGING_PATH + "/" + ENGINE + "/" + JUDGING, JUDGING_MODEL + "_" +MODEL_NAME.replace("/", "").replace(":", "") + "_" + q).replace(".png", ".txt")

                if question_path.endswith(".txt"):
                    question = open(question_path, "r", encoding="utf-8").read()

                    inquiry = ["Given the following question:\n\n"]
                    inquiry.append(question)
                    inquiry.append("\n\nHow would you grade the following answer with a descrite intiger scale from 0 (minimum) to 3 (maximum)? Please put the grade at the beginning of the response. ")
                    #if CommonShared.TRIAL_CHANGE_EVALUATION_LRM:
                    inquiry.append("Please ignore the initial part of the answer, as it contains the 'flow of thought' and it can be verbose and repetitive. Only the final part/conclusions should be considered for the grade!")
                    inquiry.append("\n\n")
                    #answer = open(answer_path, "r", encoding="utf-8").read()
                    answer = open(answer_path, "r", encoding="latin-1").read()
                    inquiry.append(answer)
                    inquiry = ",".join(inquiry)
                    
                    #print(inquiry)
                    
                    if ( JUDGING == "Ollama" ):
                        response_message = ol.query( JUDGING_MODEL, inquiry, options=OPTIONS )
                        #response_message = runOllama( MODEL_NAME, question, options=OPTIONS )
                    elif ( JUDGING == "ChatGPT" ):
                        response_message = gpt.query( JUDGING_URL, JUDGING_MODEL, inquiry, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( JUDGING == "HF" ):
                        response_message = hf.query( JUDGING_URL, JUDGING_MODEL, inquiry, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( JUDGING == "Anthropic" ):
                        response_message = anth.query( JUDGING_URL, JUDGING_MODEL, inquiry, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( JUDGING == "Google" ):
                        response_message = google.query( JUDGING_URL, JUDGING_MODEL, inquiry, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( JUDGING == "Mistral" ):
                        response_message = mistral.query( JUDGING_URL, JUDGING_MODEL, inquiry, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    elif ( JUDGING == "DeepInfra" ):
                        response_message = di.query( JUDGING_URL, JUDGING_MODEL, inquiry, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS )
                        #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS )
                    else:
                        response_message = ENGINE_NOT_SUPPORTED
                else:
                    if ( MODEL_NAME not in VISUAL_MODELS ):
                        response_message = MODEL_NOT_VISUAL
                    else:
                        base64_image = encode_image(question_path)
                        answer = open(answer_path, "r", encoding="utf-8").read()
                        inquiry = ["Given the attached image, how would you grade the following answer with a descrite intiger scale from 0 (minimum) to 3 (maximum)?. Please put the grade at the beginning of the response.\n\n"]
                        inquiry.append(answer)
                        inquiry = "".join(inquiry)
                        #print(inquiry)

                        if ( JUDGING == "Ollama" ):
                            question = [{"role": "user", 'images': [ base64_image ], "content":  inquiry }]
                            response_message = ol.query( JUDGING_MODEL, question, options=JUDGING_OPTIONS, image=True )
                            #response_message = runOllama( MODEL_NAME, question, options=OPTIONS, image=True )
                        elif ( JUDGING == "ChatGPT" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": inquiry}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = gpt.query( JUDGING_URL, JUDGING_MODEL, question, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( JUDGING == "HF" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": inquiry}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = hf.query( JUDGING_URL, JUDGING_MODEL, question, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( JUDGING == "Anthropic" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": inquiry}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = anth.query( JUDGING_URL, JUDGING_MODEL, question, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( JUDGING == "Google" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": inquiry}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = google.query( JUDGING_URL, JUDGING_MODEL, question, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( JUDGING == "Mistral" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": inquiry}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = mistral.query( JUDGING_URL, JUDGING_MODEL, question, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        elif ( JUDGING == "DeepInfra" ):
                            question = [{"role": "user", "content": [{"type": "text", "text": inquiry}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image} "}}]}]
                            response_message = di.query( JUDGING_URL, JUDGING_MODEL, question, api_key=JUDGING_API_KEY, options=JUDGING_OPTIONS, image=True )
                            #response_message = runChatGPT( URL, MODEL_NAME, question, api_key=API_KEY, options=OPTIONS, image=True )
                        else:
                            response_message = ENGINE_NOT_SUPPORTED
                
                dump_response(response_message, judging_path)
                #print(response_message)
                digits = response_message.replace("*","").replace("(","").replace(")","").replace(":","")
                grade = re.findall(r"-?\d+\.?\d*", digits)
                if not grade:
                    grade.append(0)
                output = { 'Engine': ENGINE, 'Model Name': MODEL_NAME, 'Judging Name': JUDGING, 'Judging Model': JUDGING_MODEL, 'Judging Path': judging_path, 'Judging Grade': float(grade[0])}
                self.output.append( output )
                if ( verbose ): print("Written in:", judging_path)
    return
