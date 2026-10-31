# Update-Container und Loader

## Statisch überprüft

- 124-Byte-ISU-Header; Bytes 108–123 entsprechen MD5 über alle Bytes ab Offset 124.
- Eingebetteter `enco`-Container mit 20-Byte-Blocktabelleneinträgen: ID, kodierte Position, komprimierte Größe, Folge-ID und entpackte Größe.
- Komprimierter Block beginnt mit Marker `0x63`; danach Frontier-MSB-first-DEFLATE. Zwei folgende Bytes enthalten CRC-16/GENIBUS über den komprimierten Strom ohne Marker.
- Numerische Bitdarstellung lässt sich in RFC-1951-DEFLATE transkodieren und mit Standardbibliotheks-zlib unabhängig entpacken.
- Die IDs und Folge-IDs bilden einen Verkettungsgraphen. Sie sind nicht als kumulative entpackte Bytepositionen nachgewiesen.

## Loader-Kommandos

Die beobachteten Befehle enthalten Modulnamen, initialisierte Ladebytes, Füllbereiche und Konfigurationsdatensätze. Alle 359 Originalblöcke lassen sich einzeln in vollständige Kommandos zerlegen. Ein global korrekt zusammengesetztes Speicherbild reicht als Prüfung daher nicht aus: Auch Blockgrenzen müssen erhalten bleiben.

## Web-Upload

Die untersuchte lokale Upload-Route akzeptierte eine Hülle aus XML-Metadaten, zwei Nullbytes und vollständigem ISU. Darin stehen unter anderem Version, Customisation, Größe und MD5 des vollständigen ISU. Diese Prüfsumme ist von der MD5 im ISU-Header zu unterscheiden.

Frühere Varianten mit anderem Header wurden abgewiesen; der beobachtete Fehler lautete „File check failed! Please select another binary.“ Nach korrekter Verpackung wurde eine kleine Textänderung im Versuch als wirksam gemeldet. Das ist keine allgemeine Garantie für weitere Modifikationen.

Dieses öffentliche Paket enthält bewusst keinen Firmware-Builder oder Upload-Client. Checksummen sind Konsistenzprüfungen, kein Beleg für Bootfähigkeit oder das Fehlen weiterer Akzeptanzprüfungen.
