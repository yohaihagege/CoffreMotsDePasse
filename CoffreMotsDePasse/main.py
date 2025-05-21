import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import base64, json, os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# ---------- Sécurité ----------
def generer_cle_depuis_mdp(mot_de_passe: str, sel: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sel,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(mot_de_passe.encode()))

def chiffrer(cle, texte): return Fernet(cle).encrypt(texte.encode())
def dechiffrer(cle, texte_chiffre): return Fernet(cle).decrypt(texte_chiffre).decode()

# ---------- Données ----------
fichier_donnees = "donnees.json"

def charger_donnees():
    if os.path.exists(fichier_donnees):
        with open(fichier_donnees, "r") as f:
            return json.load(f)
    return {}

def sauvegarder_donnees(data):
    with open(fichier_donnees, "w") as f:
        json.dump(data, f)

# ---------- Interface ----------
app = tk.Tk()
app.title("🔐 Coffre-fort de mots de passe")
app.geometry("450x500")
app.configure(bg="#1e272e")

# ---------- Style moderne ----------
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 11), padding=10, foreground="#ffffff", background="#3742fa")
style.map("TButton",
    background=[("active", "#5352ed")],
    foreground=[("disabled", "#dcdde1")]
)
style.configure("TLabel", font=("Segoe UI", 11), background="#1e272e", foreground="white")

# ---------- Mot de passe maître ----------
mot_de_passe_maitre = simpledialog.askstring("Mot de passe 🔑", "Entrez votre mot de passe maître :", show='*')
if not mot_de_passe_maitre:
    messagebox.showerror("Erreur", "Aucun mot de passe fourni. Fermeture.")
    app.destroy()
    exit()

sel = b'mon_sel_unique_et_constant'
cle = generer_cle_depuis_mdp(mot_de_passe_maitre, sel)

# ---------- Fonctions ----------
def ajouter_mot_de_passe():
    site = simpledialog.askstring("Site 🌐", "Nom du site :")
    identifiant = simpledialog.askstring("Identifiant 👤", "Identifiant :")
    mot_de_passe = simpledialog.askstring("Mot de passe 🔑", "Mot de passe :")

    if site and identifiant and mot_de_passe:
        data = charger_donnees()
        donnees = f"{identifiant}:{mot_de_passe}"
        donnees_chiffrees = chiffrer(cle, donnees)
        data[site] = donnees_chiffrees.decode()
        sauvegarder_donnees(data)
        messagebox.showinfo("✅ Succès", f"Mot de passe enregistré pour {site}.")
    else:
        messagebox.showerror("Erreur", "Champs incomplets.")

def afficher_mot_de_passe():
    site = simpledialog.askstring("Recherche 🔍", "Nom du site :")
    data = charger_donnees()

    if site in data:
        try:
            donnees_claires = dechiffrer(cle, data[site].encode())
            identifiant, mot_de_passe = donnees_claires.split(":")
            messagebox.showinfo("🔐 Résultat", f"Identifiant : {identifiant}\nMot de passe : {mot_de_passe}")
        except:
            messagebox.showerror("Erreur", "Échec du déchiffrement.")
    else:
        messagebox.showerror("Erreur", "Aucune donnée trouvée.")

# ---------- Widgets ----------
ttk.Label(app, text="Bienvenue dans votre coffre-fort de mots de passe", font=("Segoe UI", 13, "bold")).pack(pady=30)

container = ttk.Frame(app, padding=30, style="Card.TFrame")
container.pack(expand=True)

ttk.Button(container, text="📝 Ajouter un mot de passe", command=ajouter_mot_de_passe).pack(pady=10, fill='x')
ttk.Button(container, text="🔍 Afficher un mot de passe", command=afficher_mot_de_passe).pack(pady=10, fill='x')
ttk.Button(container, text="🚪 Quitter", command=app.destroy).pack(pady=20, fill='x')

# ---------- Lancement ----------
app.mainloop()
