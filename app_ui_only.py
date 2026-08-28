from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("Starting lightweight UI-only server...")
    app.run(debug=True, port=5000)
