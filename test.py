"""
>>>                         ADATBÁZIS TESZTELÉSRE
>>>                         NE töröld
>>>                        NE TÖRÖLD 
>>>                       NE 
"""
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
import requests

app = Flask(__name__, template_folder='atmeneti') # template_folder="atmeneti" >>> beállítja a mappát (itt atmeneti mappa) amit "megfigyel" get és post kérésekre

# Supabase PostgreSQL :fire:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:CentrumProjectDatabase@db.njtwupjeijyfmjraycus.supabase.co:5432/postgres?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# hCaptcha secret key (a dashboardról)
HCAPTCHA_SECRET = "ES_26037e183cf9463b9ce6a91efb767072"

# Táblázat modell
class Visitor(db.Model):
    __tablename__ = 'visitors'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = db.Column(db.VARCHAR(40), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        hcaptcha_response = request.form.get("h-captcha-response")

        # Ellenőrzés az hCaptcha API-nál
        verify_url = "https://hcaptcha.com/siteverify"
        payload = {'secret': HCAPTCHA_SECRET, 'response': hcaptcha_response}
        response = requests.post(verify_url, data=payload)
        result = response.json()

        # CAPTCHA ellenőrzés
        if not result.get("success"):
            return redirect(url_for("error", message="Hibás vagy hiányzó CAPTCHA!", errorCode=""))

        # Név validálás
        if not user_name: #ha nincs név de mivel a form úgysem engedi elküldeni üresen így ez fölösleges de nem bajjjj
            return "Név megadása kötelező!", 400
        if len(user_name) < 3:
            return redirect(url_for("error", message="A név túl rövid! 3 betűs nevet írj be.", errorCode=""))
        if len(user_name) > 40:
            return redirect(url_for("error", message="A név túl hosszú! Maximum 40 karakter engedélyezett.", errorCode=""))

        # Mentés adatbázisba
        new_visitor = Visitor(user_name=user_name.strip())
        db.session.add(new_visitor)
        db.session.commit()

        return redirect(url_for("index"))

    # Lekérés
    all_visitors = Visitor.query.order_by(Visitor.created_at.desc()).all()
    return render_template("index.html", visitors=all_visitors)


@app.route("/error")
def error():
    message = request.args.get("message", "Ismeretlen hiba történt.")
    errorCode = request.args.get("errorCode", "N/A")
    return render_template("error.html", message=message, errorCode=errorCode)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
