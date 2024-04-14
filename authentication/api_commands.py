from flask import request
from base import Usuario, app, db, usuario_schema
from flask_jwt_extended import create_access_token

@app.route('/api/users/signup', methods=['POST'])
def signup_user():
   if "useremail" not in request.json or "username" not in request.json or "userpassword" not in request.json:
        return "Email, username of password are invalid. Please try again.", 400

   user = Usuario(useremail=request.json["useremail"], username=request.json["username"], userpassword=request.json["userpassword"])
   db.session.add(user)
   db.session.commit()
   
   return usuario_schema.jsonify(user), 201 


@app.route('/api/users/login', methods=['POST'])
def login_user():
   if "username" not in request.json or "userpassword" not in request.json:
        return "Email, username of password are invalid. Please try again.", 400

   usuario = Usuario.query.filter(Usuario.username == request.json["username"],
                                       Usuario.userpassword == request.json["userpassword"]).first()
   if usuario is None:
      return "User does not exist. Please try again.", 404

   token_de_acceso = create_access_token(identity=usuario.id)

   return {"mensaje": "Success", "token": token_de_acceso, "id": usuario.id }

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
