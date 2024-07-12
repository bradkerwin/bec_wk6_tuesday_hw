from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from connection import connection, Error

app = Flask(__name__)
ma = Marshmallow(app)

class CustomerSchema(ma.Schema):
    id = fields.Int(dump_only= True) 
    customer_name = fields.String(required= True)
    email = fields.String()
    phone = fields.String()

class WorkoutSchema(ma.Schema):
    id = fields.Int(dump_only= True)
    workout_start_time = fields.String()
    workout_end_time = fields.String()
    workout_type = fields.String()
    customer_id = fields.Int()

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many= True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many= True)

@app.route('/customers', methods=['POST'])
def add_member():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.message), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            new_customer = (customer_data["customer_name"], customer_data["email"], customer_data["phone"])
            query = "INSERT INTO customer (customer_name, email, phone) VALUES (%s, %s, %s)"
            cursor.execute(query, new_customer)
            conn.commit()

            return jsonify({'message': 'New member added successfully!'}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/customers', methods=['GET'])
def get_all_members():
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary= True)
            query = "SELECT * FROM customer;"
            cursor.execute(query)
            customers = cursor.fetchall()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return customers_schema.jsonify(customers)
            
@app.route('/customers/<int:id>', methods= ['GET'])
def get_single_member(id):
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary= True)
            query = "SELECT * FROM customer WHERE id = %s;"
            cursor.execute(query, (id,))
            customer = cursor.fetchone()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return customer_schema.jsonify(customer)
            
@app.route("/customers/<int:id>", methods= ["PUT"])
def update_member(id):
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM customer WHERE id = %s"
            cursor.execute(check_query, (id,))
            customer = cursor.fetchone()
            if not customer:
                return jsonify({"error": "Member was not found."}), 404
            
            updated_member = (customer_data['customer_name'], customer_data['email'], customer_data['phone'], id)

            query = "UPDATE customer SET customer_name = %s, email = %s, phone = %s WHERE id = %s"

            cursor.execute(query, updated_member)
            conn.commit()

            return jsonify({'message': f"Successfully updated user {id}"}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500


@app.route("/customers/<int:id>", methods=['DELETE'])
def delete_member(id):
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM customer WHERE id = %s"
            cursor.execute(check_query, (id,))
            customer = cursor.fetchone()
            if not customer:
                return jsonify({"error": "Member not found"})
            
            query = "DELETE FROM customer WHERE id = %s"
            cursor.execute(query, (id,))
            conn.commit()

            return jsonify({"message": f"Member {id} was successfully deleted."})
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/workouts', methods=['GET'])
def get_all_workouts():
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary= True)
            query = "SELECT * FROM workouts;"
            cursor.execute(query)
            workouts = cursor.fetchall()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return workouts_schema.jsonify(workouts)

@app.route("/workouts", methods=['POST'])
def schedule_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            new_workout = (workout_data["workout_start_time"], workout_data["workout_end_time"], workout_data["workout_type"], workout_data["customer_id"])
            query = "INSERT INTO workouts (workout_start_time, workout_end_time, workout_type, customer_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, new_workout)
            conn.commit()

            return jsonify({'message': 'Congratulations! You have scheduled your next workout! Good luck!'}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout(id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400    
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM workouts WHERE id = %s"
            cursor.execute(check_query, (id,))
            workout = cursor.fetchone()
            if not workout:
                return jsonify({"error": "Workout was not found."}), 404
            
            updated_workout = (workout_data['workout_start_time'], workout_data['workout_end_time'], workout_data['workout_type'], workout_data["customer_id"])

            query = "UPDATE workouts SET workout_start_time = %s, workout_end_time = %s, workout_type = %s WHERE id = %s"

            cursor.execute(query, updated_workout)
            conn.commit()

            return jsonify({'message': f"The workout at workout ID: {id} has been updated successfully."}), 200
        except Error as e:
            return jsonify({"error": e}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/workouts/<int:id>', methods=['GET'])
def view_workout(id):
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary= True)
            query = "SELECT * FROM workouts WHERE id = %s;"
            cursor.execute(query, (id,))
            workouts = cursor.fetchone()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return workout_schema.jsonify(workouts)
            
if __name__ == "__main__":
    app.run(debug= True)