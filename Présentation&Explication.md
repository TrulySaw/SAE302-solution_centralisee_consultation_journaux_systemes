1. Introduction
2. Structure de l'application
3. Architecture du système
4. Authentification et sécurité
5. Gestion des privilèges et rôles des utilisateurs
6. Gestion des utilisateurs
7. Gestion des machines distantes
---
1. Introduction

Ce projet a été réalisé par GROS Axel et DAVY Noah :

Axel - s'est occupé des parties : 
- authentification, 
- privilèges, 
- gestion des journaux des machines distantes,
- templates pour l'authentification (login.html) et les journaux (journaux.html, select_journaux.html).

Noah - s'est occupé des parties :
- modèles de base de données,
- gestion des utilisateurs, 
- gestion des machines distantes,
- templates pour les utilisateurs (users.html, edit_user.html) et les serveurs (serveurs.html, edit_serv.html).

Nous avons travaillé à deux sur le CSS et nous sommes souvent mutuellement corrigé et/ou avons amélioré nos parties.

1.1 Contexte du projet :
Ce projet consiste en la création d'une application web permettant la consultation et la gestion centralisée des journaux système (syslog) provenant de plusieurs machines distantes sous GNU/Linux. L'application s'inscrit dans le cadre de la SAE302 et répond à un besoin de surveillance centralisée d'un parc de serveurs.
Le système permet à des utilisateurs authentifiés de consulter les journaux système de machines distantes depuis une interface web unique, tout en respectant une politique stricte de contrôle d'accès basée sur les rôles.

1.2 Objectifs du projet :
Les objectifs principaux sont les suivants :
  - Consultation des journaux de plusieurs machines depuis une interface unique hébergée sur un serveur central,
  - Implémenter un système d'authentification robuste avec gestion des privilèges selon trois niveaux (utilisateur, gestionnaire, administrateur),
  - gestion dynamique des utilisateurs et des machines à surveiller,
  - possibilité d'ajouter d'autres types de journaux.

1.3 Principaux outils :
  - Backend : Flask (Python 3) pour le serveur web,
  - Base de données : MariaDB (utilisateurs, machines, rôles),
  - SQLAlchemy : accès à la base de donnée,
  - Connexions SSH : Paramiko et Fabric pour la communication sécurisée avec les machines distantes,
  - Frontend : HTML5 et CSS3 pour l'interface utilisateur,
  - Moteur de templates : Jinja2 (intégré à Flask) pour les des pages de l'application,
  - Sécurité : Werkzeug pour le hashage sécurisé des mots de passe.
---
2. Structure de l'application

L'application est organisée de cette manière :
```
├── app                                  
│   ├── config
│   │   └── journaux                         # fichier contenant les différents journaux consultables
│   ├── __init__.py                          # création de l'application, création de l'instance de manipulation de la base de données (db), enregistrement des blueprints
│   ├── log_check.py                         # fonctions vérifiant l'état de la session (is_log (vérifier que l'utilisateur est authentifié), priv (récupération des privilèges de l'utilisateur connecté)
│   ├── models.py                            # modèles récupérant les informations des tables de la base de données (Users, Machines, Role)
│   ├── requirements.txt                     # paquets à installer pour l'application
│   ├── routes
│   │   ├── __init__.py                      # importation des routes            
│   │   ├── auth.py                          # authentification (login, logout)
│   │   ├── journaux.py                      # visualisation des logs des machines distantes  
│   │   ├── serveurs.py                      # gestion des machines distantes (modification, ajout, suppression)
│   │   └── users.py                         # gestion des utilisateurs (modification, ajout, suppression)
│   ├── static
│   │   └── styles.css                       # feuille de style en CSS pour la mise en page
│   └── templates
│       ├── edit_serv.html                   # page de modification d'une machine distante 
│       ├── edit_user.html                   # page de modification d'un utilisateur
│       ├── index.html                       # page d'accueil
│       ├── journaux.html                    # page affichant les machines et les journaux disponibles
│       ├── login.html                       # page d'authentification
│       ├── select_journaux.html             # sélection d'un/plusieurs journal(aux) et de la/des machine(s)
│       ├── serveurs.html                    # page listant les machines distantes
│       └── users.html                       # page listant les utilisateurs
├── config.py                                # paramètres généraux de configuration globale (connexion à la base de données)
└── run.py                                   # lance le serveur flask avec app.run()
```
---
3. Architecture du système

3.1 Architecture générale :
Le système suit une architecture client-serveur à trois niveaux avec communication SSH vers les machines distantes :
```
                    ┌─────────────────┐
                    │  Navigateur Web │  (Interface utilisateur)
                    └────────┬────────┘
                             │ HTTP/HTTPS
                             │
                    ┌────────▼────────┐
                    │ Serveur Central │  (Serveur Flask + MariaDB)
                    │   (Machine 0)   │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │ SSH        │ SSH        │ SSH
                │            │            │
         ┌──────▼──────┐ ┌──▼────────┐ ┌─▼──────────┐
         │  Machine 1  │ │ Machine 2 │ │ Machine 3  │  (Machines distantes)
         │ GNU/Linux   │ │ GNU/Linux │ │ GNU/Linux  │
         └─────────────┘ └───────────┘ └────────────┘
```
3.2 Composants du système :

3.2.1 Serveur central :
Le serveur central héberge :
  - Application Flask : serveur web configuré sur le port 5000,
  - Base de données MariaDB : stockage des utilisateurs, machines et rôles,
  - Clé SSH privée : stockée dans /home/qamu/.ssh/sae302_key pour l'authentification auprès des machines distantes,
  - Templates Jinja2 : pages HTML dynamiques dans le dossier templates/
  - Fichiers CSS : fichier de style pour la mise en page dans static/

Tâches :
  - Authentifier les utilisateurs et maintenir les sessions,
  - Aller chercher dans la base de données les informations relatives aux demandes de l'utilisateur,
  - Établir des connexions SSH vers les machines distantes,
  - Parser et formater les journaux pour l'affichage,
  - Gestion des machines distantes et des utilisateurs.

3.2.2 Base de données MariaDB :
La base de données sae302 contient trois tables principales :
  - users : informations des utilisateurs,
  - machines : liste des machines distantes,
  - role : définition des rôles avec privilèges associés,
  - privilege : privilèges et définitions.

3.2.3 Machines distantes (Machines 1, 2, 3) :
Chaque machine distante est un serveur GNU/Linux configuré avec :
  - Système d'exploitation : GNU/Linux (distribution Debian, Ubuntu...),
  - Compte utilisateur client : compte dédié à la consultation des logs,
  - Configuration sudo : permet à l'utilisateur client d'exécuter par exemple : sudo cat /var/log/syslog sans mot de passe, possible pour d'autres journaux comme auth.log, kern.log ou cron.log, 
  - Serveur SSH : autorise les connexions par clé publique pour l'utilisateur client,
  - Clé publique : la clé publique correspondant à /home/qamu/.ssh/sae302_key (sae302_key.pub) est ajoutée dans /home/client/.ssh/authorized_keys.

3.3 Fonctionnement général :
Le processus de consultation d'un journal suit ces étapes précises :
  - Utilisateur -> Navigateur : l'utilisateur sélectionne une ou plusiers machine(s) et clique sur "Afficher",
  - Navigateur -> Serveur Flask : requête POST envoyée avec l'IP de la machine sélectionnée,
  - Serveur Flask -> Base de données : vérification des privilèges de l'utilisateur,
  - Serveur Flask -> Machine distante : connexion SSH et exécution de la commande sudo suivie d'un cat du/des journal(aux) sélectionné(s),
  - Machine distante -> Serveur Flask : contenu du journal transmis via SSH,
  - Serveur Flask : parsing et formatage des données,
  - Serveur Flask -> Navigateur : génération et envoi de la page HTML avec les journaux,
  - Navigateur : affichage des logs coupés en différentes parties grâce au parsing.
---
4. Authentification et sécurité

4.1 Processus d'authentification :
Le système d'authentification suit ces étapes :
  - L'utilisateur rentre ses identifiants (stockés dans la table users de la base de donnée sae302),
  - Les éléments rentrés sont comparés avec ce qui se trouve dans la base de donnée via une requête envoyée par le serveur grâce à la méthode POST,
  - SQLAlchemy recherche un utilisateur avec le nom et le mot de passe donnés,
  - Récupération des privilèges associés au rôle de l'utilisateur,
  - Création de la session et redirection vers la page d'accueil.

4.2 Sécurité mise en place :
  - Un compte Client créé sur les machines distantes et ajouté au groupe sudo ne servant qu'à la consultation des journaux,
  - Un fichier bash se trouvant dans /usr/local/bin restreignant les commandes sudo pouvant être exécutées à distance sans mot de passe,
  - Des restrictions sudo dans /etc/sudoers.d/sudo_client, exemple : 
      dhcp ALL=(client) NOPASSWD: /usr/bin/cat /var/log/syslog
  - Une authentification par clé privée (sur le serveur central - id_rsa) et clé publique (se trouvant dans /home/client/.ssh/ et qui se nomme id_rsa.pub sur les machines distantes),
  - Une double authentification par une autre paire de clés privée/publique pour le compte Client se trouvant dans /home/client/.ssh/authorized_keys.
---
5. Gestion des privilèges et rôles des utilisateurs

La gestion des rôles et privilèges de chaque utilisateur se fait par le biais de 2 tables présentes dans la base de données : 
  - La table role : 
    CREATE TABLE role (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nom VARCHAR(45) NOT NULL,
        privilege INT NOT NULL
    );

  - La table privilege : 
    CREATE TABLE privilege (
        id INT PRIMARY KEY NOT NULL,
        nom VARCHAR(45) NOT NULL
    );

  - Dans la table users, on précise à l'aide d'une clé étrangère le rôle de l'utilisateur auquel est associé les privilèges : 
    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nom VARCHAR(45) NOT NULL,
        password VARCHAR(255) NOT NULL,
        role INT NOT NULL,
        FOREIGN KEY (role) REFERENCES role(id)
    );

  - Les rôles sont les suivants : 
    . Un simple utilisateur a comme rôle 1 --> il ne peut qu'accéder aux logs des machines distantes,
    . Un gestionnaire a comme rôle 3 --> il peut accéder aux logs des machines distantes et gérer ces machines (les modifier, en rajouter/supprimer),
    . Un administrateur a comme rôle 7 --> il peut accéder aux logs des machines distantes, gérer ces machines et également les utilisateurs (les modifier, en ajouter/supprimer).

  - Les privilèges sont les suivants :
    Dans la table privilege de la base de données sae302, les privilèges sont en binaire (puissances de 2) --> on additionne les valeurs des privilèges précédents pour chaque privilège plus élevé :
    . Un utilisateur se voyant attribuer le rôle 1 aura comme privilège 1 - Consultation des journaux,
    . Un gestionnaire se voyant attribuer le rôle 2 aura comme privilège 3 (1+2) - Consultation des journaux et gestion des machines distantes,
    . Un administrateur se voyant attribuer le rôle 3 aura comme privilège 7 (1+2+4) - Consultation des journaux, gestion des machines distantes ainsi que des utilisateurs.
---
6. Gestion des utilisateurs
7. 
Un utilisateur disposant des droits d'administration (rôle 3 avec privilège 1+2+4 = 7) aura la possibilité d'ajouter, modifier, supprimer un utilisateur.

6.1 Ajouter un utilisateur :
  - L'utilisateur clique sur l'élément "Utilisateurs" présent dans le header de l'interface de l'application web,
  - Complète les champs obligatoires "Username" et "Password" et sélectionnera le rôle qu'il voudra attribuer à ce nouvel utilisateur,
  - Clique sur "Ajouter" - cette action va ajouter un utilisateur dans la table "users" de la base de donnée "sae302",
  - Vérifier que le nouvel utilisateur apparaît bien dans la liste des utilisateurs.

6.2 Modifier un utilisateur :
  - L'utilisateur clique sur l'élément "Utilisateurs" présent dans le header de l'interface de l'application web,
  - L'utilisateur voit la liste des utilisateurs (Liste des utilisateurs) et clique sur le bouton "Modifier" se trouvant à côté de chaque utilisateur, il sera redirigé vers une autre page,
  - Sur cette nouvelle page, il remplace le contenu des champs qu'il veut modifier par les nouvelles valeurs,
  - Clique sur "Modifier" - cette action va mettre à jour dans la table "users" les informations relatives à l'utilisateur en question.
  - Vérifie que les modifications aient bien été appliquées.

6.3 Supprimer un utilisateur :
  - L'utilisateur clique sur l'élément "Utilisateurs" présent dans le header de l'interface de l'application web,
  - L'utilisateur voit la liste des utilisateurs (Liste des serveurs),
  - Clique sur le bouton "Supprimer" se trouvant également à côté de chaque utilisateur,
  - Cette action va supprimer l'utilisateur en question de la base de données (action irréversible, il faudra recréer l'utilisateur en cas de fausse manipulation).
---
7. Gestion des machines distantes

Un utilisateurdisposant des droits de gestion (rôle 2 avec privilège 1+2 = 3)
7.1 Ajouter une machine distante :
  - L'utilisateur clique sur l'élément "Serveurs" présent dans le header de l'interface de l'application web,
  - Complète les champs obligatoires "Name" et "IP Address",
  - Clique sur "Ajouter" - cette action va ajouter la nouvelle machine dans la table "machines",
  - Vérifie que la machine ajoutée apparaît bien dans la liste des machines.

7.2 Modifier une machine distante :
  - L'utilisateur clique sur l'élément "Serveurs" présent dans le header de l'interface de l'application web,
  - Dans la liste des machines distantes devant s'afficher (Liste des serveurs), l'utilisateur clique sur le bouton "Modifier" se trouvant à côté de chaque machine, il sera redirigé vers une nouvelle page,
  - Sur cette nouvelle page, il peut seulement modifier l'adresse IP de la machine,
  - Clique sur le bouton "Modifier" - Cette action va modifier dans la table "machines" l'IP correspondant à la machine en question.
  - Vérifie que les modifications aient bien été appliquées.

7.3 Supprimer une machine distante :
  - L'utilisateur clique sur l'élément "Serveurs" présent dans le header de l'interface de l'application web,
  - La liste des machines distantes s'affiche (Liste des serveurs),
  - Clique sur le bouton "Supprimer" se trouvant à côté de chaque machine,
  - Cette action va supprimer la machine en question de la base de données (action irréversible, il faudra recréer la machine en cas de fausse manipulation).
