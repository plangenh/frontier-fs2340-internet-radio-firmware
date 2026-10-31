# Majority Touro / Frontier FS2340 firmware research

Offene, unabhängige Untersuchung der Display-Ressourcen, Menüstrukturen und des Update-Containers eines Majority-Touro-Internetradios mit Frontier-Technik. Kein offizielles Herstellerprojekt.

**Stand: 31. Oktober 2026.** Dieses Repository dokumentiert Erkenntnisse und bietet Offline-Analysewerkzeuge. Es enthält keine installierbare Firmware und kein bestätigtes Wiederherstellungsverfahren.

## Ergebnisse

- 359 komprimierte Blöcke des untersuchten Original-Updates geprüft.
- 15 Sprachentabellen mit jeweils 1.056 Textressourcen identifiziert.
- 39 statische Listen-/Menüformulare mit 102 deklarierten Einträgen gefunden; 95 Beschriftungen statisch aufgelöst, sieben dynamisch oder offen.
- 65 Bitmap-Ressourcen im Format 4 bpp / RGB565 identifiziert und intern byteidentisch zurückkodiert.
- Podcast-Symbole auf die Renderer-Indizes 42–44 zurückgeführt.
- Einen Fehler beim Neuaufteilen von Loader-Kommandos in einer experimentellen Änderung identifiziert. Nach deren Installation blieb ein Testgerät beim Start hängen; eine erfolgreiche Recovery steht aus.

**Vorhandene Texte und Tabellen belegen keine Freischaltung einer Funktion auf jedem Gerät.** Einige Menüs entstehen dynamisch. Statische Analyse ist keine beobachtete Ausführung.

## Dokumentation

- [Erkenntnisse und Beleglage](docs/findings.md)
- [Menüstrukturen](docs/menus.md)
- [Container und Loader](docs/container.md)
- [Grafikressourcen](docs/display.md)
- [Fehlgeschlagenes Update / Recovery-Stand](docs/recovery.md)
- [Lokale Analyse](docs/reproduce.md)
- [GitHub und Pages später verbinden](docs/publishing.md)
- [Datenschutz und Veröffentlichungsgrenzen](docs/publication-scope.md)

Die [Menüübersicht](site/index.html) wird mit einem lokalen Webserver geöffnet (siehe Anleitung) oder über GitHub Pages aus `site/` veröffentlicht. Diese öffentliche Ausgabe enthält ausgewählte kurze Menübeschriftungen und technische Metadaten; die vollständigen Sprachpakete und Originalgrafiken sind nicht enthalten.

## Schnellstart

Python 3.10 oder neuer; nur Standardbibliothek:

```sh
python3 -m unittest discover -s tests -v
python3 tools/publication_check.py
python3 tools/analyze_firmware.py /pfad/zur/eigenen/original.isu.bin --output private/analysis
python3 tools/extract_resources.py private/analysis/manifest.json --output private/resources
```

Die Analyse ist an die dokumentierte Firmware gebunden und kontaktiert kein Gerät. Es gibt hier keinen Upload- oder Flash-Befehl. Entpackte lokale Daten bleiben unter `private/` und werden von Git ignoriert.

## Mitmachen

Siehe [CONTRIBUTING.md](CONTRIBUTING.md). Bitte Beobachtungen, statische Belege und Vermutungen unterscheiden und öffentliche Anhänge vorher auf Zugangsdaten und Gerätekennungen prüfen.

## Lizenz / Herkunft

Eigene Skripte und eigene Dokumentation: [MIT](LICENSE). Hersteller-Firmware, daraus gewonnene Beschriftungen, Produktnamen und fremde Beiträge bleiben von dieser Lizenz unberührt; siehe [NOTICE](NOTICE). Die Werkzeuge wurden mit KI-Unterstützung entwickelt. Tests prüfen ausgewählte Eigenschaften, keine allgemeine Eignung für beliebige Firmware.
