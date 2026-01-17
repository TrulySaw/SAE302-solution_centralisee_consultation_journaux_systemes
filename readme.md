
1. Mise en place du projet
2. Base de donnée
3. Accès aux clients
4. Dépannage
5. Installation du site sur un serveur WSGI

# 1. Mise en place du projet

## 1.1 Installation

Installer le dossier et décompressez le s'il est sous forme d'archive ou clonez le
Clonage :
```bash
apt install git python3-pip
cd sae_302
git clone https://github.com/TrulySaw/SAE302-solution_centralisee_consultation_journaux_systemes
```
Unzip :
```bash
apt install unzip
cd sae_302
unzip sae302.zip
```

```bash
apt install python3.11-venv 
python3 -m venv Journaux
.\Journaux\bin\activate
```

> [!NOTE]
> Vous pouvez si vous le souhaiter utiliser autre chose que venv mais c'est à vous de gérer la gestion de l'environnement
## 1.2 Installation des modules

```bash
sudo apt install -y mariadb-client libmariadb-dev-compat

./Journaux/bin/pip install -r requirements.txt
```

## 1.3 Choix du mot de passe admin :

```bash
./Journaux/bin/python3
```
```python
import werkzeug
werkzeug.security.generate_password_hash("x")
```

L'output devrait ressembler à `scrypt:` suivit de beaucoup de caractères, gardez-le pour plus tard.
Quittez ensuite python avec `exit()`

> [!TIP]
> Penser à mettre un mot de passe compliquer, nous recommandons qu'il sois d'au moins 12 caractères dont des spéciaux

# 2. Base de donnée

## 2.1 Installation de mariadb et accès

```bash
apt install mariadb-server -y
mariadb
```

> [!ATTENTION]
> Veuillez à être en root (ou sudo) pour accéder à la base de donnée tant que vous ne créé pas de compte

## 2.2 Création de la base de donnée et de ses tables

```sql
CREATE DATABASE sae302;

CREATE USER 'qamu'@'localhost' IDENTIFIED BY 'qamu';

GRANT ALL PRIVILEGES ON sae302.* To 'qamu'@'localhost' IDENTIFIED BY 'qamu';

USE sae302;

CREATE TABLE privilege (
	id INT PRIMARY KEY NOT NULL,
	nom VARCHAR(45) NOT NULL
);

CREATE TABLE role (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nom VARCHAR(45) NOT NULL,
	privilege INT NOT NULL
);

CREATE TABLE users (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nom VARCHAR(45) NOT NULL,
	password VARCHAR(255) NOT NULL,
	role INT NOT NULL,
	FOREIGN KEY (role) REFERENCES role(id)
);

INSERT INTO privilege VALUES ('1', 'Consultation des journaux');

INSERT INTO privilege VALUES ('2', 'Gestions des serveurs');

INSERT INTO privilege VALUES ('4', 'Administration des utilisateurs');

INSERT INTO role (nom, privilege) VALUES ('Utilisateur', '1');

INSERT INTO role (nom, privilege) VALUES ('Gestionnaire', '3');

INSERT INTO role (nom, privilege) VALUES ('Administrateur', '7');
```

Pour ajouter un compte admin : (N'oubliez pas de remplacer 'x' par votre mot de passe choisis auparavant et généré avec werkzeug)

```sql
INSERT INTO users (nom, password, role) VALUES ('admin', 'x', '3')
```

> [!NOTE]
> Cela devrais ressembler à :
> ```sql
> INSERT INTO users (nom, password, role) VALUES ('admin', 'scrypt:xxxxxxxxxxxxxxxxxxx', '3')
> ```

Si vous voulez changer le mot de passe de l'admin :

```sql
UPDATE users SET password = 'x' WHERE id = 1;
```

# 3. Accès aux clients

## 3.1 Génération de la clé ssh

```bash
ssh-keygen -f ~/.ssh/sae302_key -t rsa
```

> [!Attention]
> Ne mettez pas de mot de passe

> [!Info]
> _La partie 3.2 est à reproduire pour chaque client que vous voulez géré_
## 3.2 Création des comptes

Ici on créé un groupe et un utilisateur qui serons dédier à la lecture des journaux
```bash
apt install sudo -y
groupadd logs
useradd -m -G logs client

# A faire depuis votre serveur qui héberge l'application
scp sae302_key.pub root@<IP>:
# Et sur le client
mkdir /home/client/.ssh
cp sae302_key.pub /home/client/.ssh/sae302_key.pub
mv sae302_key.pub /home/client/.ssh/authorized_keys

# Ou du client
mkdir /home/client/.ssh
scp <compte>@<IP_Serveur>:.ssh/sae302_key.pub /home/client/.ssh/sae302_key.pub
cp /home/client/.ssh/sae302_key.pub /home/client/.ssh/authorized_keys

chown -R client:logs /home/client/.ssh
adduser client sudo

# Ajouter le dossier : /etc/sudoers.d/sudo_client
# Chaque ligne représente un journal que vous autorisé à la lecture si vous voulez ajouté un journal il faut rajouter une ligne avec son chemin absolu
# Il doit aussi faire partie du dossier /var/log
client ALL=(root) NOPASSWD: /usr/bin/cat /var/log/syslog
client ALL=(root) NOPASSWD: /usr/bin/cat /var/log/auth.log
client ALL=(root) NOPASSWD: /usr/bin/cat /var/log/kern.log
client ALL=(root) NOPASSWD: /usr/bin/cat /var/log/cron.log
```

# 4. Dépannage

>[!Info]
>La partie "Dépannage" contient des passages en cas de problèmes et des tests de vérification pour vérifier que tout fonctionne

Après l'ajout de chaque client nous vous conseillons de tester la connexion SSH manuellement avec :
```bash
ssh -i ~/.ssh/<SSH Key> client@<IP>
```
Exemple:
```bash
ssh -i ~/.ssh/sae302_key client@192.168.0.10
# Juste le ssh de base
ssh client@192.168.0.10
```

>[!IMPORTANT]
>Vous pouvez, selon la version de votre système besoin d'installer un paquet tel que `rsyslog` ce qui vous permettra d'avoir les fichiers de logs dans `/var/log/`.
# 5. Installation du site sur un serveur WSGI

Pour lancer sans WSGI
```bash
./Journaux/bin/python run.py
```

Accès via tunnel SSH :
```bash
ssh -L 5000:127.0.0.1:5000 <compte>@<IP_Serveur>
```

# 6. Bravo votre page est en ligne !
>
>Votre site est désormais en ligne, vous pouvez désormais y accédé avec votre adresse IP, le port de base est `5000` vous pouvez le changer en modifiant le fichier `/config/port` !
>

