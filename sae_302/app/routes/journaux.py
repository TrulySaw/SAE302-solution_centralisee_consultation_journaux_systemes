from flask import Blueprint, render_template, request, redirect, session, current_app
import paramiko
import fabric
from app.models import Machines
from app.log_check import is_log, priv
import os

journaux_bp = Blueprint('journaux', __name__)

@journaux_bp.route("/journaux", methods=["GET", "POST"])
def journaux():
    """
    FOnction de vérification d'existence de la session, l'utilisateur ne peut pas accéder 
    au service de consultation de journaux s'il n'est pas au moins utilisateur
    avec privilèges = 1. Grâce à paramiko et fabric, accès distant depuis le compte client
    créé sur les machines distantes.
    """
    if not is_log():
        return redirect("/login")   
    if not priv(1):
        return redirect("/")
    
    config_path = os.path.join(current_app.root_path, 'config', 'journaux')
    with open(config_path, 'r') as cnf:
        journaux = []
        ljournaux = cnf.readlines()
        for ljournal in ljournaux:
            ljournal = ljournal.strip()
            journaux.append('/var/log/' + ljournal)   
    if request.method == "POST":
        ip_check = request.form.getlist("ip")       
        if not ip_check:
            lmachines = Machines.query.all()
            error = "Please select at least one machine"
            return render_template("/select_journaux.html", journaux=journaux, machines=lmachines, error=error, nom=session["nom"], privilege=session["privilege"])
        if request.form.get("journal") in journaux:
            fich_journal = request.form.get("journal")
        else:
            fich_journal = "/var/log/syslog"
        
        res = []
        # recuperation de la cle privee sur le serveur central pour l'authentification du compte client
        # sur les machines distantes
        pkey = paramiko.RSAKey.from_private_key_file(os.getenv("HOME") + "/.ssh/sae302_key")
        ips = request.form.getlist("ip")
        
        for ip in ips:
            client = Machines.query.filter_by(IP=ip).first()
            if client:
                # grâce au module fabric, connection aux machines clients - hôte IP machine - user - client
                # afin d'exécuter la commande cat pour récupérer le contenu des fichiers de logs
                with fabric.Connection(host=client.IP, user="client", connect_kwargs={"pkey": pkey}) as cnx:
                    journal = cnx.run(f"sudo cat {fich_journal}", hide=True).stdout
                    contenu = journal.split('\n')
                    
                    for log in contenu:
                        format = log.split(" ")
                        if len(format) >= 4:
                            date = format[0]
                            machine = format[1]
                            service = format[2]
                            data = ""
                            for elem in range(3, len(format)):
                                data += " " + format[elem]
                            res.append([date, machine, service, data])      
        res.sort(key=lambda x: x[0], reverse=True)
        
        return render_template("/journaux.html", res=res, nom=session["nom"], privilege=session["privilege"])
    else:
        lmachines = Machines.query.all()
        return render_template("/select_journaux.html", journaux=journaux, machines=lmachines, nom=session["nom"], privilege=session["privilege"])