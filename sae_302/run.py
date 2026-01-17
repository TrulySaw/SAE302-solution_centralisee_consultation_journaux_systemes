from app import create_app

# creation de l'application flask
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
