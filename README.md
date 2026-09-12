# 🇫🇷 SWIPE 1791

Interaktive, anonyme Abstimmungs-App für eine Geschichtsstunde zur französischen Verfassung von 1791.

## Funktionen

- Smartphone-optimierte Schüleransicht
- echtes Links/Rechts-Swipe bei den Aussagen
- keine Registrierung
- keine Namen/E-Mail-Adressen
- Lehrer-Dashboard
- Abstimmungen können zentral geöffnet/geschlossen werden
- Ergebnisse werden erst nach Freigabe angezeigt
- **Runde 1:** spontane Einschätzung von 12 Aussagen zur Verfassung von 1791
- **Verfassungsbau:** Schülerinnen und Schüler können eigene Verfassungsregeln vorschlagen
- Vorschläge werden anonym an den Lehrer übermittelt
- Der Lehrer kann Vorschläge einzeln für die Klasse freigeben
- Die Klasse stimmt über jeden Vorschlag mit **„AUFNEHMEN“ / „NICHT AUFNEHMEN“** ab
- Angenommene Regeln werden live in der **„Klassenverfassung“** gesammelt
- Der Lehrer kann Vorschläge vor der Abstimmung löschen
- Ein Vorschlag kann nur einmal pro Browser/Session eingereicht werden
- Abstimmungen über verschiedene Vorschläge sind weiterhin möglich
- **Historischer Vergleich:** Die selbst erstellte Klassenverfassung kann anschließend mit der tatsächlichen Verfassung von 1791 verglichen werden
- Der historische Vergleich wird erst durch den Lehrer freigegeben
- Abschlussurteil auf einer Skala von 0–10
- Vorher/Nachher-Vergleich nur als Klassenstatistik
- alle Daten werden nur im Arbeitsspeicher gespeichert; ein Neustart der Anwendung löscht die Daten

## Unterrichtsablauf

Die Anwendung ist für einen Unterrichtsablauf zur Leitfrage

> **„Wie revolutionär war die französische Verfassung von 1791 wirklich?“**

konzipiert.

### 1. Runde 1 – SWIPE 1791

Die Schülerinnen und Schüler erhalten nacheinander Aussagen zur französischen Verfassung von 1791 und entscheiden spontan:

- **DAGEGEN**
- **DAFÜR**

Die Ergebnisse werden zunächst nicht auf Personenebene gespeichert und erst durch den Lehrer freigegeben.

### 2. Erarbeitung der Verfassung

Nach der ersten Abstimmungsrunde erfolgt die inhaltliche Arbeit mit historischen Quellen und Auszügen aus der Verfassung von 1791.

### 3. Verfassungsbau

Anschließend entwickeln die Schülerinnen und Schüler gemeinsam eine eigene Verfassung.

Sie können über ihre Smartphones Regeln vorschlagen, die sie für eine gerechte und sinnvolle Verfassung für wichtig halten.

Der Lehrer sieht die eingegangenen Vorschläge anonym im Dashboard und kann sie einzeln für die Klasse zur Abstimmung freigeben.

Die Klasse entscheidet anschließend:

**AUFNEHMEN** oder **NICHT AUFNEHMEN**

Angenommene Regeln werden Bestandteil der gemeinsamen **Klassenverfassung**.

### 4. Historischer Vergleich

Nachdem die Klasse ihre Verfassung erstellt hat, kann der Lehrer den historischen Vergleich freigeben.

Dabei werden zentrale Merkmale der tatsächlichen französischen Verfassung von 1791 den selbst entwickelten Regeln gegenübergestellt.

Dadurch können Gemeinsamkeiten, Unterschiede und mögliche Gründe für die Unterschiede gemeinsam diskutiert werden.

### 5. Abschlussurteil

Zum Abschluss bewerten die Schülerinnen und Schüler auf einer Skala von **0 bis 10**, wie revolutionär sie die französische Verfassung von 1791 nach der Unterrichtsarbeit einschätzen.

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
