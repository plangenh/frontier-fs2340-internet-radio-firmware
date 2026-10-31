# Display und Grafikressourcen

Drei Deskriptoren bei `0x32b722d4` enthalten 320 × 240 Pixel und aufeinanderfolgende Puffer von je 153.600 Bytes. Ein deklarierter Nullfüllbereich deckt zusammen 460.800 Bytes ab. Das stützt drei 16-Bit-Pixelpuffer; deren genaue Front-/Back-/Scratch-Rollen sind offen.

Der lückenlose Grafikbereich `0x32b4ee5c` bis exklusiv `0x32b6f5e8` enthält 65 Datensätze:

1. Ein Headerbyte (hier jeweils null; Bedeutung offen).
2. Breite und Höhe als je ein Byte.
3. 16 Big-Endian-RGB565-Farben, zusammen 32 Bytes.
4. 4-bpp-Pixelindizes, hohes Nibble zuerst; jede Zeile hat `ceil(Breite / 2)` Bytes.

Datensatzgröße: `35 + ceil(Breite / 2) × Höhe`. Bei ungerader Breite muss das ungenutzte Zeilennibble erhalten bleiben. Palette null wurde bei der lokalen Vorschau als Schwarz dargestellt; Transparenz ist dadurch nicht nachgewiesen.

## Quellen-Symbole

Acht 28-Byte-Quellendatensätze beginnen bei `0x32aeea8c`; die Lookup-Routine liegt bei Ausführungs-PC `0xb20933c4`.

| Quelle | Modus | Basis-Bildindex |
|---|---:|---:|
| Internetradio | 1 | 39 |
| Podcasts | 2 | 42 |
| Spotify | 3 | 45 |
| Musikabspieler | 4 | 48 |
| DAB | 5 | 51 |
| UKW | 6 | 54 |
| Bluetooth | 7 | 60 |
| AUX | 8 | 57 |

Podcast-Datensatz: `0x32aeeaa8`. Bild 42 bei `0x32b59955` ist 79 × 72, Bild 43 bei `0x32b5a4b8` ebenfalls 79 × 72 und Bild 44 bei `0x32b5b01b` 110 × 110 Pixel. Statische Variantenwahl addiert für den selektierten Popup-Zustand eins und für die fokussierte Karussellmitte zwei zum Basisindex.

Das Formatverständnis erlaubt lokale Analysen. Es beweist keine sichere Installation neu kodierter Ressourcen.
