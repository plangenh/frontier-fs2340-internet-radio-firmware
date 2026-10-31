# Statically reconstructed menus

The public [data file](../site/data/menus.json) contains 39 list forms, 102 declared entries, and 95 statically resolved labels. Six entries have dynamic text IDs; one further entry is not fully present in initialized data. This is a structural reconstruction, not original source code. Original English and German labels are retained verbatim as evidence.

## Main menu

Descriptor `0x32aefa00`; entries at `0x32af08a0`:

1. Internet radio
2. Podcasts
3. Spotify
4. Music player
5. DAB
6. FM
7. Bluetooth
8. AUX in
9. Sleep
10. Alarms
11. Timer
12. System settings

## System settings

Descriptor `0x32aef9c0`; entries at `0x32af07d8`:

Equaliser; Streaming audio quality; Network; Time/Date; Language; Factory reset; Software update; Setup wizard; Info; Backlight.

## Structural pattern

64-byte list descriptors have matching geometry (x=0, y=40, width=320, height=200), title IDs, and 20-byte item records. Text references carry tag `0x000f`, with the ID in the high halfword. A shared callback `0xb20cbbd4` combined with an argument pointing to another descriptor is a strong submenu candidate; runtime dispatch was not revalidated in this pass.

Internet radio (`0x32af28cc`) and Podcasts (`0x32af290c`) each contain Last listened, Station/Podcast list, System settings, and Main menu. Backlight points to Timeout, On level, and Dim level. Brightness lists contain High, Medium, and Low.

## Limitations

Time/Date, Language, Music player, and other lists contain no static rows in this format. That indicates dynamic construction, not an empty live menu. The Network structure has six statically readable rows and one unresolved row. The main-menu table must also be distinguished from the eight source records used by the icon carousel.

Not every table must be visible on a Touro. Runtime station, episode, and network lists are not represented as complete static firmware entries.
