"""
>>>                         ADATBÁZIS TESZTELÉSRE
>>>                         NE töröld
>>>                        NE TÖRÖLD 
>>>                       NE 
"""
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
import requests

app = Flask(__name__, template_folder='atmeneti') # template_folder="atmeneti" >>> beállítja a mappát (itt atmeneti mappa) amit "megfigyel" get és post kérésekre
app.secret_key = "supersecretkeyeskü"

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

        # Ellenőrzés >> hCaptcha
        verify_url = "https://hcaptcha.com/siteverify"
        payload = {'secret': HCAPTCHA_SECRET, 'response': hcaptcha_response}
        response = requests.post(verify_url, data=payload)
        result = response.json()

        # CAPTCHA ellenőrzés
        if not result.get("success"):
            session["message"] = "Hibás vagy hiányzó CAPTCHA!"
            session["errorCode"] = ""
            session["hibasNev"] = ""
            return redirect(url_for("error"))
            # RÉGI VERZIÓ >>>> return redirect(url_for("error", message="Hibás vagy hiányzó CAPTCHA!", errorCode=""))

        # Név validálás
        if not user_name: #ha nincs név de mivel a form úgysem engedi elküldeni üresen így ez fölösleges de nem bajjjj
            session["message"] = "Név megadása kötelező!"
            session["errorCode"] = 400
            session["hibasNev"] = ""
            return redirect(url_for("error"))
            # RÉGI VERZIÓ >>>>  return "Név megadása kötelező!", 400
        if len(user_name) < 3:
            session["message"] = "A név túl rövid! 3 betűs nevet írj be."
            session["errorCode"] = ""
            session["hibasNev"] = user_name
            return redirect(url_for("error"))
            # RÉGI VERZIÓ >>>> return redirect(url_for("error", message="A név túl rövid! 3 betűs nevet írj be.", hibasNev=user_name, errorCode=""))
        if len(user_name) > 40:
            session["message"] = "A név túl hosszú! Maximum 40 karakter engedélyezett."
            session["errorCode"] = ""
            session["hibasNev"] = user_name
            return redirect(url_for("error"))
            # RÉGI VERZIÓ >>>> return redirect(url_for("error", message="A név túl hosszú! Maximum 40 karakter engedélyezett.", hibasNev=user_name, errorCode=""))

        # Mentés adatbázisba
        new_visitor = Visitor(user_name=user_name.strip())
        db.session.add(new_visitor)
        db.session.commit()

        # átvisz a success.htmlre ha sikeres ez a fos
        session["user_name"] = user_name.strip()
        return redirect(url_for("success")) # index ha az eredeti oldalra akarom


    # Lekérés
    all_visitors = Visitor.query.order_by(Visitor.created_at.desc()).all()
    return render_template("index.html", visitors=all_visitors)


@app.route("/error")
def error():
    message = session.get("message", "Ismeretlen hiba történt.")
    hibasNev = session.get("hibasNev", "") 
    errorCode = session.get("errorCode", "")
    return render_template("error.html", message=message, hibasNev=hibasNev, errorCode=errorCode)

@app.route("/success", methods=["GET"])
def success():
    user_name = session.get("user_name")
    return render_template("success.html", user_name=user_name)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
