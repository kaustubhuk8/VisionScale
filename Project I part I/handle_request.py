import csv
from flask import Flask, request

app = Flask(__name__)

classification_results = {}

prediction_file_path = "/home/ubuntu/Classification_1000.csv"

with open(prediction_file_path, mode='r') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    for row in csv_reader:
        image_name, result = row[0], row[1]
        classification_results[image_name] = result

@app.route('/', methods=['POST'])
def handle_request():

        if 'inputFile' not in request.files:
            return "No file part"

        file = request.files['inputFile']

        prediction_result = lookup_classification_result(file.filename)

        return f"{file.filename}:{prediction_result}"

def lookup_classification_result(filename):
    return classification_results.get(filename.rsplit('.', 1)[0], 'Unknown')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000 , threaded=True)

