from app import create_app

# création de l'application flask, et récupération du port
app = create_app()
with open("./app/config/port", "r") as p:
    port = p.readline().strip()

if __name__ == '__main__':
    app.run(debug=True, port=port)
