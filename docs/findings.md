# Erkenntnisse und Beleglage

Untersuchtes Original: `ir-cui-FS2340-0000-0444_V4.10.18.281972.EX11_10-1A8.isu.bin`

SHA-256: `48a9da85d2580ee7fffde0f204ee2046ae0e300a2f23f1e4a6a5e3b299bd0dc3`  
Größe: 4.136.167 Bytes.

| Befund | Belegtyp | Grenze |
|---|---|---|
| 359 komprimierte Blöcke, CRC-16 und entpackte Größen stimmen | Offline-Parser; interner Vergleich mit zweitem Decoder | Gilt für dieses Artefakt |
| 15 Tabellen mit je 1.056 Ressourcen | Zeigerauflösung und erneuter bytegenauer Abgleich aller 15.840 Strings | Sprachkennung aus Texten abgeleitet |
| 39 Listenformulare / 102 Einträge / 95 statische Beschriftungen | Gemeinsames 64-Byte-Format, 20-Byte-Einträge, gültige IDs | Dynamische Einträge und Modellfilter offen |
| 65 Grafikdatensätze | Lückenloser Bereich und interner byteidentischer Rückweg aus PNG | Originalgrafiken werden nicht mitgeliefert |
| Podcast nutzt Bilder 42–44 | Statische Instruktionsanalyse von Lookup, Variantenwahl und Renderer | Kein neu beobachteter Laufzeittest |
| Experimentelles Bild-Update verletzte Blockgrenzen | Vergleich Original / Varianten, 113 problematische Blöcke | Tatsächlicher Bootloader-Kontrollfluss noch offen |

## Adresskonvention

Datenadressen verwenden hier die Ladeansicht, etwa `0x32aeea8c`. Code- und andere Zeiger können den Alias mit gesetztem höchstem Bit verwenden, etwa `0xb2aeea8c`. Das Maskieren dieses Bits ist für die untersuchten Datenzugriffe belegt; es ist kein allgemeiner Ersatz für die korrekte Abbildung von MinIM-Ausführungsadressen.

## Nicht nachgewiesen

- Vollständige dynamische Menü-Hierarchie oder Freischaltung aller Plattformfunktionen.
- Abwesenheit zusätzlicher kryptografischer Prüfungen.
- Ein sicher installierbares eigenes UI oder eine erfolgreiche Wiederherstellung des festhängenden Geräts.
- Eine allgemeine Recovery-Tastenkombination, USB-Recovery oder bestätigte Debug-Pinbelegung.

Die zugrunde liegenden Rohdaten bleiben privat. Kuratierte Tabellen und reproduzierbare Werkzeuge machen die beschriebenen Teilbefunde nachvollziehbar, ersetzen aber kein öffentliches vollständiges Disassembler-Projekt.
