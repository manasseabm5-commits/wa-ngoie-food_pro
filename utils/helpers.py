import random
import string

def generer_code_commande(prenom):
    """
    Génère un code de commande unique basé sur le prénom.
    Exemple: Si prenom="Manasse", retourne "MANASSE-8K3P9F"
    """
    # 1. Nettoyer le prénom : tout en majuscules, sans espaces
    nom_propre = prenom.strip().upper().replace(" ", "")
    
    # Si le prénom est trop long, on peut le couper (optionnel), ici on le garde tel quel
    if not nom_propre:
        nom_propre = "CLIENT" # Sécurité au cas où
        
    # 2. Générer 6 caractères alphanumériques aléatoires (Majuscules + Chiffres)
    caracteres = string.ascii_uppercase + string.digits
    code_aleatoire = ''.join(random.choices(caracteres, k=6))
    
    # 3. Assembler le tout
    numero_commande = f"{nom_propre}-{code_aleatoire}"
    
    return numero_commande