from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash
from app import db
from app.models import Users, Role
from app.log_check import is_log, priv

user_bp = Blueprint('users', __name__)

@user_bp.route("/users", methods=["GET", "POST"])
def users():
    """
    Fonction de vérification de l'existence de la session, si l'utilisateur n'est pas un admin
    l'accès à la page des utilisateurs est refusé.
    """
    if not is_log():
        return redirect("/login")    
    if not priv(4):
        error = "Error 403 : Access denied"
        return error
    
    users = Users.query.all()
    error = request.args.get("error")
    roles = Role.query.all()
    
    return render_template("users.html", users=users, error=error, nom=session["nom"], privilege=session["privilege"], roles=roles)

@user_bp.route("/edit_user", methods=["GET", "POST"])
def edit_user():
    """
    Fonction de modification des informations d'un utilisateur, vérifiant avant tout que la session 
    existe et vérifie les privilège de l'utilisateur (admin). 
    """
    if not is_log():
        return redirect("/login")    
    if not priv(4):
        return redirect("/")   
    if request.form.get("id"):
        id = request.form.get("id")
    else:
        return redirect("/users")
    
    user = Users.query.get(id)
    roles = Role.query.all()
    change = False
    
    if not user:
        return redirect("/users")    
    if request.form.get("nom"):
        nom = request.form.get("nom")
        # vérification que le nouveau nom n'est pas déjà attribué
        if nom != user.nom:
            if Users.query.filter_by(nom=nom).first():
                error = "This username has already been attributed"
                return render_template("edit_user.html", error=error, user=user, nom=session["nom"], privilege=session["privilege"], roles=roles)
            user.nom = nom
            change = True
    # hashage du nouveau mot de passe renseigné par l'administrateur pour le nouvel utilisateur
    if request.form.get("password"):
        password = request.form.get("password")
        user.password = generate_password_hash(password)
        change = True  
    if request.form.get("role"):
        role = request.form.get("role")
        user.role = role
        change = True   
    if change:
        db.session.commit()
        return redirect("/users")
    else:
        return render_template("edit_user.html", user=user, nom=session["nom"], privilege=session["privilege"], roles=roles)

@user_bp.route("/del_user", methods=["POST"])
def suppr_user():
    """
    Fonction de suppression d'un utilisateur, besoin des droits admins également.
    """
    if not is_log():
        return redirect("/login")    
    if not priv(4):
        return redirect("/")   
    if request.form.get("id"):
        id = request.form.get("id")
    else:
        return redirect("/users")   
    if id == "1":
        return redirect("/users")
    
    user = Users.query.get(id)
    
    if user:
        db.session.delete(user)
        db.session.commit()
    
    return redirect("/users")

@user_bp.route("/add_user", methods=["POST"])
def ajout_user():
    """
    Fonction d'ajout d'un utilisateur, l'administrateur devra renseigner son nom,
    lui créer un mot de passe et sélectionner son rôle parmi les 3 disponibles.
    """
    if not is_log():
        return redirect("/login")   
    if not priv(4):
        return redirect("/")
    
    nom = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")
    
    if not nom or not password:
        return redirect("/users?error=Please fill every text field")
    # vérifie que le nom renseigné n'est pas déjà attribué    
    if Users.query.filter_by(nom=nom).first():
        return redirect("/users?error=This user already exists")   
    for i in nom and password:
        if " " in nom or " " in password:
            return redirect("/users?error=Spaces are prohibited")
    # hashage du mot de passe renseigné par l'administrateur pour le nouvel utilisateur
    try:
        hash_passwd = generate_password_hash(password)
        user = Users(nom=nom, password=hash_passwd, role=role)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return redirect(f"/users?error=Internal error : {e}")
    
    return redirect("/users")