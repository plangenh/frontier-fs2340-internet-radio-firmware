# Feature visibility and dynamic menus

This offline pass follows menu callbacks and source-selection code in the documented original. It executes no firmware and provides no feature-unlock patch.

## A confirmed Time/Date visibility rule

The builder at execution PC `0xb20989e8` includes Set Time/Date, Auto update, and Set format. It adds Set timezone and Daylight savings only when the automatic update source is **Network (value 4)**. The label callback (`0xb2099264`), selection handler (`0xb209ada8`), and source setter (`0xb20994fc`) corroborate this mapping. Other source values in the static choice table are DAB=1, FM=2, None=0.

The controlling byte is at load address `0x32aeed8c`, in a runtime state object beginning at `0x32aeed80`. It is initially zero-filled; this is not proof of a persisted default or a writable flash configuration offset.

## Language is a dynamic list

The language count callback returns 15. Names come directly from the locale roots at `0x32b12b58`. State byte 13, at `0x32aeed8d`, selects the current entry and is clamped to 0–14. Activation submits event `0x103`; the receiving handler and persistence remain unresolved.

Generic dynamic descriptor roles are now traced: offset +32 supplies count/population, +36 labels, +40 activation, and +48 current selection. These roles apply to the traced dynamic list family, not every descriptor in the firmware. The shared submenu callback saves the parent and enters the child descriptor, strengthening links that were previously identified only from pointer structure.

## Eight sources, no demonstrated general unlock switch

The source carousel uses bytes `00 01 02 03 04 05 06 07` at load address `0x32b122cc`. The inspected update loop wraps indices at eight, reads this array, adds one, and looks up the mode. Those modes are Internet radio, Podcasts, Spotify, Music player, DAB, FM, Bluetooth, and AUX.

No availability predicate appears in that inspected loop. This does not prove that other code cannot rewrite its state or that every backend service works on every device. Source-transition helper `0xb20949b8` dispatches event `0x901`; its consumer is a stronger next target than assuming arbitrary extra service strings can be enabled.

## Flags must not be mistaken for capabilities

In the examined draw path, item flag `0x100` adds bit `0x2` to rendering/output flags without skipping the row. Its precise visual meaning remains unresolved. Item bit zero selects a direct text pointer versus a localized text-ID lookup. Per-mode bitfields initially considered as capability candidates are used in repeat/shuffle action contexts; they are not established feature switches.

## Color themes remain unresolved

Text IDs 808–812 exist. A bounded search of four-byte-aligned initialized main-module data found no packed-ID references. English string-pointer hits correspond to localization table slots. This does not prove absence: dynamically constructed references or other encodings are outside that search.

## Inventory correction

The original extractor overlooked the first Network row because its four-byte flags field was zero-filled, immediately followed by initialized label/callback bytes. Joining both kinds of memory resolves **Network wizard (ID 317)** at row `0x32afd42c`. All seven Network rows are statically readable.

The corrected inventory is **39 forms, 102 declared rows, 96 statically resolved labels, and six dynamic labels**. Existing table addresses and row counts did not change. The extractor now reads declared zero-fill regions and has a synthetic regression test covering this boundary.

## Remaining questions

- Backend registration and eligibility checks behind source-change event `0x901`.
- Preference load/save and the receiving side of language event `0x103`.
- Dynamic Equalizer and alarm population.
- Executable references that could establish actual color-theme behavior.

These findings do not establish a safely installable customization or a completed recovery.

## Follow-up

The next pass found the consumers of events `0x901` and `0x103`, source-entry callbacks, and the record-based settings load/save path. See [source dispatch and saved settings](source-dispatch-and-settings.md) for what is now resolved and what remains open.
