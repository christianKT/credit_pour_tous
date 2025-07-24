import os
from flask import Flask, session, render_template, request, redirect, url_for, send_file
import joblib
import pandas as pd
import io
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Charger le modèle
model = joblib.load("model/lgbm_clf.pkl")

# Liste des questions destinées aux EMPLOYÉS pour analyser un dossier client
questions = [
    ("annual_inc", "Quel est le revenu annuel déclaré (€) ?", "Indiqué dans la demande client, brut annuel."),
    ("loan_amnt", "Quel est le montant du prêt demandé (€) ?", "Montant total sollicité par le client."),
    ("int_rate", "Quel est le taux d'intérêt appliqué (%) ?", "Ex. : 7.5"),
    ("dti", "Quel est le DTI (ratio dette/revenu %) du client ?", "Ex. : 35%"),
    ("revol_util", "Utilisation du crédit renouvelable (%) ?", "Niveau d'utilisation des lignes de crédit existantes."),
    ("credit_history_length", "Ancienneté de l'historique de crédit (années) ?", "Durée en années depuis la 1re ligne de crédit."),
    ("pub_rec", "Combien d'incidents publics déclarés ?", "Ex. : défauts, recouvrements, etc."),
    ("term", "Durée du prêt demandée ?", "Ex. : 36 ou 60 mois"),
    ("home_ownership", "Statut de logement du client ?", "Locataire, Propriétaire, Autre"),
    ("purpose", "Objet du prêt ?", "Motif indiqué dans la demande"),
    ("verification", "Revenu vérifié par justificatif ?", "Oui / Non"),
    ("installment", "Montant estimé de la mensualité (€) ?", "Simulation ou estimation du prêt.")
]

question_options = {
    "term": ["36", "60"],
    "home_ownership": ["Locataire", "Propriétaire (hypothèque)", "Autre"],
    "purpose": ["Voiture", "Petite entreprise", "Travaux", "Autre"],
    "verification": ["Oui", "Non"],
    "pub_rec": ["0", "1", "2", "3"]
}

@app.route("/", methods=["GET", "POST"])
def chat():
    if 'step' not in session:
        session['step'] = 0
        session['answers'] = {}
        session['history'] = []

    step = session['step']
    answers = session['answers']
    history = session['history']
    result = None
    proba = None
    reco = None
    error = None
    download_ready = False

    if request.method == "POST":
        key, label, _ = questions[step]
        user_input = request.form['response'].strip()
        options = question_options.get(key)

        # Convertir l'ancienneté de crédit en jours
        if key == "credit_history_length":
            try:
                user_input = str(int(float(user_input) * 365))
            except ValueError:
                error = "Veuillez entrer un nombre d'années valide."
                return render_template("chat.html", question=label, helper=questions[step][2], history=history, error=error, options=options)

        if options and user_input not in options:
            error = "Veuillez sélectionner une option valide."
            return render_template("chat.html", question=label, helper=questions[step][2], history=history, error=error, options=options)

        try:
            if not options:
                if key in ["annual_inc", "loan_amnt", "int_rate", "dti", "revol_util", "installment"]:
                    float(user_input)
                elif key == "credit_history_length":
                    int(user_input)
        except ValueError:
            error = "Entrée invalide. Merci de saisir une valeur numérique."
            return render_template("chat.html", question=label, helper=questions[step][2], history=history, error=error, options=None)

        answers[key] = user_input
        history.append((label, user_input))
        session['step'] = step + 1

        if session['step'] >= len(questions):
            input_data = {
                'int_rate': float(answers['int_rate']),
                'annual_inc': float(answers['annual_inc']),
                'revol_util': float(answers['revol_util']),
                'loan_amnt': float(answers['loan_amnt']),
                'dti': float(answers['dti']),
                'credit_history_length': int(answers['credit_history_length']),
                'installment': float(answers['installment']),
                'pub_rec': int(answers['pub_rec']),
                'term': 1 if answers['term'] == "60" else 0,
                'home_ownership_MORTGAGE': 1 if "hypoth" in answers['home_ownership'].lower() else 0,
                'purpose_small_business': 1 if "entreprise" in answers['purpose'].lower() else 0,
                'verification_status_Source Verified': 1 if answers['verification'].lower().startswith("oui") else 0
            }

            df = pd.DataFrame([input_data])
            prob = model.predict_proba(df)[0][1]
            proba = round(prob * 100, 1)

            if prob > 0.55:
                result = "🔴 Dossier à risque élevé"
                reco = "Ce profil client présente un risque de défaut important. Une validation manuelle est recommandée."
            elif prob > 0.30:
                result = "🟡 Dossier modéré"
                reco = "Le risque est acceptable mais des pièces complémentaires peuvent être exigées(Analyse complémentaire recommandée.)."
            else:
                result = "🟢 Dossier favorable"
                reco = "Le profil du client est conforme aux critères de validation."

            session['result'] = result
            session['proba'] = proba
            session['reco'] = reco
            download_ready = True
            session['download_ready'] = True
            return render_template("chat.html", history=history, result=result, proba=proba, message=reco, download_ready=True)

    if session.get('step') is not None and session['step'] < len(questions):
        key, current_question, helper = questions[session['step']]
        options = question_options.get(key)
    else:
        current_question, helper, options = None, None, None

    return render_template("chat.html", question=current_question, helper=helper, options=options, history=history, result=result, proba=proba, message=reco, error=error, download_ready=download_ready)

@app.route("/download")
def download_pdf():
    if not session.get('download_ready'):
        return "PDF non disponible."

    def latin1_safe(text):
        return text.encode("latin-1", "ignore").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Diagnostic de Solvabilité - Crédit Client", ln=True, align='C')
    pdf.ln(10)

    for q, a in session['history']:
        q_clean = q.replace("€", "EUR")
        a_clean = a.replace("€", "EUR")
        pdf.multi_cell(0, 10, latin1_safe(f"{q_clean} : {a_clean}"))

    pdf.ln(5)
    pdf.cell(0, 10, latin1_safe(f"Probabilité de défaut : {session['proba']}%"), ln=True)
    pdf.cell(0, 10, latin1_safe(f"Évaluation : {session['result']}"), ln=True)
    reco_clean = session['reco'].replace('<br>', '\n')
    pdf.multi_cell(0, 10, latin1_safe(f"Recommandation : {reco_clean}"))

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name="diagnostic_credit.pdf")

@app.route("/reset", methods=["GET"])
def reset():
    session.clear()
    return redirect(url_for("chat"))
