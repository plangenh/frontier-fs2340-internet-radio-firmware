# Fehlgeschlagenes Update und Recovery-Stand

Ein experimentelles Update mit ausgetauschten Podcast-Grafiken wurde über das Web-UI installiert. Danach blieb das Gerät bei „Welcome to Internet Radio“ hängen und war nicht im Netzwerk erreichbar. Vollständiges Trennen vom Strom behob dies nicht. Ein früherer kleiner Textänderungsversuch war als erfolgreich gemeldet worden; für die blaue WLAN-Variante liegt kein gesonderter eindeutiger Laufzeitnachweis vor.

## Konkreter Fehler im experimentellen Builder

- Original: 359 von 359 entpackten Blöcken enthalten vollständige Loader-Kommandos.
- Blaue WLAN-Basis: ebenfalls 359 von 359.
- Fehlerhafte Bildvariante: nur 246 von 359; 113 Blöcke verletzen die Eigenschaft.
- Der erste betroffene Block `0x67400` enthält einen Befehl, der 52 Bytes über sein Ende hinausreicht.

Der Builder wandelte Füllbefehle in größere Ladebefehle um und schnitt anschließend den vergrößerten Strom an alten Bytegrenzen. Seine Prüfung fügte die Blöcke vor dem Nachbilden der Speicherzugriffe zusammen und übersah den Fehler. CRC und MD5 blieben trotzdem konsistent.

**Das ist ein konkreter Builder-Defekt und ein starker Kandidat für den Startfehler.** Ob der reale Bootloader genau deshalb scheitert, ist ohne dessen nachgewiesenen Blocklesepfad nicht abschließend belegt. Eine spätere Schutzprüfung weist solche Grenzverletzungen zurück; daraus folgt noch kein verifiziertes repariertes Update.

## Geplante Wiederherstellung, noch nicht durchgeführt

Auf der fotografierten Platine ist ein cFeon/EON EN25QH64A-104HIP identifiziert: 64 Mbit / 8 MiB, nominal 3,3 V. Hardware-Revisionen können abweichen; vor Arbeiten den tatsächlichen Chip prüfen.

Ein externer SPI-Programmer könnte zunächst mehrere identische Komplettlesungen erstellen. Anschließend müssen Flash-Aufteilung, Bootloader, Konfiguration und gerätespezifische Bereiche ermittelt werden. Erst daraus kann ein passendes Reparaturabbild entstehen. Der Zugriff auf den eingelöteten Chip ist nicht garantiert; möglicherweise ist Auslöten nötig.

**Eine ISU-Update-Datei ist kein vollständiger Flash-Dump. Sie darf nicht als komplettes Speicherabbild behandelt werden.** Aktuell gibt es in diesem Projekt keinen bestätigten Wiederherstellungsablauf und keinen erfolgreichen Recovery-Test.
