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
            priv_user = session.get("privilege")
            if required_priv == 1:
                return priv_user >= 1
            if required_priv == 2:
                return priv_user >= 3
            if required_priv == 4:
                return priv_user == 7
    except:
        return False