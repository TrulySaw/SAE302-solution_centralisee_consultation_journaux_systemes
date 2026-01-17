from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from app.models import Users, Role
from app.log_check import is_log

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/")
def index():
    """
    Fonction index vérifiant que l'utilisateur est connecté, récupère les privilèges
    associés à son rôle et renvoie la page d'accueil contenue dans index.html.
    """
    if not is_log():
        return redirect("/login")
    
    privilege = session.get("privilege")
    return render_template("index.html", nom=session["nom"], privilege=privilege)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Fonction d'authentification, l'utilisateur rentre ses identifiants,
    vérification côté serveur, renvoi d'une erreur si identifiants incorrects.
    """
    if request.method == "POST":
        nom = request.form.get("nom")
        password = request.form.get("password")
        
        if not nom or not password:
            return redirect("/login?error=Please fill every text field")
        
        user = Users.query.filter_by(nom=nom).first()
        
        if user and check_password_hash(user.password, password):
            role = Role.query.get(user.role)
            session["Loggedin"] = True
            session["id"] = user.id
            session["nom"] = user.nom
            session["role"] = user.role
            session["privilege"] = role.privilege
            return redirect("/")
        else:
            return redirect("/login?error=Invalid credentials")
    
    error = request.args.get("error") 
    return render_template("/login.html", error=error)

@auth_bp.route("/logout")
def logout():
    """
    Si l'utilisateur clique sur le bouton "logout", la session se ferme
    et redirection sur la page de login.
    """
    session.clear()
    return redirect("/")