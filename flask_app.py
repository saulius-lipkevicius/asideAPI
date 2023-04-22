from flask import Flask, request, jsonify
from preprocessing import *

app = Flask(__name__)



@app.route('/process', methods=['POST'])
def process():
    data = request.get_json() # get the JSON payload from the request
    processed_data = process_input(data)
    # do some processing on the data
    response_data = {'result': 'success', 'processed_data': json.loads(processed_data)} # create a JSON response
    return jsonify(response_data) # return the response as JSON

if __name__ == '__main__':
    with open('json_dump/hackaton.json', 'r') as f:
        # Load the contents of the file into a dictionary
        data = json.load(f)

    prep_data = json.loads(process_input(data))
  
    for item in prep_data:

        print(item['measure'])

  
    app.run(debug=True)