from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Конфигурация базы данных
db_config = {
    'host': '147.45.138.77',
    'port': 3306,
    'database': 'TEKMAN',
    'user': 'tekman',
    'password': 'Moloko123!'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/api/logins', methods=['GET'])
def get_logins():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM lines_logins")
        logins = cursor.fetchall()
        return jsonify(logins)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/movement_types', methods=['GET'])
def get_movement_types():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM movement_type")
        types = cursor.fetchall()
        return jsonify(types)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM stocks")
        stocks = cursor.fetchall()
        return jsonify(stocks)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Новые роуты для линий и принтеров
@app.route('/api/lines', methods=['GET'])
def get_lines():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT login, name FROM lines_logins")
        lines = cursor.fetchall()
        return jsonify(lines)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/printers', methods=['GET'])
def get_printers():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT name, ip, line_name FROM printers")
        printers = cursor.fetchall()
        return jsonify(printers)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Новые роуты для работы с фактами
@app.route('/api/facts', methods=['GET'])
def get_facts():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT text FROM facts")
        facts = cursor.fetchall()
        return jsonify(facts)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/facts', methods=['POST'])
def add_fact():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text in request'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO facts (text) VALUES (%s)", (data['text'],))
        connection.commit()
        return jsonify({'message': 'Fact added successfully'}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



# Новые роуты для инфраструктурных компонентов
@app.route('/api/infrastructure/components', methods=['GET'])
def get_infrastructure_components():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM infrastructure_components")
        components = cursor.fetchall()
        return jsonify(components)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/infrastructure/components/<int:component_id>', methods=['GET'])
def get_component(component_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM infrastructure_components WHERE id = %s", (component_id,))
        component = cursor.fetchone()
        if component:
            return jsonify(component)
        else:
            return jsonify({'error': 'Component not found'}), 404
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



# Роуты для соединений между компонентами
@app.route('/api/infrastructure/connections', methods=['GET'])
def get_component_connections():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT cc.*, 
               src.name as source_name, src.type as source_type,
               tgt.name as target_name, tgt.type as target_type
        FROM component_connections cc
        JOIN infrastructure_components src ON cc.source_component_id = src.id
        JOIN infrastructure_components tgt ON cc.target_component_id = tgt.id
        """
        cursor.execute(query)
        connections = cursor.fetchall()
        return jsonify(connections)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/infrastructure/connections/by_component/<int:component_id>', methods=['GET'])
def get_connections_by_component(component_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT cc.*, 
               src.name as source_name, src.type as source_type,
               tgt.name as target_name, tgt.type as target_type
        FROM component_connections cc
        JOIN infrastructure_components src ON cc.source_component_id = src.id
        JOIN infrastructure_components tgt ON cc.target_component_id = tgt.id
        WHERE cc.source_component_id = %s OR cc.target_component_id = %s
        """
        cursor.execute(query, (component_id, component_id))
        connections = cursor.fetchall()
        return jsonify(connections)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Роуты для представлений
@app.route('/api/infrastructure/port_usage', methods=['GET'])
def get_port_usage():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM port_usage")
        port_usage = cursor.fetchall()
        return jsonify(port_usage)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/infrastructure/component_connectivity', methods=['GET'])
def get_component_connectivity():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM component_connectivity")
        connectivity = cursor.fetchall()
        return jsonify(connectivity)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)