from flask import Flask

app = Flask(__name__)  # Création de l'application

@app.route('/')  # Page d'accueil
def home():
    return "Bienvenue sur mon premier site Flask !"

if __name__ == '__main__':
    app.run(debug=True)
