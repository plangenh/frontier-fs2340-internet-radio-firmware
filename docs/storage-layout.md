# Settings storage: configured flash window and object format

This offline pass follows the settings store down to its read/write/erase adapters. No flash chip was accessed, and no recovery image was created. Findings are specific to the documented original firmware.

## Configured storage window

Initialization at execution PC `0xb2002a74` configures the store object at load address `0x32ce0160` with byte-address base `0x7a1000`, length `0x5e000`, and erase-sector base `0x7a1`.

| Range / property | Value | Evidence boundary |
|---|---|---|
| Settings-store address window | `0x7A1000` to exclusive `0x7FF000` | Static initialization and adapter arithmetic |
| Window length | 385,024 bytes / 376 KiB | 94 × 4 KiB |
| Erase group size | 4,096 bytes | Group arithmetic and erase address shift |
| Program page size | 256 bytes | Driver splits writes at page boundaries |
| Final 4 KiB of an 8 MiB chip | `0x7FF000`–`0x800000` | Not classified by this investigation |
| Everything below the settings window | Not mapped in this pass | Must not be assumed to be one replaceable application image |

The read adapter (`0xb202e944`) and write adapter (`0xb202ec68`) check relative offsets against the configured length, add the byte base, then invoke the store callbacks. The erase adapter adds the sector base before calling its callback. Driver transaction construction uses opcode `0x20` with a 12-bit sector shift for erase, `0x02` for page programming, and `0x0b` for reads.

This is a strong statically configured SPI-address window to inspect in a full dump. The call to `0x8090f964` was initially treated as an unavailable final transaction boundary. A [later `_lib0` decoding](boot-validation-and-splash.md) identifies it as a 24-bit big-endian address serializer. Actual bus dispatch is a separate path; this is not a complete flash partition map.

## Record key, object schema, and physical location are different

The settings record uses key `0x2e`, but its object tag is **3**. The initialized object at RAM load address `0x32aeedf4` has this schema:

| Object offset | Width | Expected value / meaning |
|---:|---:|---|
| +0 | 4 | Tag 3 |
| +4 | 1 | Header length 12 |
| +5 | 1 | Schema version 1 |
| +6 | 2 | Flags; bit zero requests optional encryption |
| +8 | 4 | Total object size 292 bytes |
| +12 | 280 | Settings payload |
| +20 | 4 | Time-update source, including the header in the offset |
| +41 | 1 | Language index, including the header in the offset |

The load path compares header length, tag, version, and total size against the expected initialized object. Mismatches are rejected and can lead to the caller's fallback-default path. This is not demonstrated automatic schema migration.

The examined initialized settings object has flags zero, so its ordinary save path does not request encryption at the object layer. The generic layer also supports optional encryption/decryption, corroborated by diagnostic names and transform calls. This does not establish the cipher, authentication properties, or absence of protection elsewhere.

## Integrity also exists below the schema

The lower record-storage layer calculates a 16-bit checksum using seed `0xffff`. On read, it checks the reconstructed record against its index metadata. Group-header creation also checksums the first ten bytes of a twelve-byte header.

The checksum wrapper (`0xb20b8374`) jumps to `0x8090f778`, now [recovered from `_lib0`](boot-validation-and-splash.md). Its nibble table establishes the non-reflected CCITT polynomial `0x1021`. End-to-end stored-record checksum conventions still require validation against physical records; the inspection tool below does not perform that validation.

Record reads can assemble multiple fragments, and writes update group/index metadata and use rollover paths. The exact current record location and active-generation selection remain unresolved. **Record key `0x2e` is not a stable flash offset.** A matching object header is not sufficient to identify a live, valid settings record.

## Read-only preparation for a future dump

The optional tool below requires a caller-supplied **8 MiB full-chip dump**, not an ISU update:

```sh
python3 tools/inspect_flash_dump.py private/full-chip.bin \
  --layout fs2340-touro-v4.10.18 \
  --output private/flash-inspection.json
```

It reports a hash, erased-sector counts in the configured window, and unverified contiguous object-header candidates. For complete, unencrypted candidates within one sector, it reports only the two documented scalar fields. It does not expose arbitrary strings or credentials.

It does **not** verify record checksums, reconstruct fragments, decrypt objects, select current generations, or write to the dump. Cross-sector, encrypted, and truncated candidates are explicitly not decoded. Inputs for other models or versions are not automatically recognized. Keep dumps and inspection reports private.

Synthetic tests cover wrong input size, the configured search boundary, false/unverified candidate semantics, input preservation, and encrypted/cross-sector/truncated cases. No actual hardware dump has been tested yet.

## Recovery implications

The settings region is a concrete area to preserve and examine when a verified dump becomes available. It does not tell us which bytes to overwrite to repair the application. Bootloader/application boundaries, any other device-specific regions, record-generation rules, and checksum details still need to be understood before constructing a repair image.
