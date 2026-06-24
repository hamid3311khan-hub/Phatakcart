from flask import Flask, render_template

app = Flask(__name__)

# Home Page - ye abhi chal raha hai
@app.route('/')
def home():
    return render_template('index.html')

# Food Page - naya route
@app.route('/food')
def food():
    return render_template('food.html')

# Dress Page
@app.route('/dress')
def dress():
    return render_template('dress.html')

# Grocery Page  
@app.route('/grocery')
def grocery():
    return render_template('grocery.html')

if __name__ == '__main__':
    app.run(debug=True)
