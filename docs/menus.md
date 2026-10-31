# Statisch rekonstruierte Menüs

Die öffentliche [Datendatei](../site/data/menus.json) enthält 39 Listenformulare, 102 deklarierte Einträge und 95 statisch aufgelöste Beschriftungen. Sechs Einträge haben dynamische Text-IDs, ein weiterer liegt nicht vollständig in den initialisierten Daten. Es handelt sich um eine strukturelle Rekonstruktion, nicht um das Original-Quellprogramm.

## Hauptmenü

Deskriptor `0x32aefa00`, Einträge bei `0x32af08a0`:

1. Internetradio
2. Podcasts
3. Spotify
4. Musikabspieler
5. DAB
6. FM
7. Bluetooth
8. AUX
9. Schlummer
10. Wecker
11. Timer
12. Systemeinstellungen

## Systemeinstellungen

Deskriptor `0x32aef9c0`, Einträge bei `0x32af07d8`:

Equalizer; Qualität Audiostream; Netzwerk; Zeit/Datum; Sprache; Werkseinstellung; Softwareupdate; Einrichtungsassistent; Info; Displaybeleuchtung.

## Strukturmuster

64-Byte-Listendeskriptoren mit passender Geometrie (x=0, y=40, Breite=320, Höhe=200), Titel-IDs und 20-Byte-Eintragsdatensätzen. Textreferenzen tragen das Tag `0x000f`, die ID steht im hohen Halbwort. Die Kombination aus gemeinsamem Callback `0xb20cbbd4` und Argument-Zeiger auf einen anderen Deskriptor ist ein starker Untermenü-Kandidat; dessen Laufzeit-Dispatch wurde in diesem Pass nicht erneut validiert.

Internetradio (`0x32af28cc`) und Podcasts (`0x32af290c`) enthalten je „Zuletzt angehört“, Sender-/Podcastliste, Systemeinstellungen und Hauptmenü. Displaybeleuchtung verweist auf Timeout, Betriebshelligkeit und gedimmte Helligkeit; die Helligkeitslisten enthalten Hell/Mittel/Dunkel.

## Grenzen

Zeit/Datum, Sprache, Musikabspieler und weitere Listen haben keine statischen Zeilen in diesem Format. Das bedeutet dynamischen Aufbau, nicht ein leeres Live-Menü. Die Netzwerkstruktur enthält sechs statisch lesbare Zeilen und eine offene. Die Menütabelle des Hauptmenüs ist außerdem von den acht Quellendatensätzen des Icon-Karussells zu unterscheiden.

Nicht alle Tabellen müssen beim Touro sichtbar sein. Laufzeit-Sender, Podcast-Episoden und Netzwerklisten werden nicht als statische Firmwareeinträge ausgegeben.
