from projekat import app

#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
