
import numpy as np
import streamlit as st
import joblib
import pandas as pd
import statsmodels.api as sm

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Burn-out au travail", page_icon="🧠", layout="centered")

# --- TITRE ---
st.title("Application d’évaluation du risque de burn-out au travail 🧠")

# --- INTRODUCTION ---
st.markdown("""
Bienvenue dans cette application interactive conçue pour **évaluer votre risque de burn-out professionnel** à partir de données issues de l’enquête nationale **Conditions de travail et Risques psychosociaux (CT-RPS) 2016**.

L’évaluation repose sur un **modèle statistique rigoureux** construit à partir des réponses de plus de 9000 actifs, combinant :
- Les **dimensions du burn-out** selon le **Maslach Burnout Inventory (MBI)**,
- Des **facteurs personnels et professionnels** (âge, sexe, diplôme, emploi, etc.),
- Des **variables liées au travail** (tensions, soutien, autonomie, etc.).

---
### Que fait cette application ?
- Calcule un **score de burn-out** basé sur vos réponses ;
- Estime la **probabilité d’être en situation de burn-out sévère** ;
- Fournit des **conseils personnalisés** en fonction de votre profil.

---
### À lire avant de commencer

Cette application a une **visée informative et préventive**.  
Elle **ne remplace pas un diagnostic médical**. En cas de mal-être ou de souffrance au travail, consultez un professionnel de santé ou un service de prévention.
""")

# --- DÉMARRAGE DU QUESTIONNAIRE ---
st.markdown("""
---

### Comment ça marche ?

Nous allons vous poser une série de **questions simples** sur :

- **Votre ressenti au travail** (épuisement, motivation, pression…)  
- **Vos relations professionnelles** (soutien, conflits, reconnaissance…)  
- **Vos conditions de travail** (horaires, autonomie, clarté des attentes…)  
- **Votre situation personnelle** (âge, sexe, diplôme, type d’emploi…)

Il vous suffit de **répondre le plus honnêtement possible** en cochant les réponses qui correspondent à votre vécu **au cours des dernières semaines**.

---
""")

# --- DÉBUT DU FORMULAIRE ---
st.subheader("🧾 Questionnaire")

st.markdown("---")
st.subheader("📌 Informations personnelles et emploi")
# puis les questions : âge, sexe, diplôme, type d'emploi, revenu

## AGE ##
age = st.slider("Quel est votre âge ?", min_value=18, max_value=64, value=30)

if age < 24:
    st.warning("⚠️ Attention : notre modèle a été entraîné uniquement sur des individus âgés de 24 à 64 ans. La prédiction peut être moins fiable.")

## IDENTITÉ DE GENRE ##
st.markdown("### Identité de genre")

genre_selectionne = st.selectbox(
    "Quel est votre genre ?",
    options=["Femme", "Homme", "Autre/Ne souhaite pas répondre"]
)
show_prediction = False
genre_autre = False

# Traitement du genre
if genre_selectionne == "Femme":
    sexe = 1
    show_prediction = True
elif genre_selectionne == "Homme":
    sexe = 0
    show_prediction = True
elif genre_selectionne == "Autre/Ne souhaite pas répondre":
    sexe = np.nan
    show_prediction = False
    genre_autre = True  # ➜ on active ce drapeau
    st.warning("ℹ️ Votre profil ne peut pas être évalué par le modèle actuel. Vous trouverez néanmoins ci-dessous des conseils utiles.")
    st.subheader("🧠 Conseils personnalisés (sans estimation)")
    st.markdown("""
Bien que nous ne puissions pas vous donner de score personnalisé dans ce cas, voici **des conseils utiles** si vous ressentez une charge mentale importante ou des signes d'épuisement :

- **Écoutez vos signaux d’alerte** : troubles du sommeil, fatigue, irritabilité, perte d’envie ou de concentration sont des indicateurs importants.
- **Parlez-en à un·e professionnel·le de santé** si vous avez un doute ou ressentez un mal-être.
- **N'attendez pas que la situation s'aggrave** : il est possible de prévenir le burn-out par des ajustements simples dans l'organisation, la charge ou le soutien au travail.
- **Entourez-vous de personnes de confiance**, au travail ou en dehors, et ne restez pas seul·e.
- **Consultez votre médecin du travail** si besoin : il peut vous aider à adapter vos conditions de travail.
""")

st.markdown("---")

if not genre_autre:
    ##DIPLOME##
    # # Question sur le diplôme
    diplome = st.selectbox(
    "Quel est votre niveau de diplôme le plus élevé obtenu ?",
    options=[
        "Aucun diplôme ou primaire",
        "CAP / BEP / Bac",
        "Bac +2 (BTS, DUT, etc.)",
        "Bac +3 ou plus (Licence, Master...)"
    ]
    )
    diplome_dict = {
        "Aucun diplôme ou primaire": 0,
        "CAP / BEP / Bac": 1,
        "Bac +2 (BTS, DUT, etc.)": 2,
        "Bac +3 ou plus (Licence, Master...)": 3
    }

    niv_diplome_reg = diplome_dict[diplome]

    ##TYPEMPLOI##
    type_emploi = st.selectbox(
        "Quel est votre type d'emploi actuel ?",
        [
            "1 - Fonctionnaire titulaire",
            "2 - Fonctionnaire non titulaire",
            "3 - Salarié permanent CDI",
            "4 - Salarié temporaire ou CDD",
            "5 - Intérimaire",
            "6 - Indépendant / à son compte",
            "7 - Aide familiale"
        ]
    )
    TYPEMPLOI = int(type_emploi.split(" - ")[0])



    ##revmensc_tranche##
    # Question sur le revenu mensuel
    revenu = st.selectbox(
        "Quel est votre revenu mensuel net moyen (en €) ?",
        options=[
            "Je préfère ne pas répondre",
            "≤ 1350",
            "1351–1700",
            "1701–2250",
            "2251–3000",
            "> 3000"
        ]
    )
    revmensc_dummies = {
        "revmensc_tranche_1351–1700": 0,
        "revmensc_tranche_1701–2250": 0,
        "revmensc_tranche_2251–3000": 0,
        "revmensc_tranche_> 3000": 0
    }

    if revenu == "Je préfère ne pas répondre":
        st.warning("Vous avez choisi de ne pas répondre à cette question. La prédiction pourrait être légèrement moins précise.")
    elif revenu != "≤ 1350":
        revmensc_dummies[f"revmensc_tranche_{revenu}"] = 1

    st.markdown("---")

    st.subheader("⏰ Conditions de travail")
    # horaires, prévisibilité, initiatives, autonomie...

    ##ÉQUILIBRE VIE PROFESSIONNELLE / PERSONNELLE##
    cvfvp = st.radio(
        "Comment jugez-vous votre équilibre entre vie professionnelle et vie personnelle ?",
        options=[
            "Très bien",
            "Bien",
            "Pas très bien",
            "Pas bien du tout",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )

    if cvfvp in ["Très bien", "Bien"]:
        CVFVP_reg = 1
    elif cvfvp in ["Pas très bien", "Pas bien du tout"]:
        CVFVP_reg = 0
    else:
        CVFVP_reg = np.nan

    ##PRÉVISIBILITÉ DES HORAIRES##
    previs = st.radio(
        "À quel moment êtes-vous informé·e de vos horaires de travail ?",
        options=[
            "Au moins un mois à l’avance",
            "Au moins une semaine à l’avance",
            "La veille",
            "Le jour même ou pas du tout",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )

    previs_dict = {
        "Au moins un mois à l’avance": 1,
        "Au moins une semaine à l’avance": 2,
        "La veille": 3,
        "Le jour même ou pas du tout": 4
    }

    PREVIS = previs_dict.get(previs, np.nan)


    ##INITIATIVES AU TRAVAIL##
    initiat = st.radio(
        "Votre travail nécessite-t-il que vous preniez des initiatives ?",
        options=[
            "Toujours",
            "Souvent",
            "Parfois",
            "Jamais",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )

    # Recodage INITIAT_reg (1 à 4 conservés, 8/9 → np.nan)
    initiat_dict = {
        "Toujours": 1,
        "Souvent": 2,
        "Parfois": 3,
        "Jamais": 4,
        "Je ne sais pas / Je préfère ne pas répondre": np.nan
    }

    INITIAT_reg = initiat_dict[initiat]

    ##POSSIBILITÉ DE METTRE EN PRATIQUE SES PROPRES IDÉES##
    idee = st.radio(
        "Avez-vous la possibilité de mettre vos propres idées en pratique dans votre travail ?",
        options=[
            "Toujours",
            "Souvent",
            "Parfois",
            "Jamais",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )

    # Recodage IDEE_reg
    if idee in ["Toujours", "Souvent"]:
        IDEE_reg = 1
    elif idee in ["Parfois", "Jamais"]:
        IDEE_reg = 0
    else:
        IDEE_reg = np.nan

    ##INTERVENTION SUR LA QUANTITÉ DE TRAVAIL##
    quanti = st.radio(
        "Pouvez-vous intervenir sur la quantité de travail qui vous est attribuée ?",
        options=[
            "Toujours",
            "Souvent",
            "Parfois",
            "Jamais",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )
    if quanti in ["Toujours", "Souvent"]:
        QUANTI_reg = 1
    elif quanti in ["Parfois", "Jamais"]:
        QUANTI_reg = 0
    else:
        QUANTI_reg = np.nan

    ##BIENETR1##
    bienetr1 = st.radio(
        "Comment évaluez-vous votre bien-être global ces dernières semaines ?",
        ["Plutôt bien", "Plutôt mal", "Je ne sais pas / Je préfère ne pas répondre"]
    )
    if bienetr1 == "Plutôt bien":
        BIENETR1_reg = 1
    elif bienetr1 == "Plutôt mal":
        BIENETR1_reg = 0
    else:
        BIENETR1_reg = np.nan


    st.markdown("---")

    st.subheader("🤝 Relations professionnelles")
    # soutien, tensions, aide, conflits...

    # --- TENSIONS AVEC LA HIÉRARCHIE ---
    tension2 = st.radio(
        "Vivez-vous des situations de tension dans vos rapports avec vos supérieurs hiérarchiques (suffisamment fréquentes pour perturber votre travail) ?",
        options=[
            "Oui",
            "Non",
            "Sans objet (pas de supérieur hiérarchique)",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )

    if tension2 == "Oui":
        TENSION2_reg = 1
    elif tension2 == "Non":
        TENSION2_reg = 0
    else:
        TENSION2_reg = np.nan

    ##SOUTIEN SOCIAL RP1##
    rp1 = st.radio(
        "Y a-t-il quelqu’un sur qui vous pouvez compter pour discuter de choses personnelles ou pour prendre une décision difficile ?",
        options=[
            "Oui",
            "Non",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )

    if rp1 == "Oui":
        RP1_reg = 1
    elif rp1 == "Non":
        RP1_reg = 0
    else:
        RP1_reg = np.nan


    ##DÉSACCORD AVEC LE SUPÉRIEUR SUR LA FAÇON DE TRAVAILLER##
    acchef = st.radio(
        "Vous arrive-t-il d’être en désaccord avec vos supérieurs sur la façon de bien faire votre travail ?",
        options=[
            "Toujours",
            "Souvent",
            "Parfois",
            "Jamais",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )
    acchef_dict = {
        "Toujours": 3,
        "Souvent": 2,
        "Parfois": 1,
        "Jamais": 0,
        "Je ne sais pas / Je préfère ne pas répondre": np.nan
    }

    ACCHEF_reg = acchef_dict[acchef]

    ##AIDE DES COLLÈGUES EN CAS DE DIFFICULTÉ##
    aidcoll = st.radio(
        "Si vous avez du mal à faire un travail délicat ou compliqué, êtes-vous aidé·e par les personnes avec qui vous travaillez habituellement ?",
        options=[
            "Oui",
            "Non",
            "Sans objet / Je ne sais pas / Je préfère ne pas répondre"
        ]
    )
    if aidcoll == "Oui":
        AIDCOLL_reg = 1
    elif aidcoll == "Non":
        AIDCOLL_reg = 0
    else:
        AIDCOLL_reg = np.nan

    ##CONFIANCE DANS LES INFORMATIONS DU SUPÉRIEUR##
    infoconf = st.radio(
        "Pouvez-vous faire confiance aux informations qui viennent de vos supérieurs ou responsables ?",
        options=[
            "Toujours",
            "Souvent",
            "Parfois",
            "Jamais",
            "Sans objet / Je ne sais pas / Je préfère ne pas répondre"
        ]
    )
    infoconf_dict = {
        "Toujours": 3,
        "Souvent": 2,
        "Parfois": 1,
        "Jamais": 0,
        "Sans objet / Je ne sais pas / Je préfère ne pas répondre": np.nan
    }

    INFOCONF_reg = infoconf_dict[infoconf]

    st.markdown("---")

    st.subheader("⚠️ Événements de vie marquants")

    ##ÉVÉNEMENT MARQUANT - SANTÉ / DÉCÈS D’UN PROCHE##
    rp4b = st.radio(
        "Au cours des trois dernières années, un événement vous a-t-il marqué, comme de graves problèmes de santé d’un proche ou le décès d’un parent (père, mère, autre) ?",
        options=[
            "Oui",
            "Non",
            "Je ne sais pas / Je préfère ne pas répondre"
        ]
    )
    if rp4b == "Oui":
        RP4B_reg = 1
    elif rp4b == "Non":
        RP4B_reg = 0
    else:
        RP4B_reg = np.nan

    st.markdown("---")

    st.subheader("📲 Intrusion du travail dans la vie privée")

    ##CONTACT EN DEHORS DU TEMPS DE TRAVAIL PAR DES PERSONNES EXTÉRIEURES##
    joinext = st.radio(
        "Au cours des douze derniers mois, avez-vous été contacté·e en dehors de vos horaires de travail par des personnes extérieures à l’entreprise pour les besoins du travail ?",
        options=[
            "Oui",
            "Non",
            "Sans objet / Je travaille seul·e / Je ne sais pas / Je préfère ne pas répondre"
        ]
    )
    if joinext == "Oui":
        JOINEXT_reg = 1
    elif joinext == "Non":
        JOINEXT_reg = 0
    else:
        JOINEXT_reg = np.nan


    st.markdown("---")

    st.subheader("📉 Ressenti au travail")
    # ennui, tâches inutiles, moqueries...

    ##COMPORTEMENT HOSTILE : TÂCHES INUTILES##
    rpb1e = st.radio(
        "Au travail, vous arrive-t-il d’être chargé·e de tâches inutiles ou dégradantes ?",
        options=["Oui", "Non", "Je ne sais pas / Je préfère ne pas répondre"]
    )
    RPB1E_b = 1 if rpb1e == "Oui" else 0 if rpb1e == "Non" else np.nan

    ##COMPORTEMENT HOSTILE : EMPÊCHÉ DE S'EXPRIMER##
    rpb1h = st.radio(
        "Vous est-il déjà arrivé d’être empêché·e de vous exprimer dans votre travail ?",
        options=["Oui", "Non", "Je ne sais pas / Je préfère ne pas répondre"]
    )
    RPB1H_b = 1 if rpb1h == "Oui" else 0 if rpb1h == "Non" else np.nan

    ##COMPORTEMENT HOSTILE : MOQUERIES OU BLAGUES BLESSANTES##
    rpb1j = st.radio(
        "Avez-vous subi des moqueries ou blagues blessantes dans votre environnement de travail ?",
        options=["Oui", "Non", "Je ne sais pas / Je préfère ne pas répondre"]
    )
    RPB1J_b = 1 if rpb1j == "Oui" else 0 if rpb1j == "Non" else np.nan

    ##RESSENTI : ENNUI DANS LE TRAVAIL##
    rpb5e = st.radio(
        "Dans votre travail, ressentez-vous souvent de l’ennui ?",
        options=["Toujours", "Souvent", "Parfois", "Jamais", "Je ne sais pas / Je préfère ne pas répondre"]
    )
    if rpb5e in ["Toujours", "Souvent"]:
        RPB5E_b = 1
    elif rpb5e in ["Parfois", "Jamais"]:
        RPB5E_b = 0
    else:
        RPB5E_b = np.nan

    # Coefficients estimés du modèle logit1
    coefficients = {
        "const": -3.3687,
        "TENSION2_reg": 0.6319,
        "INITIAT_reg": 0.5121,
        "JOINEXT_reg": 0.6286,
        "RPB5E_b": 0.7328,
        "RPB1J_b": 0.7206,
        "ACCHEF_reg": 0.2619,
        "RP4B_reg": 0.3798,
        "sexe": 0.7848,
        "RPB1E_b": 0.8432,
        "CVFVP_reg": -0.7198,
        "RP1_reg": -0.6660,
        "BIENETR1_reg": -0.4299,
        "niv_diplome_reg": 0.1484,
        "IDEE_reg": -0.2672,
        "QUANTI_reg": -0.2745,
        "AIDCOLL_reg": -0.2803,
        "INFOCONF_reg": -0.1177,
        "revmensc_tranche_> 3000": -0.4194,
        "PREVIS": 0.1115,
        "TYPEMPLOI": 0.2261,
        "revmensc_tranche_2251–3000": -0.1733,
        "revmensc_tranche_1351–1700": -0.0993,
        "revmensc_tranche_1701–2250": -0.0826,
        "AGE": 0.0022
    }


    # Construction du DataFrame utilisateur pour la prédiction
    X_input = pd.DataFrame([{
        "sexe": sexe,
        "AGE": age,
        "CVFVP_reg": CVFVP_reg,
        "BIENETR1_reg": BIENETR1_reg,
        "RP1_reg": RP1_reg,
        "RP4B_reg": RP4B_reg,
        "RPB1E_b": RPB1E_b,
        "RPB1J_b": RPB1J_b,
        "RPB5E_b": RPB5E_b,
        "AIDCOLL_reg": AIDCOLL_reg,
        "JOINEXT_reg": JOINEXT_reg,
        "INFOCONF_reg": INFOCONF_reg,
        "ACCHEF_reg": ACCHEF_reg,
        "niv_diplome_reg": niv_diplome_reg,
        "PREVIS": PREVIS,
        "INITIAT_reg": INITIAT_reg,
        "IDEE_reg": IDEE_reg,
        "QUANTI_reg": QUANTI_reg,
        "TENSION2_reg": TENSION2_reg,
        "TYPEMPLOI": TYPEMPLOI,
        "revmensc_tranche_1351–1700": revmensc_dummies["revmensc_tranche_1351–1700"],
        "revmensc_tranche_1701–2250": revmensc_dummies["revmensc_tranche_1701–2250"],
        "revmensc_tranche_2251–3000": revmensc_dummies["revmensc_tranche_2251–3000"],
        "revmensc_tranche_> 3000": revmensc_dummies["revmensc_tranche_> 3000"]
    }])

    if not show_prediction :
        st.info("🛈 Merci de compléter toutes les questions pour obtenir votre score.")
    elif X_input.isnull().any(axis=1).values[0]:
        # Dictionnaire pour afficher des noms lisibles
        var_to_label = {
            "CVFVP_reg": "Équilibre vie professionnelle / personnelle",
            "PREVIS": "Prévisibilité des horaires",
            "INITIAT_reg": "Nécessité de prendre des initiatives",
            "IDEE_reg": "Possibilité de mettre ses idées en pratique",
            "QUANTI_reg": "Intervenir sur la quantité de travail",
            "BIENETR1_reg": "Bien-être global",
            "RP1_reg": "Soutien social",
            "RP4B_reg": "Événement de vie marquant",
            "RPB1E_b": "Tâches inutiles ou dégradantes",
            "RPB1J_b": "Moqueries ou blagues blessantes",
            "RPB5E_b": "Ennui au travail",
            "JOINEXT_reg": "Contacts hors temps de travail",
            "INFOCONF_reg": "Confiance dans les informations",
            "ACCHEF_reg": "Désaccord avec le supérieur",
            "AIDCOLL_reg": "Aide des collègues",
            "TENSION2_reg": "Tensions avec la hiérarchie",
            "niv_diplome_reg": "Niveau de diplôme",
            "TYPEMPLOI": "Type d'emploi",
            "revmensc_tranche_1351–1700": "Revenu 1351–1700€",
            "revmensc_tranche_1701–2250": "Revenu 1701–2250€",
            "revmensc_tranche_2251–3000": "Revenu 2251–3000€",
            "revmensc_tranche_> 3000": "Revenu > 3000€",
            "sexe": "Genre",
            "AGE": "Âge"
        }
        missing_vars = X_input.columns[X_input.isnull().any()].tolist()
        missing_labels = [var_to_label.get(v, v) for v in missing_vars]
        st.warning(f"⚠️ Veuillez répondre à toutes les questions. Questions manquantes : {', '.join(missing_labels)}")
        else:
            if st.button("🧮 Calculer mon score de burn-out"):
            # --- Calcul de la probabilité ---
            X_input["const"] = 1  # Ajoute constante
            X_input = X_input[list(coefficients.keys())]  # Garde seulement les variables du modèle
            X_array = X_input.values[0]
            coef_array = np.array(list(coefficients.values()))
            log_odds = np.dot(X_array, coef_array)
            proba = 1 / (1 + np.exp(-log_odds))
            prediction = int(proba >= 0.2)

            # --- Résultat ---
            st.subheader("🧠 Résultat")
            st.metric("Probabilité estimée de burn-out sévère", f"{round(proba * 100, 1)} %")
            st.info(f"Selon vos réponses, votre risque estimé de burn-out sévère est de **{round(proba*100, 1)} %**.")
            st.progress(proba)

            # --- Conseils en fonction du niveau de risque ---
            if proba >= 0.4:
                st.warning("⚠️ Le risque de burn-out sévère détecté est très élevé.")
                st.markdown("""
        **Voici quelques conseils adaptés à votre situation :**
        - **Consultez rapidement un professionnel de santé** (médecin traitant, psychologue, psychiatre) pour faire le point sur votre état de santé.
        - **Envisagez un arrêt de travail temporaire** si vous êtes en situation d’épuisement avancé. Cela peut vous permettre de prendre du recul et de vous reposer.
        - **Prenez soin de vous** : veillez à votre sommeil, réduisez les surstimulations (notifications, écrans...), et accordez-vous des moments de récupération sans culpabilité.
        - **Ne restez pas isolé·e** : parlez à vos proches, à un collègue de confiance ou à votre médecin du travail. Vous pouvez aussi contacter des associations de soutien.
        - **Pensez à consulter votre médecin du travail** pour un éventuel aménagement de poste (réduction des horaires, baisse de charge, télétravail temporaire...).
        """)

            elif 0.2 <= proba < 0.4:
                st.info("⚠️ Un risque modéré de burn-out est détecté.")
                st.markdown("""
        **Quelques recommandations pour agir à temps :**
        - **Soyez attentif·ve aux signaux de fatigue** : troubles du sommeil, irritabilité, perte de motivation, etc.
        - **Essayez d’identifier les facteurs de stress** dans votre environnement de travail : surcharge, manque de reconnaissance, tensions relationnelles…
        - **Organisez vos priorités**, apprenez à dire non si besoin, et aménagez-vous des temps de déconnexion.
        - **Échangez avec votre supérieur·e ou RH** si certaines tâches vous semblent insoutenables ou mal comprises.
        - **Envisagez un accompagnement psychologique préventif** (psychologue, thérapeute, groupe de parole).
        """)

            else:
                st.success("✅ Aucun risque préoccupant de burn-out n'est détecté.")
                st.markdown("""
        **Vous semblez actuellement dans une situation stable. Bravo !**
        Voici quelques conseils pour **préserver votre équilibre** :
        - Maintenez des **temps de récupération réguliers** : pauses, congés, moments de détente.
        - **Entretenez vos relations sociales** au travail et en dehors : soutien et reconnaissance sont protecteurs.
        - Soyez à l’écoute de vous-même : en cas de changement d’humeur, fatigue persistante ou perte de sens, n’hésitez pas à consulter.
        - Continuez à **vous questionner sur le sens de votre travail**, et à ajuster vos objectifs personnels et professionnels.
        """)
    st.markdown("---")
    if st.button("🔄 Recommencer avec un nouveau profil"):
        st.experimental_rerun()

