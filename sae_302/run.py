from app import create_app

# creation de l'application flask
app = create_app()
with open("./config/ports", "r") as p:
    port = p.readlines().strip()

if __name__ == '__main__':
    app.run(debug=True, port=port)
    
