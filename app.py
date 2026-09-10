import os
import secrets
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort, Response
import io
import qrcode

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ADMIN_PIN = os.environ.get("ADMIN_PIN", "1791")

QUESTIONS = [
    {
        "id": 1,
        "text": "Die Verfassung von 1791 beendet die politische Vorherrschaft des Königs, obwohl er weiterhin Staatsoberhaupt bleibt."
    },
    {
        "id": 2,
        "text": "Die Einführung einer gewählten Nationalversammlung stellt einen grundlegenden Bruch mit der politischen Ordnung des Ancien Régime dar."
    },
    {
        "id": 3,
        "text": "Wenn die Staatsgewalt von der Nation ausgeht, bedeutet dies, dass politische Herrschaft nicht mehr allein durch die Stellung des Königs legitimiert wird."
    },
    {
        "id": 4,
        "text": "Die rechtliche Gleichheit der Bürger beseitigt die gesellschaftlichen Unterschiede zwischen Adel, Klerus und dem übrigen Volk."
    },
    {
        "id": 5,
        "text": "Eine Verfassung kann als revolutionär gelten, obwohl ein großer Teil der Bevölkerung weiterhin vom politischen Entscheidungsprozess ausgeschlossen bleibt."
    },
    {
        "id": 6,
        "text": "Dass Frauen keine politischen Rechte erhalten, widerspricht dem Anspruch der Revolution auf Freiheit und Gleichheit."
    },
    {
        "id": 7,
        "text": "Das Vetorecht des Königs zeigt, dass die Revolutionäre die monarchische Herrschaft nicht vollständig abschaffen wollten."
    },
    {
        "id": 8,
        "text": "Die Beschränkung der politischen Macht des Königs bedeutet nicht automatisch, dass Frankreich bereits eine demokratische Ordnung geschaffen hat."
    },
    {
        "id": 9,
        "text": "Die Abschaffung ständischer Vorrechte verändert die rechtliche Ordnung stärker als die bloße Einführung einer gewählten Volksvertretung."
    },
    {
        "id": 10,
        "text": "Wenn politische Rechte von Besitz oder Steuerleistung abhängen, widerspricht dies dem Gedanken der Volkssouveränität."
    },
    {
        "id": 11,
        "text": "Die Verteilung staatlicher Macht auf verschiedene Institutionen verhindert, dass politische Herrschaft erneut vollständig in den Händen einer einzelnen Person liegt."
    },
    {
        "id": 12,
        "text": "Die Verfassung von 1791 verwirklicht die Forderungen der Französischen Revolution nur teilweise."
    }
]
# Alles wird nur im laufenden Prozess gehalten.
# Keine Namen, E-Mail-Adressen oder individuellen Antwortverläufe werden gespeichert.
state = {
    "active": False,
    "round": 1,
    "question_index": 0,
    "accepting": False,
    "revealed": False,
    "votes": {},
    "final_scores": []
}

def fresh_votes():
    return {"yes": 0, "no": 0, "total": 0}

def current_question():
    return QUESTIONS[state["question_index"]]

def require_admin():
    if not session.get("admin"):
        abort(403)

@app.route("/")
def index():
    return redirect(url_for("student"))

@app.route("/student")
def student():
    return render_template("student.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/qr.png")
def qr_png():
    # QR always points to the public student view of the currently deployed app.
    target = url_for("student", _external=True)
    img = qrcode.make(target)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return Response(buffer.getvalue(), mimetype="image/png")

@app.route("/admin")
def admin():
    return render_template("admin.html", questions=QUESTIONS)

@app.route("/api/status")
def status():
    q = current_question() if state["active"] else None
    return jsonify({
        "active": state["active"],
        "round": state["round"],
        "question_index": state["question_index"],
        "question_count": len(QUESTIONS),
        "question": q if state["active"] else None,
        "accepting": state["accepting"],
        "revealed": state["revealed"],
        "votes": state["votes"].get(state["round"], {}).get(state["question_index"], fresh_votes()),
    })

@app.route("/api/vote", methods=["POST"])
def vote():
    if not state["active"] or not state["accepting"]:
        return jsonify({"ok": False, "error": "Die Abstimmung ist gerade geschlossen."}), 409

    # Pro Gerät/Browser nur eine Antwort pro Frage.
    # Diese Kennung ist zufällig und enthält keinerlei Identitätsinformation.
    voter_tokens = session.setdefault("voted", {})
    key = f'{state["round"]}:{state["question_index"]}'
    if voter_tokens.get(key):
        return jsonify({"ok": False, "error": "Du hast bereits abgestimmt."}), 409

    data = request.get_json(silent=True) or {}
    answer = data.get("answer")
    if answer not in ("yes", "no"):
        return jsonify({"ok": False, "error": "Ungültige Antwort."}), 400

    state["votes"].setdefault(state["round"], {})
    state["votes"][state["round"]].setdefault(state["question_index"], fresh_votes())
    bucket = state["votes"][state["round"]][state["question_index"]]
    bucket[answer] += 1
    bucket["total"] += 1

    voter_tokens[key] = True
    session["voted"] = voter_tokens
    session.modified = True

    return jsonify({"ok": True})

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    if secrets.compare_digest(str(data.get("pin", "")), ADMIN_PIN):
        session.clear()
        session["admin"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Falscher PIN."}), 401

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/admin/state")
def admin_state():
    require_admin()
    return status()

@app.route("/api/admin/start", methods=["POST"])
def admin_start():
    require_admin()
    state.update({
        "active": True,
        "round": 1,
        "question_index": 0,
        "accepting": False,
        "revealed": False,
        "votes": {1: {}, 2: {}},
        "final_scores": []
    })
    session.pop("voted", None)
    return jsonify({"ok": True})

@app.route("/api/admin/open", methods=["POST"])
def admin_open():
    require_admin()
    state["accepting"] = True
    state["revealed"] = False
    return jsonify({"ok": True})

@app.route("/api/admin/close", methods=["POST"])
def admin_close():
    require_admin()
    state["accepting"] = False
    return jsonify({"ok": True})

@app.route("/api/admin/reveal", methods=["POST"])
def admin_reveal():
    require_admin()
    state["accepting"] = False
    state["revealed"] = True
    return jsonify({"ok": True})

@app.route("/api/admin/next", methods=["POST"])
def admin_next():
    require_admin()
    if state["question_index"] < len(QUESTIONS) - 1:
        state["question_index"] += 1
        state["accepting"] = False
        state["revealed"] = False
        # Alte Geräte dürfen bei der neuen Frage wieder abstimmen.
        session.pop("voted", None)
        return jsonify({"ok": True})

    return jsonify({"ok": False, "error": "Das war die letzte Aussage."}), 400

@app.route("/api/admin/start_round2", methods=["POST"])
def admin_start_round2():
    require_admin()
    state["round"] = 2
    state["question_index"] = 0
    state["accepting"] = False
    state["revealed"] = False
    # Ganz wichtig: Runde 1 und Runde 2 werden nicht auf Personenebene verbunden.
    session.pop("voted", None)
    return jsonify({"ok": True})

@app.route("/api/admin/final-score", methods=["POST"])
def final_score():
    if not state["active"]:
        return jsonify({"ok": False}), 409
    data = request.get_json(silent=True) or {}
    score = int(data.get("score", -1))
    if not 0 <= score <= 10:
        return jsonify({"ok": False, "error": "Score muss zwischen 0 und 10 liegen."}), 400
    state["final_scores"].append(score)
    return jsonify({"ok": True})

@app.route("/api/admin/reset", methods=["POST"])
def admin_reset():
    require_admin()
    state.update({
        "active": False,
        "round": 1,
        "question_index": 0,
        "accepting": False,
        "revealed": False,
        "votes": {},
        "final_scores": []
    })
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/admin/summary")
def admin_summary():
    require_admin()
    r1, r2 = state["votes"].get(1, {}), state["votes"].get(2, {})
    result = []
    for i, q in enumerate(QUESTIONS):
        a = r1.get(i, fresh_votes())
        b = r2.get(i, fresh_votes())
        result.append({"question": q, "round1": a, "round2": b})
    scores = state["final_scores"]
    return jsonify({
        "questions": result,
        "scores": scores,
        "score_average": round(sum(scores) / len(scores), 1) if scores else None
    })

if __name__ == "__main__":
    # 0.0.0.0 ist für lokales LAN relevant. Im Cloud-Hosting wird PORT verwendet.
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
