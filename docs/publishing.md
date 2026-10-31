# GitHub später verbinden

Das lokale Repository ist unabhängig vom privaten Analyse-Arbeitsverzeichnis. Es enthält noch keinen Remote und keine Zugangsdaten.

## Repository im Browser anlegen

1. Bei GitHub anmelden und ein neues Repository namens `majority-touro-research` anlegen.
2. Sichtbarkeit **Public** wählen. Keine zusätzliche README, Lizenz oder `.gitignore` erzeugen, da diese hier bereits vorhanden sind.
3. Im Terminal in diesen Projektordner wechseln. Bei Bedarf die eigene Git-Identität nur für dieses Repository setzen.
4. Die von GitHub angezeigte HTTPS- oder SSH-Adresse als Remote hinzufügen und pushen:

```sh
git remote add origin https://github.com/DEIN-NAME/majority-touro-research.git
git push -u origin main
```

Die GitHub-Anmeldung erfolgt dabei über deine eigenen Git-Zugangsdaten oder die GitHub CLI. Für die Veröffentlichung sind keine Zugangsdaten in Projektdateien nötig.

## GitHub Pages aktivieren

Nach dem Push: **Settings → Pages → Build and deployment → Source: GitHub Actions** auswählen. Danach unter **Actions → Deploy research pages → Run workflow** ausführen. Der Workflow lädt ausschließlich `site/` hoch. Spätere Pushes auf `main`, die `site/` ändern, starten das Deployment erneut.

GitHub zeigt die endgültige Pages-Adresse im Deployment an. Es ist vor der Verbindung noch keine öffentliche URL vorhanden.

## ZIP-Alternative

Das beigefügte ZIP enthält nur die kuratierten Projektdateien, ohne Git-Historie. Entpacken und per GitHub-Weboberfläche hochladen ist ebenfalls möglich; versteckte Dateien wie `.github/` und `.gitignore` mit übernehmen.

## Vor jeder Veröffentlichung

```sh
python3 -m unittest discover -s tests -v
python3 tools/publication_check.py
git status --short
git diff --cached
```

Die Prüfungen ersetzen keine inhaltliche Durchsicht neu hinzugefügter Anhänge.

Die Pages-Konfiguration folgt der [offiziellen GitHub-Anleitung](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
