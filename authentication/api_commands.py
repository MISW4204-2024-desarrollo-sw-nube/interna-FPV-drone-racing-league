from flask import request
from base import Usuario, app, db, usuario_schema
from flask_jwt_extended import create_access_token
from sqlalchemy import or_
import datetime

def validate_password_confirmation(password1, password2):
   return password1 != password2

def validate_user_existance(email, username):
    return Usuario.query.filter(or_(Usuario.username == username, Usuario.useremail == email)).first()

def find_account(username, password):
   return Usuario.query.filter(Usuario.username == username,
                                       Usuario.userpassword == password).first()
      
@app.route('/api/users/signup', methods=['POST'])
def signup_user():
   if "useremail" not in request.json or "username" not in request.json or "password1" not in request.json or "password2" not in request.json:
        return "useremail, username, password1 or password2 are invalid. Please try again.", 400

   if validate_password_confirmation(request.json["password1"], request.json["password2"]):
      return "password1 and password2 do not match. Please try again."
  
   if validate_user_existance(request.json["useremail"], request.json["username"]) is not None:
      return "username or email already exists. Please provide another email or username.", 400
   
   user = Usuario(useremail=request.json["useremail"], username=request.json["username"], userpassword=request.json["password1"])
   db.session.add(user)
   db.session.commit()
   
   return usuario_schema.jsonify(user), 201 


@app.route('/api/users/login', methods=['POST'])
def login_user():
   if "username" not in request.json or "password" not in request.json:
        return "username or password are invalid. Please try again.", 400

   user = find_account(request.json["username"],request.json["password"])

   if user is None:
      return "User does not exist. Please try again.", 404

   token_de_acceso = create_access_token(identity=user.id, expires_delta=datetime.timedelta(minutes=5))

   return {"mensaje": "Success", "token": token_de_acceso, "id": user.id }

if __name__ == "__main__":
    app.run(host="0.0.0.0")
