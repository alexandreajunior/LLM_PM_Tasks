import pandas
import pm4py

def convert_csv( file_path ):
    event_log = pandas.read_csv( file_path, sep=',' )
    event_log = pm4py.format_dataframe( event_log, case_id='case_id', activity_key='Activity', start_timestamp_key='start_time', timestamp_key='end_time', timest_format='%Y-%m-%dT%H:%M:%S' )
    pm4py.write_xes( event_log, file_path + ".xes" )

if __name__ == "__main__":
    filename = "PurchaseRequest.csv"
    convert_csv( filename )

