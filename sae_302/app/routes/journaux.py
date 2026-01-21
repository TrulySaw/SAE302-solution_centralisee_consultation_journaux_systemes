from flask import Blueprint, render_template, request, redirect, session, current_app
import paramiko
import fabric
from app.models import Machines
from app.log_check import priv
import os
import subprocess
import socket

journaux_bp = Blueprint('journaux', __name__)

def get_journaux():
    config_path = os.path.join(current_app.root_path, 'config', 'journaux')
    with open(config_path, 'r') as cnf:
        journaux = []
        ljournaux = cnf.readlines()
        for ljournal in ljournaux:
            ljournal = ljournal.strip()
            journaux.append('/var/log/' + ljournal)
    return journaux

def ping(ip):
    try:
        ping = subprocess.run(
            ['ping', '-c', '1', '-W', '1', ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2)
        fping = ping.returncode
    except Exception:
        return False
    if fping != 0:
        return False
    else:
        return True

def journal_from(client, fich_journal, pkey, res):
    """
    Récupération du journal distant via fabric
    Et ajout dans la liste res des logs formatés
    """
    with fabric.Connection(host=client.IP, user="client", connect_kwargs={"pkey": pkey, "timeout": 3}) as cnx:
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
    return res

def handle_error(error):
    if error:
        lmachines = Machines.query.all()
        journaux = get_journaux()
        return render_template("/select_journaux.html", error=error, journaux=journaux, machines=lmachines, nom=session["nom"], privilege=session["privilege"])
    else:
        return None

@journaux_bp.route("/journaux", methods=["GET", "POST"])
def journaux():
    """
    Fonction qui vérifie les privilèges de l'utilisateur. Grâce à paramiko on récupère la clé sur les machines
    distantes et ping pour vérifier que la vm est allumée.
    """
    if not priv(1):
        return redirect("/")
    
    journaux = get_journaux()
    
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
        
        error = None
        # ping pour tester si la VM est allumée
        for ip in ips:
            client = Machines.query.filter_by(IP=ip).first()
            if client:
                if ping(ip):
                    continue
                else:
                    return handle_error("Host " + client.nom + " unreachable")
            else:
                return handle_error("Unknown host")
        # boucle de récupération de journaux
        for ip in ips:
            client = Machines.query.filter_by(IP=ip).first()
            try:
                res = journal_from(client, fich_journal, pkey, res)
            except socket.timeout:
                return handle_error(f"Connection to {client.nom} timed out")
            except Exception as e:
                return handle_error(f"Error with {client.nom}: {str(e)}")
        # lambda - fonction temporaire pour trier les dates des logs par ordre décroissant      
        res.sort(key=lambda x: x[0], reverse=True)
        
        return render_template("/journaux.html", res=res, nom=session["nom"], privilege=session["privilege"])
    else:
        lmachines = Machines.query.all()
        return render_template("/select_journaux.html", journaux=journaux, machines=lmachines, nom=session["nom"], privilege=session["privilege"])
