import pm4py

chatgpt_key = "YOUR_CHATGPT_KEY_HERE"

def query_1( log ):
    query = """\n What are the root causes of the performance issues in the process? """
    abstract_model = pm4py.llm.abstract_dfg( log )
    print( abstract_model + query )
    #resp = pm4py.llm.openai_query( abstract_model + query, api_key=chatgpt_key, openai_model="gpt-3.5-turbo" )
    #print(resp)

def query_2( log ):
    query = """\n What are the root causes of the performance issues in the process? Please provide only process and data specific considerations, no general considerations."""
    abstract_model = pm4py.llm.abstract_variants( log, include_performance = False )
    print( abstract_model + query )
    #resp = pm4py.llm.openai_query( abstract_model + query, api_key=chatgpt_key, openai_model="gpt-3.5-turbo" )
    #print( resp )

def query_3( log ):
    net, im, fm = pm4py.discover_petri_net_inductive( log )
    query = """\n Can you provide suggestions to improve the process model based on your domain knowledge? Please provide only process and data specific considerations, no general considerations."""
    abstract_model = pm4py.llm.abstract_petri_net( net, im, fm )
    print(abstract_model + query)
    #resp = pm4py.llm.openai_query( abstract_model + query, api_key=chatgpt_key, openai_model="gpt-3.5-turbo" )
    #print(resp)

if __name__ == "__main__":
    filename = "PurchaseRequest.csv.xes"
    log = pm4py.read_xes( filename )
    #query_1( log )
    #query_2( log )
    query_3( log )
 
