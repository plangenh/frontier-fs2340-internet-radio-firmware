# Mitwirken

1. Firmware-Version und SHA-256 nennen; keine Firmwaredatei anhängen.
2. Befunde mit Adresse, Datensatz, reproduzierbarem Befehl oder bereinigtem Beobachtungsprotokoll belegen.
3. Kennzeichnen: statisch belegt, Laufzeit beobachtet, abgeleitet oder offen.
4. Keine MAC-Adressen, privaten IP-Adressen, WLAN-Namen/-Schlüssel, persönlichen Dateien oder vollständigen Geräteberichte veröffentlichen.
5. Keine Flash-Empfehlung allein aus korrekten CRC-/MD5-Werten ableiten. Loader-Struktur und Hardwarezustand sind eigene Prüfebenen.
6. Vor einem Pull Request die Tests und `python3 tools/publication_check.py` ausführen.

Die Webübersicht unter `site/` enthält bewusst nur Menü-Auszüge und eigene Beschreibungen. Vollständige extrahierte Ressourcen gehören in den ignorierten Ordner `private/`.
