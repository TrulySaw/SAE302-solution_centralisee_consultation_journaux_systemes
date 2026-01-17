from flask import Blueprint, render_template, request, redirect, session
from ipaddress import IPv4Address
from app import db
from app.models import Machines
from app.log_check import is_log, priv

serveurs_bp = Blueprint('serveurs', __name__)

@serveurs_bp.route("/serveurs", methods=["GET", "POST"])
def serveurs():
    """
    Fonction qui vérifie l'existence de la session, si l'utilisateur n'est pas au
    moins un gestionnaire, l'accès à la page est refusée.
    """
    if not is_log():
        return redirect("/login")   
    if not priv(2):
        error = "Error 403 : Access denied"
        return error
    
    machines = Machines.query.all()
    error = request.args.get("error")
    
    return render_template("serveurs.html", machines=machines, error=error, nom=session["nom"], privilege=session["privilege"])

@serveurs_bp.route("/edit_serv", methods=["GET", "POST"])
def edit_serv():
    """
    Fonction de vérification des privilèges et de session pour modifier un serveur, l'utilisateur doit également
    être au moins gestionnaire. Il pourra seulement modifier l'adresse IP.
    """
    if not is_log():
        return redirect("/login")    
    if not priv(2):
        return redirect("/")  
    if request.form.get("nom"):
        nom = request.form.get("nom")
    else:
        return redirect("/serveurs")
    
    machine = Machines.query.get(nom)
    
    if not machine:
        return redirect("/serveurs")   
    if request.form.get("ip"):
        ip = request.form.get("ip")
        try:
            IPv4Address(ip)
        except:
            error = "Wrong address format"
            return render_template("edit_serv.html", error=error, machine=machine, nom=session["nom"], privilege=session["privilege"])
    else:
        return render_template("edit_serv.html", machine=machine, nom=session["nom"], privilege=session["privilege"])   
    if Machines.query.filter_by(IP=ip).first():
        error = "This IP has already been attributed"
        return render_template("edit_serv.html", error=error, machine=machine, nom=session["nom"], privilege=session["privilege"])    
    machine.IP = ip
    db.session.commit()
    
    return redirect("/serveurs")

@serveurs_bp.route("/del_serv", methods=["POST"])
def suppr_serv():
    """
    Fonction de suppression d'un serveur distant de la base de donnée, vérifie à nouveau la session et les 
    privilèges de l'utilisateur.
    """
    if not is_log():
        return redirect("/login")    
    if not priv(2):
        return redirect("/")   
    if request.form.get("nom"):
        nom = request.form.get("nom")
    else:
        return redirect("/serveurs")
    
    machine = Machines.query.get(nom)
    
    if machine:
        db.session.delete(machine)
        db.session.commit()  
 
    return redirect("/serveurs")

@serveurs_bp.route("/add_serv", methods=["POST"])
def ajout_serv():
    """
    Fonction d'ajout d'un serveur, l'utilisateur rentre le nom et l'IP qui 
    doit être dans un format valide.
    """
    if not is_log():
        return redirect("/login")   
    if not priv(2):
        return redirect("/")   
    nom = request.form.get("nom")
    ip = request.form.get("ip")   
    if not nom or not ip:
        return redirect("/serveurs?error=Please fill all the text fields")
    
    try:
        IPv4Address(ip)
    except:
        return redirect("/serveurs?error=Wrong address format")   
    if Machines.query.get(nom):
        return redirect("/serveurs?error=This machine already exists")   
    if Machines.query.filter_by(IP=ip).first():
        return redirect("/serveurs?error=This IP has already been attributed")
    
    for i in nom and ip:
        if " " in nom or " " in ip:
            return redirect("/serveurs?error=Spaces are prohibited")
    
    try:
        machine = Machines(nom=nom, IP=ip)
        db.session.add(machine)
        db.session.commit()
    except Exception as e:
        return redirect(f"/serveurs?error=Internal error : {e}")
    
    return redirect("/serveurs")