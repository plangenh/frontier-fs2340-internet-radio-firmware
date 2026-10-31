# Source dispatch and saved settings

Offline continuation of the [dynamic menu investigation](feature-visibility.md), using the same documented original SHA-256. These are static instruction/data findings, not observed hardware transitions. No firmware bytes or device settings were changed.

## 1. Source-change events reach a registered consumer

The source-selection producer at execution PC `0xb2094994` posts event `0x901` with the requested mode as argument. The shared post path writes a queued record with a zero field at +16, event ID at +20, and argument at +24.

The receive/dispatch loop uses the record's +20 address as the event payload. It visits callback slots and can consult per-slot filters. Main UI initialization registers the callback record at load address `0x32aeec18` in slot 7 of the registry at `0x32b125b8`. Its first word points to handler `0xb2095140`; its second word is a replacement/cleanup callback.

Slot 7 is a callback registry index, not a source number or demonstrated event-class identifier. Earlier subscribers or filters may consume an event; the trace does not claim arbitrary injected events always reach this handler.

The handler explicitly compares the payload ID against `0x901` and enters case `0xb2096754`. It reads the requested mode from payload +4 and calls `0xb2094d04`.

```mermaid
flowchart LR
    A[Source selection] --> B[Event 0x901 and requested mode]
    B --> C[Queue and callback dispatch]
    C --> D[Registered main UI handler]
    D --> E[Mode transition]
    E --> F[Matching source record]
    F --> G[Mode entry callback]
```

This closes the earlier gap between the source-selection producer and consumer.

## 2. The icon table also registers source-entry behavior

The transition path stores the requested mode in the runtime configuration object, then uses the source lookup at `0xb20933c4`. On the ordinary matched-record path, `0xb20944b8` reads the entry callback at record +16 and arguments at +20/+24, then performs an indirect call at `0xb2094664`.

The eight 28-byte records beginning at load `0x32aeea8c` therefore describe both source icons and actual source-entry functions:

| Mode | Source | Entry callback | First argument |
|---:|---|---|---:|
| 1 | Internet radio | `0xb209d1b0` | 1 |
| 2 | Podcasts | `0xb209d1b0` | 2 |
| 3 | Spotify | `0xb20bd0f8` | 0 |
| 4 | Music player | `0xb209d1b0` | 13 |
| 5 | DAB | `0xb20937c8` | 0 |
| 6 | FM | `0xb20937a8` | 0 |
| 7 | Bluetooth | `0xb20e68c8` | 1 |
| 8 | AUX | `0xb20e50a0` | 0 |

The second argument is `0xffffffff` in all eight records. Internet radio, Podcasts, and Music player share a common media entry routine while passing different context arguments. The other sources enter separate routines.

The lookup scans eight records and returns null if no match exists; the ordinary entry path checks for null before calling a record. However, the inspected earlier transition function has no general range check before updating mode state. This is not a safe public mode-setting API, and arbitrary mode values are not an established feature-unlock mechanism. Special state branches and the backend's own eligibility checks remain separate questions.

## 3. Fifteen media contexts are not fifteen enabled sources

The common media path references fifteen 52-byte context records beginning at load `0x32af0ebc`. A lookup compares each record's context ID at +48. This is a second namespace, distinct from the eight top-level source modes.

| Table indices | Context IDs | Associated menu |
|---|---|---|
| 0 | 0 | Internet radio |
| 1 | 1 | Podcasts |
| 2–11 | 2–11 | Main menu |
| 12 | 14 | Music player |
| 13 | 12 | Music player |
| 14 | 13 | Music player |

The exact service/backend meaning of the remaining IDs is unresolved. Some entries share generic callbacks and point back to Main menu. Their presence does not prove that additional streaming services can be enabled by changing a bit.

## 4. Language selection changes the actual lookup root

The same UI handler recognizes language event `0x103` and branches to `0xb2095a8c`. It writes the selected language to runtime configuration byte 13, at load `0x32aeed8d`, marks settings for deferred saving, and invokes locale setter `0xb20eb9e0`.

For an index in 0–14, the setter reads the corresponding pointer from locale roots `0x32b12b58` and writes the active locale root at `0x32b12b54`. Normal translation lookup reads that active root. This is an actual table-selection path, not just a visual selection marker.

The handler also refreshes translated source-label caches and submits follow-up event `0x104`. All effects of that event and another notification call remain untraced. The valid menu supplies indices 0–14; behavior for arbitrary externally injected arguments was not tested.

## 5. Settings use a separate record-based storage representation

Language changes write 100 to a pending-save word at load `0x32aeeb78`. The handler for event `0x100` decrements it. When the countdown reaches zero, two predicate checks must both return zero before entering the save path.

The value 100 is an observed dispatch countdown. Its duration in seconds, failure handling, and power-loss behavior are not established.

Runtime configuration at `0x32aeed80` is compared with a separate serialized settings object at `0x32aeedf4`:

| Setting | Runtime representation | Serialized representation |
|---|---|---|
| Automatic time-update source | byte +12 | dword +20 |
| Language index | byte +13 | byte +41 |

Changed settings pass through wrapper `0xb20978fc` and record identifier `0x2e`, using backing-store object `0xb2ce0160`. The call chain reaches record-write and store-finalization APIs. The physical flash backend and record location remain unresolved; these RAM addresses and field offsets must not be treated as SPI flash offsets.

Startup function `0xb209850c` loads the same record and copies those fields back into runtime state. Its fallback initializer sets **Network time updates (4)** and **English (0)**. These are fallback-path defaults, not measured settings of the actual device: an existing saved record may override them.

This explains why changing an initially zero-filled runtime byte is not sufficient to establish the setting the device will use after startup.

## Next boundaries

- Trace backend mode registration and service eligibility beyond the source-entry callbacks.
- Identify the nonvolatile store format, integrity checks, and physical layout of record `0x2e`.
- Resolve save predicates, countdown scheduling, and event `0x104` behavior.
- Map further media-context fields without conflating context IDs and source IDs.

The private evidence bundle contains focused instruction excerpts, original table records, and reproducible collectors for event transport, source dispatch, and settings persistence. This public document provides original research prose and technical addresses; raw executable excerpts and device-specific data are not distributed here. No tested feature-unlock patch, custom firmware release, or completed recovery follows from this analysis.

## Storage follow-up

A later pass identifies a configured settings window and object-schema checks, plus lower-layer checksum use. See [settings storage](storage-layout.md). The actual record position, checksum algorithm, and hardware dump still remain unresolved.
