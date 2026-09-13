import os
import secrets
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort, Response
import io
import qrcode

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ADMIN_PIN = os.environ.get("ADMIN_PIN", "1791")

QUESTIONS = [
    {"id": 1, "text": "Beendet die Verfassung von 1791 die politische Vorherrschaft des Königs, obwohl er weiterhin Staatsoberhaupt bleibt?"},
    
    {"id": 2, "text": "Stellt die Einführung einer gewählten Nationalversammlung einen grundlegenden Bruch mit der politischen Ordnung des Ancien Régime dar?"},
    
    {"id": 3, "text": "Bedeutet die Aussage, dass die Staatsgewalt von der Nation ausgeht, dass politische Herrschaft nicht mehr allein durch die Stellung des Königs legitimiert wird?"},
    
    {"id": 4, "text": "Beseitigt die rechtliche Gleichheit der Bürger die gesellschaftlichen Unterschiede zwischen Adel, Klerus und dem übrigen Volk?"},
    
    {"id": 5, "text": "Kann eine Verfassung als revolutionär gelten, obwohl ein großer Teil der Bevölkerung weiterhin vom politischen Entscheidungsprozess ausgeschlossen bleibt?"},
    
    {"id": 6, "text": "Widerspricht es dem Anspruch der Revolution auf Freiheit und Gleichheit, dass Frauen keine politischen Rechte erhalten?"},
    
    {"id": 7, "text": "Zeigt das Vetorecht des Königs, dass die Revolutionäre die monarchische Herrschaft nicht vollständig abschaffen wollten?"},
    
    {"id": 8, "text": "Bedeutet die Beschränkung der politischen Macht des Königs, dass Frankreich bereits eine demokratische Ordnung geschaffen hat?"},
    
    {"id": 9, "text": "Verändert die Abschaffung ständischer Vorrechte die rechtliche Ordnung stärker als die bloße Einführung einer gewählten Volksvertretung?"},
    
    {"id": 10, "text": "Widerspricht es dem Gedanken der Volkssouveränität, wenn politische Rechte von Besitz oder Steuerleistung abhängen?"},
    
    {"id": 11, "text": "Verhindert die Verteilung staatlicher Macht auf verschiedene Institutionen, dass politische Herrschaft erneut vollständig in den Händen einer einzelnen Person liegt?"},
    
    {"id": 12, "text": "Verwirklicht die Verfassung von 1791 die Forderungen der Französischen Revolution nur teilweise?"}
]

# Bewusst knapp gehaltene Vergleichspunkte für die abschließende Auswertung.
# Sie dienen als Orientierung für die Lehrkraft, nicht als automatische Bewertung
# der freien Schülervorschläge.
ACTUAL_CONSTITUTION = [
    {
        "title": "Souveränität",
        "text": "Die Souveränität liegt bei der Nation. Die politische Ordnung ist repräsentativ."
    },
    {
        "title": "Gesetzgebung",
        "text": "Eine gewählte gesetzgebende Versammlung beschließt die Gesetze."
    },
    {
        "title": "König",
        "text": "Frankreich bleibt eine konstitutionelle Monarchie. Der König übt die Exekutive aus."
    },
    {
        "title": "Veto",
        "text": "Der König besitzt ein nur aufschiebendes Vetorecht gegen Beschlüsse der Gesetzgebung."
    },
    {
        "title": "Wahlrecht",
        "text": "Das politische Wahlrecht ist eingeschränkt und an Voraussetzungen geknüpft; es handelt sich um ein männliches Zensuswahlrecht."
    },
    {
        "title": "Frauen",
        "text": "Frauen erhalten keine politischen Wahlrechte. Olympe de Gouges kritisiert diese Begrenzung 1791."
    },
    {
        "title": "Gleichheit",
        "text": "Die neue Ordnung beruht auf rechtlicher Gleichheit und der Abkehr von ständischen Vorrechten; rechtliche, soziale und politische Gleichheit sind jedoch nicht dasselbe."
    },
    {
        "title": "Gewaltenteilung",
        "text": "Die staatlichen Funktionen werden auf verschiedene Institutionen verteilt und damit die Macht des Königs begrenzt."
    },
]

state = {
    "active": False,
    "session_id": None,
    "phase": "swipe",  # swipe | constitution
    "round": 1,
    "question_index": 0,
    "accepting": False,
    "revealed": False,
    "votes": {},
    "final_scores": [],

    "submission_open": False,
    "proposals": [],
    "next_proposal_id": 1,
    "current_proposal_id": None,
    "proposal_accepting": False,
    "proposal_revealed": False,
    "proposal_votes": {"yes": 0, "no": 0, "total": 0},
    "constitution_rules": [],
    "comparison_released": False,
}

def fresh_votes():
    return {"yes": 0, "no": 0, "total": 0}


def current_question():
    return QUESTIONS[state["question_index"]]


def current_proposal():
    proposal_id = state["current_proposal_id"]
    if proposal_id is None:
        return None
    return next(
        (p for p in state["proposals"] if p["id"] == proposal_id),
        None,
    )
    
def ensure_student_session():
    if state["session_id"] is None:
        return

    if session.get("student_session_id") != state["session_id"]:
        session["student_session_id"] = state["session_id"]

        session.pop("voted", None)
        session.pop("proposal_session_id", None)
        session.pop("proposal_voted_id", None)

        session.modified = True

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
    # Prüfen, ob der Browser zur aktuell laufenden Unterrichts-Session gehört
    ensure_student_session()

    if state["active"] and state["phase"] == "swipe":
        q = current_question()

        return jsonify({
            "active": True,
            "phase": "swipe",
            "round": 1,
            "question_index": state["question_index"],
            "question_count": len(QUESTIONS),
            "question": q,
            "accepting": state["accepting"],
            "revealed": state["revealed"],
            "votes": state["votes"].get(
                1,
                {}
            ).get(
                state["question_index"],
                fresh_votes()
            ),
        })

    if state["active"] and state["phase"] == "constitution":
        proposal = current_proposal()

        voted = bool(
            proposal
            and session.get("proposal_voted_id") == proposal["id"]
        )

        return jsonify({
            "active": True,
            "phase": "constitution",
            "round": 1,
            "question_index": 0,
            "question_count": len(QUESTIONS),
            "question": None,

            "accepting": state["proposal_accepting"],
            "revealed": state["proposal_revealed"],

            "submission_open": state["submission_open"],

            # Hat der Schüler in DIESER Session bereits
            # einen Verfassungsvorschlag eingereicht?
            "submission_sent": (
                session.get("proposal_session_id")
                == state["session_id"]
            ),

            "proposal": proposal,
            "proposal_voted": voted,
            "proposal_votes": state["proposal_votes"],

            "constitution_rules": state["constitution_rules"],
            "comparison_released": state["comparison_released"],
        })

    return jsonify({
        "active": False,
        "phase": "waiting",
        "round": 1,
        "question_index": 0,
        "question_count": len(QUESTIONS),
        "question": None,

        "accepting": False,
        "revealed": False,
        "votes": fresh_votes(),

        "submission_open": False,
        "proposal": None,
        "proposal_voted": False,
        "proposal_votes": fresh_votes(),

        "constitution_rules": state["constitution_rules"],
        "comparison_released": state["comparison_released"],

        "submission_sent": False,
    })


@app.route("/api/vote", methods=["POST"])
def vote():
    # Prüfen, ob der Schüler zur aktuellen Session gehört
    ensure_student_session()

    if (
        not state["active"]
        or state["phase"] != "swipe"
        or not state["accepting"]
    ):
        return jsonify({
            "ok": False,
            "error": "Die Abstimmung ist gerade geschlossen."
        }), 409

    voter_tokens = session.setdefault("voted", {})

    key = f'1:{state["question_index"]}'

    if voter_tokens.get(key):
        return jsonify({
            "ok": False,
            "error": "Du hast bereits abgestimmt."
        }), 409

    data = request.get_json(silent=True) or {}
    answer = data.get("answer")

    if answer not in ("yes", "no"):
        return jsonify({
            "ok": False,
            "error": "Ungültige Antwort."
        }), 400

    state["votes"].setdefault(1, {})
    state["votes"][1].setdefault(
        state["question_index"],
        fresh_votes()
    )

    bucket = state["votes"][1][state["question_index"]]

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

    return jsonify({
        "active": state["active"],
        "phase": state["phase"],
        "round": state["round"],
        "question_index": state["question_index"],
        "question_count": len(QUESTIONS),
        "question": (
            current_question()
            if state["active"] and state["phase"] == "swipe"
            else None
        ),
        "accepting": state["accepting"],
        "revealed": state["revealed"],
        "votes": (
            state["votes"].get(1, {}).get(state["question_index"], fresh_votes())
            if state["phase"] == "swipe"
            else fresh_votes()
        ),
        "submission_open": state["submission_open"],
        "proposals": state["proposals"],
        "current_proposal": current_proposal(),
        "proposal_accepting": state["proposal_accepting"],
        "proposal_revealed": state["proposal_revealed"],
        "proposal_votes": state["proposal_votes"],
        "constitution_rules": state["constitution_rules"],
        "actual_constitution": ACTUAL_CONSTITUTION,
        "final_scores": state["final_scores"],
    })


@app.route("/api/admin/start", methods=["POST"])
def admin_start():
    require_admin()

    state.update({
        "active": True,

        # Neue Unterrichts-Session erzeugen
        "session_id": secrets.token_hex(16),

        "phase": "swipe",
        "round": 1,
        "question_index": 0,
        "accepting": False,
        "revealed": False,
        "votes": {1: {}},
        "final_scores": [],

        "submission_open": False,
        "proposals": [],
        "next_proposal_id": 1,
        "current_proposal_id": None,
        "proposal_accepting": False,
        "proposal_revealed": False,
        "proposal_votes": fresh_votes(),
        "constitution_rules": [],
        "comparison_released": False,
    })

    # Nur die Admin-Session bereinigen
    session.pop("voted", None)
    session.pop("proposal_voted_id", None)

    return jsonify({"ok": True})


@app.route("/api/admin/open", methods=["POST"])
def admin_open():
    require_admin()
    if state["phase"] != "swipe":
        return jsonify({"ok": False, "error": "Runde 1 ist bereits beendet."}), 409
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
    if state["phase"] != "swipe":
        return jsonify({"ok": False, "error": "Runde 1 ist beendet."}), 400

    if state["question_index"] < len(QUESTIONS) - 1:
        state["question_index"] += 1
        state["accepting"] = False
        state["revealed"] = False
        session.pop("voted", None)
        return jsonify({"ok": True})

    return jsonify({"ok": False, "error": "Das war die letzte Aussage."}), 400


@app.route("/api/admin/start_constitution", methods=["POST"])
def admin_start_constitution():
    require_admin()

    state["active"] = True
    state["phase"] = "constitution"
    state["accepting"] = False
    state["revealed"] = False
    state["submission_open"] = True
    state["current_proposal_id"] = None
    state["proposal_accepting"] = False
    state["proposal_revealed"] = False
    state["proposal_votes"] = fresh_votes()
    state["constitution_rules"] = []
    state["comparison_released"] = False
    session.pop("proposal_voted_id", None)
    session.pop("proposal_session_id", None)

    return jsonify({"ok": True})


@app.route("/api/proposal/submit", methods=["POST"])
def submit_proposal():
    # Prüfen, ob der Browser zur aktuellen Unterrichts-Session gehört
    ensure_student_session()

    if (
        not state["active"]
        or state["phase"] != "constitution"
        or not state["submission_open"]
    ):
        return jsonify({
            "ok": False,
            "error": "Vorschläge können gerade nicht eingereicht werden."
        }), 409

    # Prüfen, ob bereits in DIESER Session ein Vorschlag eingereicht wurde
    if session.get("proposal_session_id") == state["session_id"]:
        return jsonify({
            "ok": False,
            "error": "Du hast bereits einen Vorschlag eingereicht."
        }), 409

    data = request.get_json(silent=True) or {}
    text = " ".join(str(data.get("text", "")).split()).strip()

    if len(text) < 8:
        return jsonify({
            "ok": False,
            "error": "Der Vorschlag ist zu kurz."
        }), 400

    if len(text) > 240:
        return jsonify({
            "ok": False,
            "error": "Bitte formuliere den Vorschlag in höchstens 240 Zeichen."
        }), 400

    proposal = {
        "id": state["next_proposal_id"],
        "text": text,
        "status": "pending",
    }

    state["next_proposal_id"] += 1
    state["proposals"].append(proposal)

    # Diesen Schüler für diese konkrete Session als "hat eingereicht" markieren
    session["proposal_session_id"] = state["session_id"]
    session.modified = True

    return jsonify({"ok": True})


@app.route("/api/admin/submissions/close", methods=["POST"])
def admin_close_submissions():
    require_admin()
    state["submission_open"] = False
    return jsonify({"ok": True})


@app.route("/api/admin/proposal/select", methods=["POST"])
def admin_select_proposal():
    require_admin()

    data = request.get_json(silent=True) or {}
    try:
        proposal_id = int(data.get("id"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Ungültiger Vorschlag."}), 400

    proposal = next(
        (p for p in state["proposals"] if p["id"] == proposal_id and p["status"] == "pending"),
        None,
    )
    if not proposal:
        return jsonify({"ok": False, "error": "Vorschlag nicht gefunden oder bereits bearbeitet."}), 404

    state["current_proposal_id"] = proposal_id
    state["proposal_accepting"] = False
    state["proposal_revealed"] = False
    state["proposal_votes"] = fresh_votes()

    proposal["status"] = "selected"
    session.pop("proposal_voted_id", None)

    return jsonify({"ok": True})


@app.route("/api/admin/proposal/open", methods=["POST"])
def admin_open_proposal():
    require_admin()
    if current_proposal() is None:
        return jsonify({"ok": False, "error": "Zuerst einen Vorschlag auswählen."}), 400

    state["proposal_accepting"] = True
    state["proposal_revealed"] = False
    session.pop("proposal_voted_id", None)
    return jsonify({"ok": True})


@app.route("/api/admin/proposal/close", methods=["POST"])
def admin_close_proposal():
    require_admin()
    state["proposal_accepting"] = False
    return jsonify({"ok": True})


@app.route("/api/admin/proposal/reveal", methods=["POST"])
def admin_reveal_proposal():
    require_admin()
    state["proposal_accepting"] = False
    state["proposal_revealed"] = True
    return jsonify({"ok": True})


@app.route("/api/proposal/vote", methods=["POST"])
def vote_proposal():
    # Prüfen, ob der Browser zur aktuellen Unterrichts-Session gehört
    ensure_student_session()

    if (
        not state["active"]
        or state["phase"] != "constitution"
        or not state["proposal_accepting"]
        or current_proposal() is None
    ):
        return jsonify({
            "ok": False,
            "error": "Die Abstimmung ist gerade geschlossen."
        }), 409

    proposal_id = current_proposal()["id"]

    if session.get("proposal_voted_id") == proposal_id:
        return jsonify({
            "ok": False,
            "error": "Du hast bereits abgestimmt."
        }), 409

    data = request.get_json(silent=True) or {}
    answer = data.get("answer")

    if answer not in ("yes", "no"):
        return jsonify({
            "ok": False,
            "error": "Ungültige Antwort."
        }), 400

    state["proposal_votes"][answer] += 1
    state["proposal_votes"]["total"] += 1

    session["proposal_voted_id"] = proposal_id
    session.modified = True

    return jsonify({"ok": True})


@app.route("/api/admin/proposal/accept", methods=["POST"])
def admin_accept_proposal():
    require_admin()

    proposal = current_proposal()
    if proposal is None:
        return jsonify({"ok": False, "error": "Kein Vorschlag ausgewählt."}), 400

    if not state["proposal_revealed"]:
        return jsonify({
            "ok": False,
            "error": "Zeige zuerst das Abstimmungsergebnis."
        }), 400

    yes = state["proposal_votes"]["yes"]
    no = state["proposal_votes"]["no"]

    if yes <= no:
        return jsonify({
            "ok": False,
            "error": "Der Vorschlag hat keine Mehrheit für die Aufnahme."
        }), 409

    proposal["status"] = "accepted"
    state["constitution_rules"].append({
        "number": len(state["constitution_rules"]) + 1,
        "text": proposal["text"],
        "proposal_id": proposal["id"],
    })

    state["current_proposal_id"] = None
    state["proposal_accepting"] = False
    state["proposal_revealed"] = False
    state["proposal_votes"] = fresh_votes()
    session.pop("proposal_voted_id", None)

    return jsonify({"ok": True})


@app.route("/api/admin/proposal/reject", methods=["POST"])
def admin_reject_proposal():
    require_admin()

    proposal = current_proposal()
    if proposal is None:
        return jsonify({"ok": False, "error": "Kein Vorschlag ausgewählt."}), 400

    proposal["status"] = "rejected"
    state["current_proposal_id"] = None
    state["proposal_accepting"] = False
    state["proposal_revealed"] = False
    state["proposal_votes"] = fresh_votes()
    session.pop("proposal_voted_id", None)

    return jsonify({"ok": True})


@app.route("/api/admin/release_comparison", methods=["POST"])
def release_comparison():
    require_admin()
    state["comparison_released"] = True
    return jsonify({"ok": True})


@app.route("/api/admin/final-score", methods=["POST"])
def final_score():
    if not state["active"]:
        return jsonify({"ok": False}), 409

    data = request.get_json(silent=True) or {}
    try:
        score = int(data.get("score", -1))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Ungültige Bewertung."}), 400

    if not 0 <= score <= 10:
        return jsonify({"ok": False, "error": "Score muss zwischen 0 und 10 liegen."}), 400

    state["final_scores"].append(score)
    return jsonify({"ok": True})


@app.route("/api/admin/reset", methods=["POST"])
def admin_reset():
    require_admin()
    state.update({
        "active": False,
        "session_id": None,
        "phase": "swipe",
        "round": 1,
        "question_index": 0,
        "accepting": False,
        "revealed": False,
        "votes": {},
        "final_scores": [],
        "submission_open": False,
        "proposals": [],
        "next_proposal_id": 1,
        "current_proposal_id": None,
        "proposal_accepting": False,
        "proposal_revealed": False,
        "proposal_votes": fresh_votes(),
        "constitution_rules": [],
        "comparison_released": False,
    })
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/admin/summary")
def admin_summary():
    require_admin()

    result = []
    r1 = state["votes"].get(1, {})
    for i, q in enumerate(QUESTIONS):
        result.append({
            "question": q,
            "round1": r1.get(i, fresh_votes()),
        })

    scores = state["final_scores"]

    return jsonify({
        "questions": result,
        "scores": scores,
        "score_average": round(sum(scores) / len(scores), 1) if scores else None,
        "constitution_rules": state["constitution_rules"],
        "actual_constitution": ACTUAL_CONSTITUTION,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
