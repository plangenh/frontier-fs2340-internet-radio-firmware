# Ordinary local-update payload mapping

This investigation traces a specific buffered web-upload path to its Flash-write adapter. It does not reconstruct every update mode or the complete bootloader. No firmware was installed and no physical Flash dump was inspected.

## Concrete path

The upload continuation at execution PC `0xb20fd9e4` reaches `0xb20906f4`, which creates a worker at `0xb2090dbc`. That worker invokes the payload writer `0xb2090ba0`.

The writer copies the 124-byte ISU header locally, reads its payload-offset field, skips that many source bytes, subtracts it from the expected binary size, and starts the destination at **`0x12000`**. It advances the source and destination by each chunk's length.

Calls through `0xb21705bc`, `0xb21705ac`, and `0xb217059c` resolve to the same erase, program, and finalize adapters identified in the settings-store investigation. Programming uses 256-byte pages and erase management uses 4 KiB sectors.

## Original-file address mapping

For the documented original:

| Property | Value |
|---|---|
| Complete ISU size | 4,136,167 bytes |
| Skipped header | 124 bytes |
| Copied payload size | 4,136,043 bytes / `0x3F1C6B` |
| Configured payload destination | `0x12000` to exclusive `0x403C6B` |
| `enco` marker in that destination | `0x12080` |
| Separate configured settings window | `0x7A1000` to exclusive `0x7FF000` |

The outer XML envelope and the ISU header are not copied as part of this payload loop.

An independent check of **all 359 original compressed-block records** confirms that each table's encoded block position equals:

```text
0x12000 + block_offset_in_ISU_file - 124
```

This gives a direct connection between the container and the configured Flash destination. It concerns the block-position field, not the block ID or next-ID fields. Module RAM load addresses must still not be treated as physical Flash offsets.

## Important limits

The writer first calls a helper through `0xb216fd8c` into unavailable code at `0x80915ad0`. Its side effects are unresolved. Boot/commit flags, active-image selection, subsequent boot decompression, and other possible update side effects have not been reconstructed.

The observed original payload-copy range does not overlap the configured settings window. That does not prove that an entire update preserves every configuration byte, or that replacing only those payload bytes is sufficient recovery.

Areas before `0x12000`, between the original payload end and settings window, and the final 4 KiB of an 8 MiB chip remain unclassified. They are not established as unused or safe to erase. Different compressed variants may have different payload end addresses.

## Compare a future dump without modifying it

```sh
python3 tools/compare_update_to_dump.py private/full-chip.bin private/original.isu.bin \
  --layout fs2340-touro-v4.10.18 \
  --output private/update-comparison.json
```

The tool requires an 8 MiB dump and the documented version/customization. It checks the outer ISU header, payload MD5, expected `enco` position, and window bounds, then reports exact payload equality or differing byte ranges. The binary inputs remain unchanged; only a new JSON report is written.

An exact match does not prove bootability, current-image selection, or valid boot metadata. A mismatch does not by itself identify corruption: the device may contain another variant. The tool does not check every block CRC, emulate the loader, create a repair image, or write Flash.

Tests cover exact matches, bounded differences, unchanged inputs, and malformed outer headers/checksums. The original file was also compared with an explicitly synthetic buffer containing its own payload. **No real hardware dump has been validated yet.**

## Recovery consequence

A later verified dump can now be compared against the original and the experimental update at a concrete, independently cross-checked location. We still need actual contents, the boot/commit path, and other device-specific regions before preparing any write operation.
