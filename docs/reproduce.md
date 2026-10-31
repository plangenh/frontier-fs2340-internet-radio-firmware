# Lokal reproduzieren

Python 3.10+ mit Standardbibliothek genügt. Keine Fremdprogramme und kein Gerätezugriff nötig.

1. Eine rechtmäßig bezogene eigene Kopie des dokumentierten Original-Updates bereithalten.
2. Den Parser mit einem neuen privaten Ausgabeordner aufrufen:

```sh
python3 tools/analyze_firmware.py /pfad/original.isu.bin --output private/analysis
python3 tools/extract_resources.py private/analysis/manifest.json --output private/resources
```

Der Parser prüft den erwarteten SHA-256, ISU-MD5, Block-CRCs, Größen und vollständige Kommandos pro entpacktem Block. Er erzeugt lokale Modulbereiche, ein Manifest und Zeichenkettenlisten. Die Quell-Firmware wird nur gelesen. Vorhandene Ausgabeordner werden abgewiesen; fehlgeschlagene Läufe können einen unvollständigen neuen Ausgabeordner hinterlassen.

Der Ressourcenleser löst die 15 Sprachentabellen über die Wurzel bei `0x32b12b58` auf. Diese privaten vollständigen Sprachdaten gehören nicht in die Veröffentlichung.

## Menüdeskriptoren erneut extrahieren

```sh
python3 tools/extract_menus.py private/analysis/manifest.json private/resources/locales_complete.json --output private/menus
```

Das Suchmuster ist streng und versionsgebunden; andere UI-Formate und dynamische Einträge bleiben außerhalb der Abdeckung. Die öffentliche Datendatei wurde aus derselben Originalfassung abgeleitet.

## Lokal die öffentliche Seite ansehen

```sh
python3 -m http.server 8000 --directory site
```

Dann den lokalen Port im Browser öffnen. Die Seite braucht weder Build-Schritt noch externe Schriften oder Skripte.

## Tests

```sh
python3 -m unittest discover -s tests -v
python3 tools/publication_check.py
```

Die öffentlichen Tests benutzen synthetische Daten und die kuratierte Menüdatei. Der komplette Firmwaretest benötigt die nicht mitgelieferte Originaldatei und wurde zusätzlich lokal ausgeführt. Alle Aussagen beziehen sich auf die dokumentierte SHA-256; kein allgemeiner Parser für beliebige Frontier-Versionen.
