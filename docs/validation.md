# Validierung vor der Veröffentlichung

Datum: 31. Oktober 2026.

- Synthetische Tests: drei Tests erfolgreich, einschließlich DEFLATE-Rückweg auf vier Kompressionsstufen und Zurückweisung eines über die Blockgrenze laufenden Ladebefehls.
- Neue öffentliche Extraktionswerkzeuge gegen das private Original ausgeführt: 359 komprimierte Blöcke, sechs Ketten, 23 Moduldatensätze und 30.084 Loader-Kommandos.
- Alle Originalblöcke separat auf vollständige Kommandos geprüft.
- Sprachressourcen frisch extrahiert: 15 Tabellen / 15.840 Einträge.
- Menüs frisch extrahiert: 39 Formulare / 102 Zeilen. Ergebnis stimmt strukturell vollständig mit der kuratierten öffentlichen JSON-Datei überein.
- Publikationsprüfung auf gesperrte Dateitypen, lokale Nutzerpfade, private Netzwerkadressen, MAC-Adressen und ausgewählte Zugangsdatenmuster erfolgreich.
- Rohdaten und lokale Testausgaben unter `private/` werden ignoriert und sind nicht im Commit oder ZIP enthalten.

Die Tests benötigen keine Hardware. GitHub-Actions-Ausführung und Pages-Deployment sind erst nach Verbindung zu einem GitHub-Repository möglich und wurden nicht als erfolgreich ausgegeben.
