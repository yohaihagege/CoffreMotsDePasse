import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk  # Ajout du module ttk pour améliorer l'apparence

import base64
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Fonction pour générer une clé de chiffrement
def generer_cle_depuis_mdp(mot_de_passe: str, sel: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sel,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(mot_de_passe.encode()))

# Fonction de chiffrement et déchiffrement
def chiffrer(cle, texte):
    f = Fernet(cle)
    return f.encrypt(texte.encode())

def dechiffrer(cle, texte_chiffre):
    f = Fernet(cle)
    return f.decrypt(texte_chiffre).decode()

# Fichier de stockage des données chiffrées
fichier_donnees = "donnees.json"

# Chargement et sauvegarde des données JSON
def charger_donnees():
    if os.path.exists(fichier_donnees):
        with open(fichier_donnees, "r") as f:
            return json.load(f)
    return {}

def sauvegarder_donnees(data):
    with open(fichier_donnees, "w") as f:
        json.dump(data, f)

# Création de l'application Tkinter
app = tk.Tk()
app.title("Coffre-fort de mots de passe 🔒")
app.geometry("400x400")
app.configure(bg="#2C3E50")  # Couleur de fond sombre

# Ajout d'un style pour rendre l'application plus moderne
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=6)
style.configure("TLabel", font=("Arial", 12), background="#2C3E50", foreground="white")

# Demande du mot de passe maître
mot_de_passe_maitre = simpledialog.askstring("Mot de passe 🔑", "Entrez votre mot de passe maître :", show='*')

if not mot_de_passe_maitre:
    messagebox.showerror("Erreur", "Aucun mot de passe fourni. Fermeture.")
    app.destroy()
    exit()

# Sel constant et génération de la clé
sel = b'mon_sel_unique_et_constant'
cle = generer_cle_depuis_mdp(mot_de_passe_maitre, sel)

# Fonction pour ajouter un mot de passe
def ajouter_mot_de_passe():
    site = simpledialog.askstring("Ajouter un site 🌐", "Nom du site :")
    identifiant = simpledialog.askstring("Ajouter un identifiant 👤", "Identifiant :")
    mot_de_passe = simpledialog.askstring("Ajouter un mot de passe 🔑", "Mot de passe :")

    if site and identifiant and mot_de_passe:
        data = charger_donnees()
        donnees = f"{identifiant}:{mot_de_passe}"
        donnees_chiffrees = chiffrer(cle, donnees)
        data[site] = donnees_chiffrees.decode()
        sauvegarder_donnees(data)
        messagebox.showinfo("Succès ✅", f"Mot de passe enregistré pour {site}.")
    else:
        messagebox.showerror("Erreur ❌", "Champs incomplets.")

# Fonction pour afficher un mot de passe
def afficher_mot_de_passe():
    site = simpledialog.askstring("Afficher 🔍", "Nom du site à afficher :")
    data = charger_donnees()

    if site in data:
        donnees_chiffrees = data[site].encode()
        try:
            donnees_claires = dechiffrer(cle, donnees_chiffrees)
            identifiant, mot_de_passe = donnees_claires.split(":")
            messagebox.showinfo("Résultat 🎯", f"Identifiant : {identifiant}\nMot de passe : {mot_de_passe}")
        except:
            messagebox.showerror("Erreur ❌", "Impossible de déchiffrer les données.")
    else:
        messagebox.showerror("Erreur ❌", "Aucune donnée trouvée.")

# Ajout des boutons avec ttk et un bel espacement
frame = ttk.Frame(app, padding=20)
frame.pack(expand=True)

ttk.Button(frame, text="Ajouter un mot de passe 📝", command=ajouter_mot_de_passe).pack(pady=10)
ttk.Button(frame, text="Afficher un mot de passe 🔍", command=afficher_mot_de_passe).pack(pady=10)
ttk.Button(frame, text="Quitter 🚪", command=app.destroy).pack(pady=10)

# Lancement de l'application
app.mainloop()
