# 🇫🇷 SWIPE 1791

Interaktive, anonyme Abstimmungs-App für eine Geschichtsstunde zur französischen Verfassung von 1791.

## Funktionen

- Smartphone-optimierte Schüleransicht
- echtes Links/Rechts-Swipe
- keine Registrierung
- keine Namen/E-Mail-Adressen
- Lehrer-Dashboard
- Abstimmung kann zentral geöffnet/geschlossen werden
- Ergebnis wird erst nach Freigabe angezeigt
- Runde 1 und Runde 2 werden nicht auf Personenebene miteinander verknüpft
- Vorher/Nachher-Vergleich nur als Klassenstatistik
- Abschlussurteil 0–10
- alle Daten nur im Arbeitsspeicher; Neustart löscht sie

## Lokal testen

Python 3.11+ empfohlen.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Dann:
- Schüler: http://127.0.0.1:5000/student
- Lehrer: http://127.0.0.1:5000/admin

Standard-PIN: `1791`

Für einen echten Einsatz bitte `ADMIN_PIN` und `SECRET_KEY` als Umgebungsvariablen setzen.

## Öffentliches Hosting

Die App kann auf einem Python-fähigen Cloud-Host laufen. Das Projekt enthält dafür eine `Procfile`.

Wichtig: Ein kostenloses Hosting-Angebot ist nicht automatisch dauerhaft kostenlos und kann je nach Anbieter Limits oder Schlafmodi haben.

## Datenschutz-Hinweis

Die Anwendung selbst speichert keine Namen, E-Mail-Adressen oder individuellen Antwortverläufe. Die zufällige Browser-Session verhindert Doppelabstimmungen pro Frage.

Bei öffentlichem Hosting kann der Hosting-Anbieter jedoch technische Server-/Netzwerkprotokolle (z. B. IP-Adressen) führen. Für einen echten Schuleinsatz sollte daher vorab die Datenschutzfreigabe der Schule bzw. des Trägers geklärt werden.

## Fragen ändern

Die 8 Aussagen stehen ganz oben in `app.py` in `QUESTIONS`.


### Bedienung am Laptop
- `←` oder `A` = Dagegen
- `→` oder `D` = Dafür
- Auf Smartphones weiterhin per Swipe oder Button.

## QR-Code für die Schüler

Nach dem Hosting ist der QR-Code automatisch unter:

`https://DEINE-APP-URL.onrender.com/qr.png`

erreichbar.

Der QR-Code führt direkt zur Schüleransicht `/student`. Du kannst ihn einfach
im Browser öffnen und auf dem Beamer anzeigen oder als Bild speichern.

Die Schülerseite ist außerdem direkt unter `/student` erreichbar.
Der Lehrerbereich bleibt unter `/admin`.

## Render

Empfohlene Einstellungen:

- **Service:** Web Service
- **Language:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Plan:** Free zum Testen
- **Region:** Frankfurt
- **Environment Variable:** `SECRET_KEY` mit einem langen zufälligen Wert
- **Environment Variable:** `ADMIN_PIN` mit deinem gewünschten Lehrer-PIN

Die Datenschutzseite ist unter `/privacy` erreichbar.
