
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid,os
from dotenv import load_dotenv
from utils.DBManager import DBClient,AuthClient
load_dotenv()

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static/uploads/cars'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/")
def Hello():
    return "hii"


# Route to sign up user
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    
    email = data['email']
    password = data['password']
    
    try:
        user = AuthClient.createUserFromEmailPassword(email=email, password=password)
        return jsonify({"message": "User created successfully!", "uid": user.uid}), 201
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400
    

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    try:
        user = AuthClient.LoginWithEmailPassword(email,password)
        print(user)
        if "email" not in user:
            return jsonify({"error": "Email or Password is Wrong"}), 404

            # Authentication logic can be added here for token validation
        print(user)
        return jsonify({"message": "User logged in successfully!", "uid": user["localId"]}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "User not found"}), 404
    

# Route to add a car
@app.route('/cars', methods=['POST'])
def add_car():
    user_id = request.form['user_id']  # Assuming the user ID comes in the request
    name = request.form['name']
    price = request.form['price']
    transmission = request.form['transmission']
    mileage = request.form['mileage']
    description = request.form['description']
    engine_size = request.form['engine_size']
    fuelType = request.form['fuelType']
    # Handle image uploads
    image_urls = []
    if 'images' in request.files:
        images = request.files.getlist('images')
        if(len(image) > 10):
            return jsonify({"error": "Images Exceed over 10"}), 404
        for image in images:
            if allowed_file(image.filename):
                file_extension = image.filename.rsplit('.', 1)[1].lower()  # Get the file extension
                random_filename = str(uuid.uuid4()) + '.' + file_extension 
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
                image.save(file_path)
                # Create URL for the image that can be accessed publicly
                image_url = f'/{UPLOAD_FOLDER}/{random_filename}'
                image_urls.append(image_url)
    
    # Store car details in Firestore
    car_data = {
        'user_id':user_id,
        'name': name,
        'mileage': mileage,
        'engine_size': engine_size,
        'fuelType': fuelType,
        'description': description,
        'price': price,
        'images': image_urls,
        'transmission': transmission,
    }
    try:
        car = DBClient.AddNewCar(cardata=car_data)
        return jsonify({"message": "Car added successfully!", "car_id": car[1].id}), 201
    except Exception as e:
        return jsonify({"error": "Car not Added"}), 404

@app.route('/cars', methods=['GET'])
def get_cars():
    user_id = request.args.get('user_id')  # Get user ID from query params
    cars = DBClient.GetCars(userid=user_id)
    
    car_list = []
    for car in cars:
        car_data = car.to_dict()
        car_data['car_id'] = car.id
        car_list.append(car_data)
    
    return jsonify(car_list)


@app.route('/cars/<car_id>', methods=['DELETE'])
def delete_car(car_id):
    print(car_id)
    res = DBClient.deleteCar(car_id=car_id)
    print(res)
    return jsonify(res)


@app.route('/cars/search', methods=['GET'])
def search_cars():
    # Extract search keyword and user ID (optional) from query parameters
    keyword = request.args.get('keyword', '').lower()
    user_id = request.args.get('user_id')  # Optional: For searching only within a user's cars
    print(request.args.to_dict())
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400
    
    try:
        # Fetch all cars (or only the user's cars if `user_id` is provided)
        cars = DBClient.GetCars(userid=user_id)
        
        # Filter cars based on keyword match in title, description, or tags
        matching_cars = []
        for car in cars:
            car_data = car.to_dict()
            car_data['car_id'] = car.id
            
            # Check if the keyword exists in any of the searchable fields
            if (keyword in car_data.get('name', '').lower() or
                keyword in car_data.get('description', '').lower()):
                matching_cars.append(car_data)
        
        return jsonify(matching_cars), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while searching", "details": str(e)}), 500




@app.route('/cars/edit', methods=['POST'])
def edit_car():
    car_id = request.form['car_id']
    data = request.form
    res = DBClient.editCar(car_id=car_id,data=data)
    print(res)
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True)
