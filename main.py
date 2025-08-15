from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={
    r"/*": {  # Обратите внимание на "/*" вместо "/api/*"
        "origins": "*",  
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
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



# ... (предыдущий код остается без изменений) ...

# Роуты для веб канбан-доски
@app.route('/api/web_canban', methods=['GET'])
def get_web_canban():
    """Получить все задачи из веб канбан-доски"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM web_canban")
        tasks = cursor.fetchall()
        return jsonify(tasks)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/web_canban', methods=['POST'])
def add_web_canban_task():
    """Добавить новую задачу в веб канбан-доску"""
    data = request.get_json()
    if not data or 'task' not in data or 'description' not in data:
        return jsonify({'error': 'Missing required fields (task, description)'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO web_canban (task, description, status)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (
            data['task'],
            data['description'],
            data.get('status', 'set')
        ))
        connection.commit()
        
        task_id = cursor.lastrowid
        return jsonify({'message': 'Task added successfully', 'id': task_id}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/web_canban/update', methods=['PUT'])
def update_web_canban_task():
    """Обновить задачу в веб канбан-доске"""
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'Missing task id'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Проверяем существование задачи
        cursor.execute("SELECT id FROM web_canban WHERE id = %s", (data['id'],))
        if not cursor.fetchone():
            return jsonify({'error': 'Task not found'}), 404
        
        # Формируем запрос для обновления
        set_parts = []
        params = []
        
        if 'task' in data:
            set_parts.append("task = %s")
            params.append(data['task'])
        if 'description' in data:
            set_parts.append("description = %s")
            params.append(data['description'])
        if 'status' in data:
            set_parts.append("status = %s")
            params.append(data['status'])
        
        if not set_parts:
            return jsonify({'error': 'No fields to update'}), 400
        
        params.append(data['id'])
        query = f"UPDATE web_canban SET {', '.join(set_parts)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        connection.commit()
        
        return jsonify({'message': 'Task updated successfully'})
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/web_canban/delete', methods=['DELETE'])
def delete_web_canban_task():
    """Удалить задачу из веб канбан-доски"""
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'Missing task id'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM web_canban WHERE id = %s", (data['id'],))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Task not found'}), 404
            
        return jsonify({'message': 'Task deleted successfully'})
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Роуты для TSD Android канбан-доски
@app.route('/api/tsd_android_canban', methods=['GET'])
def get_tsd_android_canban():
    """Получить все задачи из TSD Android канбан-доски"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tsd_android_canban")
        tasks = cursor.fetchall()
        return jsonify(tasks)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/tsd_android_canban', methods=['POST'])
def add_tsd_android_canban_task():
    """Добавить новую задачу в TSD Android канбан-доску"""
    data = request.get_json()
    if not data or 'task' not in data or 'description' not in data:
        return jsonify({'error': 'Missing required fields (task, description)'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO tsd_android_canban (task, description, status)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (
            data['task'],
            data['description'],
            data.get('status', 'set')
        ))
        connection.commit()
        
        task_id = cursor.lastrowid
        return jsonify({'message': 'Task added successfully', 'id': task_id}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/tsd_android_canban/update', methods=['PUT'])
def update_tsd_android_canban_task():
    """Обновить задачу в TSD Android канбан-доске"""
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'Missing task id'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Проверяем существование задачи
        cursor.execute("SELECT id FROM tsd_android_canban WHERE id = %s", (data['id'],))
        if not cursor.fetchone():
            return jsonify({'error': 'Task not found'}), 404
        
        # Формируем запрос для обновления
        set_parts = []
        params = []
        
        if 'task' in data:
            set_parts.append("task = %s")
            params.append(data['task'])
        if 'description' in data:
            set_parts.append("description = %s")
            params.append(data['description'])
        if 'status' in data:
            set_parts.append("status = %s")
            params.append(data['status'])
        
        if not set_parts:
            return jsonify({'error': 'No fields to update'}), 400
        
        params.append(data['id'])
        query = f"UPDATE tsd_android_canban SET {', '.join(set_parts)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        connection.commit()
        
        return jsonify({'message': 'Task updated successfully'})
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/tsd_android_canban/delete', methods=['DELETE'])
def delete_tsd_android_canban_task():
    """Удалить задачу из TSD Android канбан-доски"""
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'Missing task id'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM tsd_android_canban WHERE id = %s", (data['id'],))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Task not found'}), 404
            
        return jsonify({'message': 'Task deleted successfully'})
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)