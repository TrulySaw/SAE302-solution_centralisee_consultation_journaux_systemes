from flask import session

def is_log():
    """
    Vérification de l'authentification de l'utilisateur
    """
    try:
        if session["Loggedin"]:
            return True
    except:
        return False

def priv(required_priv):
    """
    Récupération des privilèges de l'utilisateur si connecté, en fonction de son rôle
    """
    try:
        if is_log():     
            if session.get("privilege") & required_priv:
                return True
        else:
            return app.redirect("/login")
    except:
        return False
