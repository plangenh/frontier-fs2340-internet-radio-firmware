# Findings and evidence

Examined original: `ir-cui-FS2340-0000-0444_V4.10.18.281972.EX11_10-1A8.isu.bin`

SHA-256: `48a9da85d2580ee7fffde0f204ee2046ae0e300a2f23f1e4a6a5e3b299bd0dc3`  
Size: 4,136,167 bytes.

| Finding | Evidence | Limitations |
|---|---|---|
| 359 compressed blocks with matching CRC-16 and decoded sizes | Offline parser; internal comparison against a second decoder | Specific to this artifact |
| 15 tables of 1,056 resources each | Pointer resolution and repeated byte-level verification of all 15,840 strings | Language identity inferred from text |
| 39 list forms / 102 entries / 96 static labels | Shared 64-byte structure, 20-byte entries, valid IDs | Six dynamic labels remain; see the later callback investigation |
| 65 graphic records | Contiguous range and internal byte-identical PNG round trips | Original graphics are not distributed |
| Podcasts uses images 42–44 | Static instruction analysis of lookup, variant selection, and renderer | No newly observed runtime test |
| Experimental image update violated block boundaries | Comparison of original and modified artifacts; 113 problematic blocks | Actual bootloader control flow remains unresolved |

## Address conventions

Data addresses use the load view, such as `0x32aeea8c`. Code and other pointers may use the alias with the highest bit set, such as `0xb2aeea8c`. Masking this bit is supported for the examined data accesses; it is not a general substitute for correctly mapping MinIM execution addresses.

## Not established

- Complete dynamic menu hierarchy or availability of all platform features.
- Absence of additional cryptographic checks.
- A generally installable custom UI or recovery compatibility beyond the one owner-confirmed restored device.
- A general recovery key combination, USB recovery method, or verified debug pinout.

Underlying raw data remains private. Curated tables and reproducible tools support the documented findings, but do not constitute a complete public disassembler project.
