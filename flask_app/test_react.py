from flask import Flask, jsonify

app = Flask(__name__)

# Exemple de route pour fournir des données
@app.route('/api/data')
def get_data():
    data = {'message': 'Hello from Flask!'}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
