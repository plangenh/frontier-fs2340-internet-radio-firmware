# Input controls and context-dependent actions

Scope: static analysis of `ir-cui-FS2340-0000-0444_V4.10.18.281972.EX11_10-1A8`, SHA-256 `48a9da85d2580ee7fffde0f204ee2046ae0e300a2f23f1e4a6a5e3b299bd0dc3`. This is not a hardware input capture.

The [official Touro manual](https://majorityaudio.com/wp-content/uploads/2026/02/Touro-Manual-Collection-2026-1.pdf) identifies nine front controls, including the rotary push control, and a rear power switch. The firmware independently contains nine local key mappings plus a separate rotary path. Physical names below are corroborated by that manual; they are not labels stored in the key table.

## Local key map

The nine records at load address `0x32b4ed8c` contain four little-endian 16-bit fields: driver code, logical index, hold parameter and repeat parameter. The final two fields are 1050 and 1000 in every local record. Their time unit has not been established.

| Driver code | Logical key | Corroborated control | Statically traced action |
|---|---|---|---|
| 1 | `0x203` | BACK | Return to parent menu |
| 2 | `0x22b` | FAV | Short click opens preset recall; hold opens preset storage |
| 3 | `0x201` | MENU/INFO | Hold enters a menu in a source-specific handler; menu handler also uses this key for parent/root navigation |
| 4 | `0x211` | Standby/Mode | Short click opens source carousel; hold reaches power-state transition code |
| 5 | `0x202` | Rotary push / OK | Invoke the selected menu row callback |
| 9 | `0x21b` | Sleep/Snooze | Press reaches sleep timer UI |
| 10 | `0x20e` | Alarm | Press reaches alarm UI |
| 11 | `0x206` | Tuning pair, first member | Menu movement −1; repeat supported |
| 12 | `0x207` | Tuning pair, second member | Menu movement +1; repeat supported |

Driver codes are not GPIO numbers or manual diagram reference numbers. The exact physical plus/minus orientation of the last two records is not independently established here. Source-specific tuning, seeking and alarm-time overrides need separate traces or hardware validation.

## Event representation

Adapter `0xb20eaaec` packs events as:

```text
event = (phase << 24) | ((logical_index + 0x200) & 0xffff)
argument = separate 16-bit word
```

The decoder at `0xb20f3f18`, together with its hold timer at `0xb20f3c10`, distinguishes:

| Phase | Interpretation from control flow |
|---|---|
| 1 | Initial press |
| 2 | Release notification |
| 3 | Held-key repetition |
| 4 | First hold notification |
| 5 | Release after a hold |
| 6 | Release without a hold: short click |

A short click and an initial press are different events. For example, FAV recall uses `0x0600022b`, whereas storage uses `0x0400022b`. Applications must not treat every release as another press.

The rotary path at `0xb20f4448` emits logical index 42, hence `0x0100022a`, carrying the negated lower-driver delta. Consumers sign-extend its 16-bit argument. Clockwise polarity still requires validation.

## Action evidence anchors

Addresses are execution PCs, not file offsets.

| Consumer | Evidence |
|---|---|
| Menu movement `0xb20cb050` | Keys `0x206`/`0x207`, phases 1 and 3, call movement helper `0xb20ca958` with −1/+1. Rotary supplies variable movement. |
| Menu dispatch `0xb20cbc6c` | Key `0x202` phase 1 selects a row; `0xb20cbea4` indexes 20-byte row descriptors and invokes callback +12 with argument +16. |
| Parent menu `0xb20cbe24` | Calls `0xb20cbb74`, which follows the parent descriptor. |
| Source selection `0xb2095904` | Calls carousel entry `0xb20ea2f0`; carousel has a rotary consumer and eight source positions. |
| Power transition `0xb2095d18` | Calls `0xb209474c`; interpreting every power-state bit remains incomplete. |
| Preset recall `0xb20e4aa8` | Uses resource IDs 116/117 and opens preset UI. |
| Preset storage `0xb20e4d90` | Uses resource IDs 118/119 and opens preset UI. |
| Sleep `0xb2095d08` | Calls `0xb20ce678`. |
| Alarm `0xb2095cf8` | Calls `0xb20d1f34`. |
| Volume `0xb2095c98` | Rotary argument reaches `0xb20939d8`; setter `0xb209381c` clamps to 0–32 and updates audio plus overlay. |

## Context and additional inputs

Input filters and active screen handlers can consume an event before the global handler sees it. Rotation can therefore move a menu selection or change volume, depending on the active screen. Rotary push is not established as a universal play/pause command.

A second decoder branch uses 31 records at `0x32b4ec94`. It includes digit and dedicated volume/mute-style logical inputs absent from the local nine-key table. This resembles support for an additional remote input path; it does not prove that this device has an IR receiver or physical volume/mute buttons.

The rear power switch is documented by the manufacturer; no mapping from that switch to the local event table was established. GPIO assignments, electrical wiring, exact hold timing, all source-specific overrides and runtime behavior remain unverified.

## Implications for the display prototype

Use the rotary control for selection and contextual volume; use its press for confirmation. Provide BACK navigation and source selection through Standby/Mode. FAV offers recall and storage. Do not assume dedicated volume keys, a touchscreen, or a universal pause button. These are constraints for the next prototype revision, not changes already installed on a radio.
