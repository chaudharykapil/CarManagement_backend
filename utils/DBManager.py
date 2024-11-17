import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
import uuid
from dotenv import load_dotenv
import json
load_dotenv()


firebase_config = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT"))
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
})

class DBClient:
    db = firestore.client()
    @staticmethod
    def AddNewCar(cardata):
        car_ref = DBClient.db.collection('cars').add(cardata)
        return car_ref
    @staticmethod
    def GetCars(userid):
        cars = DBClient.db.collection('cars').where('user_id', '==', userid).stream()
        return cars
    @staticmethod
    def deleteCar(car_id):
        car_ref = DBClient.db.collection('cars').document(car_id)
        car = car_ref.get()
    
        if not car.exists:
            return {"error": "Car not found"}, 404
        
        # Optionally, delete images from Firebase Storage if required
        car_ref.delete()
        return {"message": "Car deleted successfully!"}



class AuthClient:

    @staticmethod
    def createUserFromEmailPassword(email,password):
        user = auth.create_user(email=email, password=password)
        return user
    
    @staticmethod
    def getUserByEmail(email):
        user = auth.get_user_by_email(email=email)
        return user
    