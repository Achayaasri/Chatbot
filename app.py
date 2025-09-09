from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',        
            user='root',             
            password='12345',        
            database='minibot_db'    
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def insert_regulation(rule_name, description):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM regulations WHERE rule_name = %s", (rule_name,))
            count = cursor.fetchone()[0]
            if count == 0:  
                cursor.execute("INSERT INTO regulations (rule_name, description) VALUES (%s, %s)", (rule_name, description))
                connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Error executing insert: {err}")
        finally:
            connection.close()

def fetch_regulation(query):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT description FROM regulations WHERE LOWER(rule_name) LIKE %s", ('%' + query.lower() + '%',))
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            return [desc[0] for desc in result if desc[0]]  # Avoid empty descriptions
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            return ["There was an error retrieving information from the database."]
    else:
        return ["Database connection failed."]



@app.route('/', methods=['GET', 'POST'])
def index():
    response = None
    if request.method == 'POST':
        query = request.form.get('query')
        regulations = fetch_regulation(query)
        if regulations:
            response = regulations
        else:
            response = ["I couldn't find any information on that topic. Please try another question."]
    return render_template('index.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)
