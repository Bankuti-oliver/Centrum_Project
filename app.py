# konzol clear mert why not
import os
os.system("cls")

# Database >>>> Flask importok + egyéb alap dolgok
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
import threading
import time

# NFC importok
import nfc
import ndef 

# ------------------ APP & DATABASE CONFIG ------------------
app = Flask(__name__)

# 🔧 Supabase adatbázis kapcsolat (példa URI – ezt cseréld ki a sajátodra!)
# Ezt a Supabase -> Project Settings -> Database -> Connection String alatt találod.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:CentrumProjectSzupiJelszó*@db.njtwupjeijyfmjraycus.supabase.co:5432/postgres?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ DATABASE MODEL ------------------
class Visitor(db.Model):
    __tablename__ = 'visitors'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {"user_id": str(self.user_id), "user_name": self.user_name}

with app.app_context():
    db.create_all()

# ------------------ NFC HELPER FÜGGVÉNYEK ------------------
def write_user_id_to_tag(user_id, timeout=20):
    #Felírja a user_id-t az NFC kártyára (TextRecord).
    try:
        clf = nfc.ContactlessFrontend('usb')
    except Exception as e:
        return {"error": f"NFC eszköz nem elérhető: {e}"}

    result = {"status": "timeout"}
    start = time.time()

    def on_connect(tag):
        try:
            rec = ndef.TextRecord(str(user_id))
            msg = ndef.message.Message(rec)
            if tag.ndef is None:
                tag.format(msg)
            else:
                tag.ndef.message = msg
            result["status"] = "written"
            return True
        except Exception as ex:
            result["status"] = "error"
            result["error"] = f"NFC kártya >> írási << hiba: {ex} | :c"
            return False

    try:
        while time.time() - start < timeout:
            clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: False, timeout=1.0)
            if result.get("status") in ("written", "error"):
                break
        clf.close()
    except Exception as e:
        clf.close()
        return {"error": f"NFC művelet >> hiba <<: {e}"}

    return result


def read_user_id_from_tag(timeout=15):
    # NFC kártya olvasása >>> első TextRecord tartalma
    try:
        clf = nfc.ContactlessFrontend('usb')
    except Exception as e:
        return {"status": "error", "error": f"NFC eszköz nem elérhető: {e}"}

    result = {"status": "timeout"}
    start = time.time()

    def on_connect(tag):
        try:
            if tag.ndef is None:
                result.update({"status": "error", "error": "Nincs NDEF adat a kártyán"})
                return False
            message = tag.ndef.message
            for record in message:
                if isinstance(record, ndef.TextRecord):
                    result.update({"status": "ok", "user_id": record.text})
                    return True
            result.update({"status": "error", "error": "Nincs szöveges rekord"})
            return False
        except Exception as ex:
            result.update({"status": "error", "error": f"Olvasási hiba: {ex}"})

    try:
        while time.time() - start < timeout:
            clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: False, timeout=1.0)
            if result.get("status") in ("ok", "error"):
                break
        clf.close()
    except Exception as e:
        clf.close()
        result.update({"status": "error", "error": f"NFC művelet hiba: {e}"})

    return result

# ------------------ FLASK ROUTES ------------------
@app.route('/')
def index():
    visitors = Visitor.query.all()
    return render_template('index.html', visitors=visitors)


@app.route('/add_visitor', methods=['POST'])
def add_visitor():
    name = request.form.get('user_name')
    if not name:
        return jsonify({"error": "Név megadása kötelező"}), 400

    visitor = Visitor(user_name=name)
    db.session.add(visitor)
    db.session.commit()

    # NFC írás külön szálon, hogy ne blokkolja a Flask-t
    threading.Thread(target=write_user_id_to_tag, args=(visitor.user_id,)).start()

    return redirect(url_for('index'))


@app.route('/read_nfc', methods=['GET'])
def read_nfc():
    result = read_user_id_from_tag()
    if result.get("status") == "ok":
        visitor = Visitor.query.get(uuid.UUID(result["user_id"]))
        if visitor:
            return jsonify(visitor.to_dict())
        else:
            return jsonify({"error": "Látogató nem található"}), 404
    else:
        return jsonify(result), 400


if __name__ == '__main__':
    app.run(debug=True)
