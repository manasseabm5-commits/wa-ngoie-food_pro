 
import re
from flask import Blueprint, render_template, request, make_response
from flask_login import current_user

ai_bp = Blueprint('ai', __name__)


# =====================================================================
# 1. UTILITAIRES DE SÉCURITÉ & DE NETTOYAGE DU TEXTE
# =====================================================================

def _is_admin(user) -> bool:
    """
    Vérifie en toute sécurité si l'utilisateur possède les droits administrateur.
    Compatible avec un attribut `role` (chaîne de caractères) ou `is_admin` (booléen).
    """
    if not user or not user.is_authenticated:
        return False

    if hasattr(user, "role") and getattr(user, "role"):
        return str(getattr(user, "role")).strip().lower() == "admin"

    if hasattr(user, "is_admin"):
        return bool(getattr(user, "is_admin"))

    return False


def _is_creator(user) -> bool:
    """
    Reconnaissance exclusive : permet à l'IA d'identifier son concepteur (ABM)
    lorsqu'il est connecté sur la plateforme.
    """
    if not user or not user.is_authenticated:
        return False

    email = str(getattr(user, "email", "")).lower()
    nom = str(getattr(user, "nom", "")).lower()
    username = str(getattr(user, "username", "")).lower()

    return any("manasseabm5" in email for email in [email]) or \
           any(tag in nom or tag in username for tag in ["manassé", "manasse", "akonda", "bwama", "abm", "cbfw"])


def _clean_text(text: str) -> str:
    """
    Normalisation avancée : conversion en minuscules, suppression de la ponctuation
    lourde et des espaces superflus pour garantir une correspondance parfaite.
    """
    t = (text or "").strip().lower()
    t = re.sub(r"[^\w\sàâäéèêëîïôöùûüç'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# =====================================================================
# 2. MOTEUR DE DÉCISION ABM AI (200+ INTENTIONS LOGIQUES)
# =====================================================================

def generate_response(raw_message: str, user) -> str:
    """
    Analyse le message de l'utilisateur selon un ordre de priorité strict.
    Chaque bloc est conçu pour répondre avec précision en français impeccable.
    """
    text = (raw_message or "").strip()
    clean = _clean_text(text)

    is_admin_user = _is_admin(user)
    is_abm = _is_creator(user)

    # -----------------------------------------------------------------
    # ACCUEIL PERSONNALISÉ (MESSAGE VIDE)
    # -----------------------------------------------------------------
    if not text:
        if is_abm:
            return (
                "Salut Boss ! 👑 Quel plaisir de te voir connecté, Manassé.\n\n"
                "Tous les systèmes de Wa-Ngoie Food fonctionnent à merveille. "
                "Souhaites-tu vérifier le flux des commandes, tester la carte ou auditer les statistiques ?"
            )

        if is_admin_user:
            return (
                "Bonjour 👋 Je suis ABM AI, votre assistant d'administration Wa-Ngoie Food.\n\n"
                "Je suis opérationnel pour vous épauler sur :\n"
                "• 📦 La gestion de la carte, des prix et des stocks\n"
                "• 📋 La validation et le suivi des commandes\n"
                "• 👥 L'administration des comptes utilisateurs\n"
                "• 📊 Le suivi financier, les statistiques et les rapports\n\n"
                "Quelle tâche souhaitez-vous accomplir ?"
            )

        return (
            "Bonjour 👋 Je suis ABM AI, votre assistant gourmand sur Wa-Ngoie Food !\n\n"
            "Je suis à votre entière disposition pour :\n"
            "• 🍔 Vous présenter notre menu et nos spécialités\n"
            "• 🛒 Composer votre panier et passer commande\n"
            "• 🚚 Suivre l'avancement de votre livraison en temps réel\n"
            "• 📄 Récupérer vos factures et reçus PDF\n\n"
            "Comment puis-je vous aider aujourd'hui ?"
        )

    # -----------------------------------------------------------------
    # PRIORITÉ 0 : IDENTITÉ, CONCEPTEUR & FIERTÉ TECHNIQUE
    # -----------------------------------------------------------------
    if any(k in clean for k in ["qui t a cree", "qui ta cree", "qui es tu", "qui es-tu", "c est quoi abm", "qui est abm", "que signifie abm", "createur", "concepteur", "manasse", "manassé", "akonda", "bwama", "cbfw", "developpeur", "développeur", "qui a fait le site", "isipa", "licence 3"]):
        return (
            "🤖 **À propos de moi :**\n\n"
            "Je suis **ABM AI**, l'assistant intelligent et 100 % local du restaurant **Wa-Ngoie Food** !\n\n"
            "J'ai été conçu, architecturé et développé par **Manassé Akonda Bwama (alias ABM / CBFW)**, "
            "développeur logiciel et étudiant en Licence 3 Informatique de Gestion à l'ISIPA.\n\n"
            "Ma mission est de simplifier l'expérience des clients et d'automatiser l'administration quotidienne "
            "de l'établissement avec efficacité ! 🚀"
        )

    if any(k in clean for k in ["comment tu fonctionnes", "tu utilises quelle api", "chatgpt", "openai", "local", "technologie", "code source", "python", "flask"]):
        return (
            "⚙️ **Mon architecture technique :**\n\n"
            "Je fonctionne **100 % localement** sur le serveur de Wa-Ngoie Food ! "
            "Je ne dépends d'aucune API externe ni de services tiers payants.\n\n"
            "Je garantis une confidentialité totale de vos données tout en assurant une rapidité de réponse instantanée."
        )

    # -----------------------------------------------------------------
    # PRIORITÉ 1 : ADMINISTRATION DU RESTAURANT (RÉSERVÉ AUX ADMINS)
    # -----------------------------------------------------------------
    if any(k in clean for k in ["dashboard", "tableau de bord", "espace admin", "administration", "panel admin"]):
        if is_admin_user:
            return (
                "👑 **Vue d'ensemble du Tableau de Bord :**\n\n"
                "Votre interface centralise la supervision complète du restaurant :\n"
                "• **Produits & Catégories :** Mise à jour immédiate du menu\n"
                "• **Commandes :** Validation et suivi des flux de livraison\n"
                "• **Utilisateurs :** Gestion des rôles et des comptes\n"
                "• **Statistiques :** Analyse des revenus et des performances\n\n"
                "👉 Utilisez le menu latéral pour naviguer entre vos modules."
            )
        return "⚠️ L'accès aux informations du tableau de bord administratif est restreint au personnel de direction."

    if any(k in clean for k in ["ajouter produit", "nouveau produit", "creer produit", "ajouter un plat", "mettre un plat"]):
        if is_admin_user:
            return (
                "📦 **Ajouter un nouveau produit à la carte :**\n\n"
                "1️⃣ Ouvrez **Dashboard Admin → Produits**.\n"
                "2️⃣ Cliquez sur **« Nouveau produit »**.\n"
                "3️⃣ Saisissez le nom, la catégorie, le prix, une description détaillée et une image.\n"
                "4️⃣ Enregistrez : le produit sera instantanément disponible pour les clients !"
            )
        return "⚠️ L'ajout de produits à la carte est réservé aux administrateurs."

    if any(k in clean for k in ["modifier produit", "changer prix", "modifier plat", "prix du plat", "editer produit", "corriger prix"]):
        if is_admin_user:
            return (
                "✏️ **Modifier un plat existant :**\n\n"
                "Dans **Dashboard Admin → Produits**, trouvez l'article dans la liste et cliquez sur **« Modifier »**.\n"
                "Vous pourrez actualiser son tarif, changer sa description ou modifier sa photo promotionnelle."
            )
        return "⚠️ La modification des prix et des produits est une action administrative."

    if any(k in clean for k in ["supprimer produit", "retirer plat", "enlever produit", "effacer plat", "desactiver produit"]):
        if is_admin_user:
            return (
                "🗑️ **Supprimer ou masquer un article :**\n\n"
                "Dans la liste des produits du Dashboard Admin, cliquez sur le bouton rouge **« Supprimer »**.\n"
                "💡 *Conseil :* Si le produit a un historique de commandes, préférez le marquer comme indisponible pour conserver vos archives comptables."
            )
        return "⚠️ La suppression d'articles de la carte est une fonction administrative."

    if any(k in clean for k in ["categorie", "categories", "ajouter categorie", "gerer les categories", "modifier categorie"]):
        if is_admin_user:
            return (
                "🗂️ **Gestion des catégories du Menu :**\n\n"
                "Dans **Dashboard Admin → Catégories**, vous pouvez structurer la carte en créant, modifiant "
                "ou supprimant des sections (par exemple : *Plats chauds*, *Accompagnements*, *Boissons*, *Desserts*)."
            )
        return "⚠️ La gestion des catégories de la carte est réservée aux administrateurs."

    if any(k in clean for k in ["valider commande", "accepter commande", "confirmer commande", "commande en attente", "preparer commande admin"]):
        if is_admin_user:
            return (
                "✅ **Valider une commande client :**\n\n"
                "1️⃣ Allez dans **Dashboard Admin → Commandes** et filtrez par statut **« En attente »**.\n"
                "2️⃣ Cliquez sur la commande pour examiner le contenu et l'adresse.\n"
                "3️⃣ Cliquez sur **« Valider / En préparation »**.\n"
                "🔥 Le client sera averti immédiatement et son reçu PDF se mettra à jour."
            )
        return "⚠️ La validation des commandes est une tâche réservée à l'équipe du restaurant."

    if any(k in clean for k in ["refuser commande", "annuler commande admin", "rejeter commande", "bloquer commande"]):
        if is_admin_user:
            return (
                "❌ **Refuser une commande client :**\n\n"
                "En cas d'impossibilité de servir un plat, ouvrez la commande concernée et cliquez sur **« Refuser / Annuler »**.\n"
                "💡 *Bonne pratique :* Appelez le client pour l'informer avec courtoisie et lui proposer un plat de remplacement."
            )
        return "⚠️ Le rejet administratif d'une commande est réservé au gérant."

    if any(k in clean for k in ["gestion des utilisateurs", "gerer les utilisateurs", "liste des clients", "promouvoir admin", "role admin", "bloquer compte"]):
        if is_admin_user:
            return (
                "👥 **Gestion des comptes et des rôles :**\n\n"
                "Depuis **Dashboard Admin → Utilisateurs**, vous pouvez :\n"
                "• Examiner la liste complète des clients inscrits\n"
                "• Consulter l'historique d'achats d'un utilisateur\n"
                "• Accorder ou retirer le rôle **Admin** à un collaborateur."
            )
        return "⚠️ La gestion des utilisateurs est strictement restreinte aux administrateurs."

    if any(k in clean for k in ["statistique", "statistiques", "chiffre d affaire", "chiffre d'affaire", "revenu", "revenus", "vente", "ventes", "rapport", "rapports", "bilan"]):
        if is_admin_user:
            return (
                "📊 **Analyse financière & Performances :**\n\n"
                "Le Dashboard génère des indicateurs précis en temps réel :\n"
                "• **Chiffre d'affaires :** Vue journalière, hebdomadaire et mensuelle\n"
                "• **Palmarès des ventes :** Classement des plats et boissons les plus commandés\n"
                "• **Activité :** Volume de commandes validées et en cours\n\n"
                "👉 Ouvrez la section **« Rapports / Stats »** pour analyser l'évolution financière du restaurant."
            )
        return "⚠️ Les statistiques financières de l'établissement sont confidentielles."

    if any(k in clean for k in ["rupture", "stock", "epuise", "indisponible", "gerer le stock", "approvisionnement"]):
        if is_admin_user:
            return (
                "📦 **Gestion des ruptures de stock :**\n\n"
                "Lorsqu'un ingrédient est manquant, allez dans **Dashboard Admin → Produits** "
                "et changez l'état du plat en **« Indisponible / Rupture »**.\n"
                "Il restera visible sur la carte mais ne pourra plus être ajouté au panier des clients."
            )
        return "⚠️ La gestion des stocks est réservée à l'administration."

    # -----------------------------------------------------------------
    # PRIORITÉ 2 : COMPTES CLIENTS & SÉCURITÉ DES DONNÉES
    # -----------------------------------------------------------------
    if any(k in clean for k in ["creer un compte", "créer un compte", "inscription", "m inscrire", "inscrire", "s inscrire", "nouveau compte", "enregistrement"]):
        return (
            "📝 **Créer un compte client gratuit :**\n\n"
            "1️⃣ Cliquez sur le bouton **« Inscription »** en haut à droite.\n"
            "2️⃣ Renseignez votre nom, votre adresse email et un mot de passe sécurisé.\n"
            "3️⃣ Validez votre inscription pour accéder à votre espace.\n\n"
            "💡 Un compte vous permet de sauvegarder votre adresse, de suivre vos commandes en direct et de télécharger vos factures !"
        )

    if any(k in clean for k in ["connexion", "connecter", "me connecter", "se connecter", "login", "s identifier", "acceder a mon compte"]):
        return (
            "🔐 **Se connecter à votre espace :**\n\n"
            "1️⃣ Cliquez sur **« Connexion »** en haut de l'écran.\n"
            "2️⃣ Entrez votre adresse email et votre mot de passe.\n\n"
            "⚠️ En cas de problème, vérifiez qu'aucun espace vide ne s'est glissé au début ou à la fin de vos identifiants."
        )

    if any(k in clean for k in ["mot de passe oublie", "mdp oublie", "oublie mon mot de passe", "reinitialiser mot de passe", "changer mot de passe", "modifier mot de passe"]):
        return (
            "🔑 **Gestion de votre mot de passe :**\n\n"
            "Si vous avez oublié votre mot de passe, contactez notre support via la page **« Contact »**.\n"
            "Si vous êtes connecté, vous pouvez mettre à jour votre mot de passe à tout moment depuis les paramètres de votre compte client."
        )

    if any(k in clean for k in ["modifier profil", "changer adresse", "mon adresse", "mes informations", "mon profil", "compte client"]):
        return (
            "👤 **Gérer vos informations personnelles :**\n\n"
            "Rendez-vous dans votre espace client pour actualiser vos données :\n"
            "• Modification de votre numéro de téléphone\n"
            "• Mise à jour de votre adresse de livraison principale\n"
            "• Suivi de votre historique complet de commandes."
        )

    if any(k in clean for k in ["supprimer compte", "effacer compte", "rgpd", "confidentialite", "donnees personnelles", "mes donnees"]):
        return (
            "🛡️ **Protection de votre vie privée :**\n\n"
            "Nous respectons scrupuleusement la confidentialité de vos données personnelles.\n"
            "Pour demander la suppression définitive de votre compte ou de votre historique, envoyez une demande à notre administration via la page **« Contact »**."
        )

    if any(k in clean for k in ["deconnexion", "me deconnecter", "se deconnecter", "sortir"]):
        return (
            "🚪 **Se déconnecter en toute sécurité :**\n\n"
            "Cliquez simplement sur l'option **« Déconnexion »** présente dans le menu en haut à droite de votre écran. À très bientôt !"
        )

    # -----------------------------------------------------------------
    # PRIORITÉ 3 : CARTE, PLATS, BOISSONS & DIÉTÉTIQUE
    # -----------------------------------------------------------------
    if any(k in clean for k in ["menu", "plat", "plats", "carte", "repas", "specialite", "nourriture", "manger", "qu est ce que vous vendez", "que proposez vous"]):
        return (
            "🍔 **Découvrez le Menu Wa-Ngoie Food :**\n\n"
            "Explorez notre carte complète dans la rubrique **« Menu »** :\n"
            "• **Plats chauds & grillades :** Préparés à la commande\n"
            "• **Accompagnements :** Frites de pommes de terre, bananes plantains frites, riz, légumes savoureux\n"
            "• **Boissons fraîches :** Sodas, jus naturels, eau minérale\n\n"
            "🔍 *Astuce :* Utilisez la barre de recherche rapide sur le menu pour trouver votre plat en une seconde !"
        )

    if any(k in clean for k in ["accompagnement", "frites", "riz", "banane plantain", "bananes plantains", "legume", "garniture"]):
        return (
            "🍟 **Nos accompagnements au choix :**\n\n"
            "Pour accompagner vos plats principaux, nous proposons :\n"
            "• Des portions de frites dorées et croustillantes\n"
            "• Des bananes plantains frites (douces et savoureuses)\n"
            "• Du riz parfumé et des portions de légumes de saison."
        )

    if any(k in clean for k in ["boisson", "boissons", "jus", "soda", "eau", "coca", "fanta", "boire", "rafraichissement"]):
        return (
            "🥤 **Notre sélection de boissons :**\n\n"
            "Accompagnez votre repas avec notre gamme de boissons bien fraîches :\n"
            "• Sodas classiques et gazeux\n"
            "• Jus de fruits naturels\n"
            "• Eau minérale plate et gazeuse\n\n"
            "Ajoutez-les directement à votre panier depuis la section Boissons du menu !"
        )

    if any(k in clean for k in ["dessert", "desserts", "sucre", "douceur", "gateau"]):
        return (
            "🍰 **Une touche sucrée ?**\n\n"
            "Consultez la catégorie **« Desserts »** sur notre page Menu pour découvrir nos douceurs du jour et terminer votre repas sur une excellente note !"
        )

    if any(k in clean for k in ["sauce", "sauces", "piment", "mayonnaise", "ketchup"]):
        return (
            "🌶️ **Sauces & Assaisonnements :**\n\n"
            "Nous servons nos plats avec un choix d'assaisonnements savoureux. "
            "Si vous souhaitez un extra de piment fort, de mayonnaise ou de sauce douce, indiquez-le dans le champ **« Notes de commande »** !"
        )

    if any(k in clean for k in ["prix", "tarif", "combien coute", "coute combien", "cher", "promotion"]):
        return (
            "🏷️ **Transparence de nos tarifs :**\n\n"
            "Tous nos prix sont affichés sous chaque plat sur la page **« Menu »**.\n"
            "Nous proposons un excellent rapport qualité-prix afin d'offrir des repas généreux, chauds et accessibles à tous !"
        )

    if any(k in clean for k in ["vegetarien", "sans viande", "legume uniquement", "vegan", "vegetal"]):
        return (
            "🥗 **Options végétariennes :**\n\n"
            "Nous disposons d'options sans viande et d'accompagnements riches en légumes, riz et bananes plantains frites. "
            "Vous pouvez vérifier la composition de chaque assiette en consultant sa description sur le Menu."
        )

    if any(k in clean for k in ["allergie", "allergie alimentaire", "arachide", "gluten", "lactose", "halal", "sans sel", "regime"]):
        return (
            "⚠️ **Allergies & Régimes spécifiques :**\n\n"
            "Votre santé est notre priorité. Si vous êtes allergique à un aliment (arachides, œufs, produits laitiers) ou si vous suivez un régime sans sel :\n"
            "👉 Précisez-le impérativement dans les **« Notes pour la cuisine »** au moment du paiement, ou contactez notre équipe par téléphone !"
        )

    if any(k in clean for k in ["fraicheur", "frais", "qualite", "ingredients", "hygiene", "proprete", "origine"]):
        return (
            "🥗 **Engagement Fraîcheur & Hygiène :**\n\n"
            "Chez **Wa-Ngoie Food**, nous respectons des standards de qualité rigoureux :\n"
            "• Sélection quotidienne d'ingrédients frais et d'excellente qualité\n"
            "• Respect strict des normes d'hygiène en cuisine\n"
            "• Préparation à la commande pour garantir une chaleur et un goût irréprochables !"
        )

    if any(k in clean for k in ["portion", "taille", "grand", "moyen", "quantite plat", "copieux"]):
        return (
            "🍽️ **Taille et générosité des portions :**\n\n"
            "Nos portions sont pensées pour être généreuses et rassasiantes ! "
            "Les détails des accompagnements inclus sont précisés dans la fiche descriptive de chaque plat."
        )

    # -----------------------------------------------------------------
    # PRIORITÉ 4 : PANIER, PROCESSUS DE COMMANDE & PAIEMENT
    # -----------------------------------------------------------------
    if any(k in clean for k in ["ajouter au panier", "mettre dans le panier", "comment ajouter", "ajoute mon plat"]):
        return (
            "🛒 **Ajouter un article à votre panier :**\n\n"
            "1️⃣ Sur la page du **Menu**, choisissez un plat ou une boisson.\n"
            "2️⃣ Cliquez sur le bouton **« Ajouter au panier »**.\n"
            "3️⃣ L'icône de votre panier (en haut à droite) affichera immédiatement le nombre d'articles ajoutés."
        )

    if any(k in clean for k in ["vider le panier", "supprimer du panier", "enlever du panier", "retirer du panier", "modifier panier", "changer quantite"]):
        return (
            "🛒 **Gérer et ajuster votre panier :**\n\n"
            "Ouvrez votre panier en cliquant sur l'icône en haut à droite :\n"
            "• **Ajuster les quantités :** Utilisez les boutons **(+)** et **(-)**.\n"
            "• **Retirer un article :** Cliquez sur l'icône de corbeille (🗑️).\n"
            "• **Vider le panier :** Supprimez vos articles avant de changer de sélection."
        )

    if any(k in clean for k in ["panier", "mon panier", "caddie", "voir le panier"]):
        return (
            "🛒 **Votre Panier Wa-Ngoie Food :**\n\n"
            "Votre panier centralise votre sélection en cours. Vous pouvez y accéder à tout moment "
            "via l'icône en haut à droite pour vérifier votre total avant de valider."
        )

    if any(k in clean for k in ["passer commande", "passer une commande", "comment commander", "commander un plat", "commander en ligne", "valider mon panier", "passer a la caisse"]):
        return (
            "📦 **Passer votre commande étape par étape :**\n\n"
            "1️⃣ Ajoutez vos plats et boissons au **Panier**.\n"
            "2️⃣ Ouvrez le panier et cliquez sur **« Passer à la caisse »**.\n"
            "3️⃣ Indiquez ou vérifiez votre **adresse exacte de livraison**.\n"
            "4️⃣ Choisissez votre mode de paiement et cliquez sur **« Confirmer la commande »**.\n\n"
            "🔥 Votre commande est alors envoyée directement en cuisine !"
        )

    if any(k in clean for k in ["adresse de livraison", "maison", "bureau", "changer adresse livraison", "ou livrer"]):
        return (
            "📍 **Indiquer votre adresse de livraison :**\n\n"
            "Lors de la validation de votre panier, un champ dédié vous permet d'écrire votre adresse complète "
            "(commune, quartier, avenue et point de référence) afin de guider le livreur avec précision."
        )

    if any(k in clean for k in ["moyen de paiement", "comment payer", "paiement", "payer", "mobile money", "m-pesa", "mpesa", "orange money", "airtel money", "espece", "cash", "argent"]):
        return (
            "💳 **Modes de paiement acceptés :**\n\n"
            "Sur **Wa-Ngoie Food**, nous facilitons vos règlements :\n"
            "• **Paiement à la livraison (Espèces) :** Payez directement le livreur à réception de vos plats\n"
            "• **Mobile Money :** (M-Pesa, Orange Money, Airtel Money) selon la disponibilité indiquée à la caisse.\n\n"
            "🛡️ Toutes nos transactions font l'objet de l'émission d'un reçu officiel."
        )

    if any(k in clean for k in ["securite paiement", "fiable", "arnaque", "securise", "confiance"]):
        return (
            "🔒 **Sécurité et Confiance :**\n\n"
            "Votre sécurité est totale sur **Wa-Ngoie Food**. "
            "En optant pour le paiement à la livraison, vous ne réglez vos achats que lorsque le livreur vous remet vos plats en mains propres !"
        )

    if any(k in clean for k in ["code promo", "reduction", "coupon", "remise", "solde"]):
        return (
            "🎟️ **Codes promotionnels & Réductions :**\n\n"
            "Si vous disposez d'un code promotionnel, saisissez-le dans le champ dédié **« Code Promo »** "
            "sur la page de paiement pour bénéficier instantanément de votre remise sur le total de la commande !"
        )

    if any(k in clean for k in ["pourboire", "gratification livreur", "donner un pourboire"]):
        return (
            "🛵 **Pourboire pour le livreur :**\n\n"
            "Si vous appréciez la rapidité et la courtoisie de votre livreur, vous êtes libre de lui remettre "
            "une gratification en espèces lors de la livraison de votre commande. C'est toujours très apprécié !"
        )

    # -----------------------------------------------------------------
    # PRIORITÉ 5 : LIVRAISON, SUIVI & SERVICE APRÈS-VENTE (SAV)
    # -----------------------------------------------------------------
    if any(k in clean for k in ["suivre", "suivi", "ou est ma commande", "statut de ma commande", "ma commande est ou", "quand arrive ma commande", "temps d attente", "duree livraison", "delai livraison"]):
        return (
            "🚚 **Suivre votre livraison en temps réel :**\n\n"
            "Rendez-vous dans votre espace client, rubrique **« Mes Commandes »**.\n"
            "Vous pourrez suivre le statut en direct :\n"
            "• ⏳ **En attente :** Notre équipe examine votre commande\n"
            "• 🍳 **En préparation :** Notre cuisine prépare vos plats chauds\n"
            "• 🛵 **En livraison :** Le livreur est en chemin vers votre adresse !"
        )

    if any(k in clean for k in ["livraison", "livrer", "zone de livraison", "vous livrez ou", "kintambo", "kinshasa", "frais de livraison", "secteur"]):
        return (
            "🛵 **Zones desservies & Délais de livraison :**\n\n"
            "Notre restaurant **Wa-Ngoie Food** est situé dans la commune de **Kintambo** (Kinshasa) :\n"
            "• Nous livrons rapidement à **Kintambo** et dans les communes adjacentes\n"
            "• Le délai moyen de préparation et de transport est estimé entre **30 et 45 minutes**\n"
            "• Les éventuels frais de transport sont indiqués avant la validation finale de votre panier."
        )

    if any(k in clean for k in ["retard", "livraison en retard", "trop long", "j attends toujours"]):
        return (
            "⏳ **Votre livraison prend du retard ?**\n\n"
            "Les conditions de circulation à Kinshasa peuvent parfois ralentir nos livreurs.\n"
            "Veuillez nous appeler directement au numéro de notre page **« Contact »** en mentionnant votre **numéro de commande** "
            "afin que nous contactions le livreur sur-le-champ pour vous informer !"
        )

    if any(k in clean for k in ["commande incomplete", "il manque un plat", "plat endommage", "erreur commande", "mauvais plat", "froid"]):
        return (
            "⚠️ **Un souci avec votre livraison ?**\n\n"
            "Si vous constatez un article manquant ou un problème à l'arrivée de votre commande :\n"
            "1️⃣ Signalez-le immédiatement au livreur sur place\n"
            "2️⃣ Appelez notre support client via la page **« Contact »** muni de votre numéro de reçu.\n"
            "Nous interviendrons rapidement pour trouver une solution satisfaisante et corriger l'incident !"
        )

    if any(k in clean for k in ["annuler ma commande", "modifier ma commande", "je me suis trompe", "annuler commande"]):
        return (
            "⚠️ **Annuler ou modifier une commande passée :**\n\n"
            "Si votre commande est encore au statut **« En attente »** :\n"
            "Appelez notre restaurant **immédiatement** via le numéro de la page **« Contact »**.\n\n"
            "❌ *Important :* Dès que la cuisine a commencé la préparation (statut **« En préparation »**), "
            "la commande ne peut plus être annulée ni modifiée."
        )

    if any(k in clean for k in ["changer adresse livraison en cours", "mauvaise adresse", "je me suis trompe d adresse"]):
        return (
            "📍 **Modification d'adresse en cours de livraison :**\n\n"
            "Si vous avez fait une erreur dans votre adresse, téléphonez de toute urgence à notre service client "
            "via la page **« Contact »** afin que nous puissions rediriger notre livreur avant son arrivée."
        )

    if any(k in clean for k in ["recu", "reçu", "facture", "pdf", "telecharger recu", "télécharger reçu", "imprimer recu", "justificatif"]):
        return (
            "📄 **Télécharger votre Reçu PDF officiel :**\n\n"
            "Dès que votre commande est validée par le restaurant, une facture au format PDF est générée automatiquement :\n"
            "1️⃣ Allez dans la rubrique **« Mes Commandes »**.\n"
            "2️⃣ Cliquez sur la commande concernée.\n"
            "3️⃣ Cliquez sur **« Télécharger le reçu (PDF) »**.\n\n"
            "Ce document sert de justificatif officiel de votre transaction."
        )

    if any(k in clean for k in ["remboursement", "rembourser", "reclamation", "litige"]):
        return (
            "🛡️ **Réclamations & Solution commerciale :**\n\n"
            "Notre engagement est votre entière satisfaction. En cas de réclamation justifiée sur une commande, "
            "contactez notre administration par email ou téléphone via la rubrique **« Contact »** pour un examen rapide de votre demande."
        )

    # -----------------------------------------------------------------
    # PRIORITÉ 6 : INFOS PRATIQUES, HORAIRES, ÉVÉNEMENTS & FAQ
    # -----------------------------------------------------------------
    if any(k in clean for k in ["horaire", "horaires", "heure d ouverture", "vous ouvrez a quelle heure", "ouvert", "ferme", "quand êtes vous ouvert", "jours d ouverture"]):
        return (
            "⏰ **Horaires d'ouverture de Wa-Ngoie Food :**\n\n"
            "Nous sommes à votre service pour vos repas et livraisons :\n"
            "• **Du Lundi au Samedi :** De 09h00 à 22h00\n"
            "• **Le Dimanche :** De 11h00 à 22h00\n\n"
            "🔥 Commandez en ligne à tout moment pendant nos heures d'ouverture !"
        )

    if any(k in clean for k in ["adresse", "localisation", "vous etes ou", "ou se trouve le restaurant", "kintambo", "situé ou", "situe ou", "plan d acces", "venir manger"]):
        return (
            "📍 **Où nous trouver ?**\n\n"
            "Le restaurant **Wa-Ngoie Food** est idéalement situé dans la commune de **Kintambo**, dans la ville de **Kinshasa** (RDC).\n\n"
            "Rendez-vous sur la page **« Contact »** pour consulter nos coordonnées exactes et visualiser notre plan d'accès."
        )

    if any(k in clean for k in ["contact", "contacter", "numero", "numéro", "telephone", "téléphone", "appeler", "whatsapp", "email", "joindre", "aide", "assistance", "probleme"]):
        return (
            "📞 **Contacter le Service Client Wa-Ngoie Food :**\n\n"
            "Pour toute question ou demande d'assistance :\n"
            "• Visitez notre page **« Contact »** pour accéder à notre numéro de téléphone direct et notre adresse électronique.\n"
            "• Gardez votre numéro de commande à portée de main lors de votre appel pour accélérer le traitement de votre demande."
        )

    if any(k in clean for k in ["evenement", "événement", "fete", "anniversaire", "traiteur", "grosse commande", "plusieurs plats", "reunion", "groupe"]):
        return (
            "🎉 **Service Traiteur & Commandes de groupe :**\n\n"
            "Vous organisez une réception, un anniversaire ou une réunion professionnelle à Kinshasa ?\n"
            "**Wa-Ngoie Food** peut gérer vos commandes en gros volumes ! Contactez notre direction à l'avance via la page **« Contact »** pour obtenir un devis sur mesure."
        )

    if any(k in clean for k in ["reservation", "reserver une table", "manger sur place", "table"]):
        return (
            "🪑 **Consommation sur place :**\n\n"
            "Notre établissement de Kintambo accueille également les clients qui souhaitent manger sur place. "
            "Vous pouvez venir directement pendant nos horaires d'ouverture ou commander à l'avance !"
        )

    if any(k in clean for k in ["emballage", "ecologie", "box", "boite", "couvert", "serviette"]):
        return (
            "🍱 **Emballages et Ustensiles :**\n\n"
            "Chacune de nos commandes est soigneusement conditionnée dans des emballages thermiques et hygiéniques "
            "pour conserver la chaleur de vos repas. Des serviettes et ustensiles de table sont inclus sur simple demande !"
        )

    if any(k in clean for k in ["recrutement", "emploi", "travail", "embauche", "stage", "postuler", "travailler chez vous"]):
        return (
            "💼 **Emploi & Candidatures :**\n\n"
            "Vous souhaitez rejoindre l'équipe de Wa-Ngoie Food en cuisine, au service ou à la livraison ?\n"
            "Envoyez votre candidature et votre curriculum vitae à notre direction par email via les coordonnées de la page **« Contact »**."
        )

    if any(k in clean for k in ["comment ca marche", "comment utiliser", "guide", "aide moi", "comment faire", "mode d emploi"]):
        return (
            "🧭 **Guide d'utilisation de la plateforme Wa-Ngoie Food :**\n\n"
            "1️⃣ **Explorez :** Visitez l'onglet *Menu* pour découvrir nos spécialités\n"
            "2️⃣ **Sélectionnez :** Ajoutez vos plats préférés au *Panier*\n"
            "3️⃣ **Commandez :** Renseignez votre adresse à Kintambo/Kinshasa et validez\n"
            "4️⃣ **Suivez :** Suivez la préparation en temps réel depuis *Mes Commandes*\n"
            "5️⃣ **Justifiez :** Téléchargez votre reçu PDF officiel dès validation !"
        )

    # -----------------------------------------------------------------
    # SALUTATIONS & REMERCIEMENTS
    # -----------------------------------------------------------------
    if any(k in clean for k in ["merci", "je te remercie", "super", "genial", "parfait", "bravo"]):
        return (
            "😊 Tout le plaisir est pour moi ! N'hésitez pas si vous avez d'autres questions. "
            "Toute l'équipe de **Wa-Ngoie Food** vous souhaite un excellent appétit !"
        )

    greetings = ["bonjour", "salut", "hello", "bonsoir", "hey", "bjr", "coucou", "yo"]
    if any(clean.startswith(g) or f" {g}" in f" {clean}" for g in greetings):
        if is_abm:
            return "Salut Manassé ! 🔥 Prêt à faire rayonner Wa-Ngoie Food aujourd'hui ?"
        return (
            "Bonjour ! 👋 Ravi de vous accueillir sur Wa-Ngoie Food.\n\n"
            "Posez-moi votre question (par exemple : « Comment voir le menu ? » ou « Comment suivre une commande ? »), je suis à votre disposition !"
        )

    # -----------------------------------------------------------------
    # REPONSE PAR DEFAUT INTELLIGENTE (FALLBACK SÉCURISÉ)
    # -----------------------------------------------------------------
    if is_admin_user:
        return (
            "🤖 Je n'ai pas trouvé de réponse exacte à votre requête administrative.\n\n"
            "Pour obtenir la bonne information, essayez des formulations simples comme :\n"
            "• *« Comment ajouter un produit ? »*\n"
            "• *« Comment valider une commande ? »*\n"
            "• *« Où consulter les statistiques de vente ? »*\n"
            "• *« Comment gérer les utilisateurs ? »*"
        )

    return (
        "🤖 Je ne suis pas certain d'avoir bien compris votre question.\n\n"
        "Je suis un assistant intelligent formé pour vous accompagner sur Wa-Ngoie Food. Vous pouvez me demander :\n"
        "• *« Comment voir le menu ? »*\n"
        "• *« Comment passer une commande ? »*\n"
        "• *« Comment télécharger mon reçu PDF ? »*\n"
        "• *« Qui t'a créé ? »*\n\n"
        "Reformulez votre question simplement et je me ferai un plaisir de vous renseigner !"
    )


# =====================================================================
# 3. ROUTES FLASK DE L'ASSISTANT ABM AI
# =====================================================================

@ai_bp.route('/ai')
def query():
    """
    Rend la page de chat principale (interface client) de l'assistant ABM AI.
    """
    return render_template('ai/query.html')


@ai_bp.route('/ai/message', methods=['POST'])
def message():
    """
    Endpoint POST pour le dialogue AJAX avec ABM AI.
    - Analyse le texte envoyé via `request.form`
    - Applique un filtre de sécurité sur la longueur (max 2000 caractères)
    - Appelle le moteur local `generate_response()`
    - Renvoie une réponse `text/plain; charset=utf-8` PURE afin d'éviter
      les problèmes de conversion d'apostrophes (ex: &#x27;) côté JavaScript.
    """
    raw = request.form.get('message', '').strip()

    # Protection contre les messages anormalement longs (anti-spam)
    if len(raw) > 2000:
        raw = raw[:2000]

    # Détection propre du contexte et du compte utilisateur
    user = current_user if current_user.is_authenticated else None

    try:
        reply = generate_response(raw, user)
    except Exception:
        # Fallback de sécurité : on ne divulgue jamais d'erreur système au client
        reply = (
            "Une brève erreur technique est survenue lors du traitement de votre message.\n\n"
            "Veuillez reformuler votre question ou réessayer dans quelques secondes."
        )

    # Réponse en texte brut en UTF-8 pour un rendu propre dans l'interface chat
    response = make_response(reply)
    response.mimetype = "text/plain"
    response.charset = "utf-8"

    return response