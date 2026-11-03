# Failed update and recovery status

An experimental update with replaced Podcast graphics was installed through the web UI. The device then stalled at “Welcome to Internet Radio” and became unreachable on the network. Fully disconnecting power did not resolve it. An earlier small text-change experiment was reported successful; the blue Wi-Fi variant has no separate unambiguous runtime confirmation.

## Concrete defect in the experimental builder

- Original: all 359 decoded blocks contain complete loader commands.
- Blue Wi-Fi base: also 359 of 359.
- Failed image variant: only 246 of 359; 113 blocks violate that property.
- The first affected block, `0x67400`, contains a command extending 52 bytes beyond its end.

The builder converted fill commands into larger load commands, then sliced the expanded stream at old byte boundaries. Its memory-replay check concatenated blocks first, masking the defect. CRC and MD5 values nevertheless remained consistent.

**This is a concrete builder defect.** The later [physical bootloader investigation](bootloader.md) confirms a block-oriented command parser whose first malformed block underflows its remaining-byte count by 52 bytes and continues parsing. This establishes the static failure mechanism; the exact execution that produced the observed startup hang was not recorded. A later guard rejects these boundary violations; that does not establish a verified repaired update.

## Physical readout: November 3, 2026

A closer photograph identifies the affected unit's chip as cFeon `QX64A-104HIP`, corresponding to the EN25QX64A family: 64 Mbit / 8 MiB, 2.7–3.6 V. This corrects the earlier QH identification. Hardware revisions may differ.

In-circuit attempts did not identify the chip. After desoldering and correcting contact, a Raspberry Pi Pico H running stacksmashing/pico-serprog returned JEDEC ID `1c 71 17`. Flashrom 1.8.0 detected an 8 MiB SFDP-capable chip rather than an exact named model.

Two separately acquired full-chip reads, at 1 MHz and 500 kHz, were byte-identical and nonconstant. Comparing the mapped payload window established an exact byte match to the retained failed graphics experiment. The original update differs in 1,252,480 bytes over its own payload window. These comparisons establish the stored payload, not the precise startup failure mechanism.

The raw reads and configuration inspection stay private. Matching reads plus the retained-artifact match strongly support correct acquisition; no hardware boot test has occurred.

**An ISU update file is not a complete flash dump and must not be treated as one.** This project currently has no confirmed recovery procedure or successful recovery test.

## Original-payload restoration: November 3, 2026

A private 8 MiB candidate was built from the matching physical reads. Only `[0x12000, 0x403c6b)` was replaced with the verified original ISU payload; the 124-byte ISU header was excluded. All bytes outside that interval were copied unchanged from the device backup. The original passed the independent structural checker with 359 blocks.

The candidate differed from the backup in 1,252,480 bytes across 309 4 KiB sectors. External programming used 500 kHz SPI and an explicit layout restricted to sectors `[0x12000, 0x404000)`. The final sector tail was retained from the backup. Flashrom reported successful programming and verification, and reported restoring the chip status register after temporarily disabling protection.

A separate full-chip read at 1 MHz then matched the candidate byte for byte. Offline comparison confirmed:

- The mapped payload equals the original update payload exactly.
- Every byte outside that payload interval is unchanged from the pre-write backup.
- The prefix before `0x12000`, configured settings window and final sector are preserved.

**This verifies external chip programming, not a successful radio boot.** The chip remains to be reinstalled and tested in the device. Complete boot/commit semantics remain unresolved. No public ready-to-flash image or general recovery guarantee is provided. Dumps, device configuration, private restore images and programmer logs are not distributed.

## Settings-storage follow-up

A later static trace identifies settings record `0x2e` and separate runtime/serialized fields for language and time-update source. Its physical flash location is still unresolved. This strengthens the need to preserve configuration during recovery, without providing a ready-to-write flash map. See [the settings investigation](source-dispatch-and-settings.md).

## Update-to-dump comparison

The ordinary local-upload payload destination is now statically mapped and cross-checked against all 359 original block locations. A [read-only comparison tool](update-flash-mapping.md) is available for a future verified full dump. This is not yet a repair image or proof that boot/commit metadata can be left unchanged.

## Check repeated reads before comparing firmware

Keep each independently acquired full-chip read as a separate, unchanged file. The documented chip size is 8 MiB. Once those files exist, this offline command checks repeatability and compares explicitly supplied update candidates:

```sh
python3 tools/check_recovery_reads.py private/read-1.bin private/read-2.bin \
  --layout fs2340-touro-v4.10.18 \
  --update private/original.isu.bin \
  --update private/experimental.isu.bin \
  --output private/recovery-read-report.json
```

The command never opens a programmer or writes Flash. It requires distinct read paths and creates a new report without overwriting inputs. Differing reads, or a read consisting entirely of one repeated byte, prevent candidate comparison. Such input needs investigation before drawing conclusions from its contents.

For repeatable nonconstant reads, each candidate is compared over its own [mapped payload window](update-flash-mapping.md). SHA-256 identifies candidates in the report without copying filenames or device data. Counts from different candidate lengths are not a ranking of which image is installed. An exact payload match identifies those bytes only; it does not validate loader commands, boot metadata, device-specific regions, or bootability.

Two matching files do not prove independent acquisition or electrically correct reading. A consistently incorrect read can also match. This tool establishes no readiness to erase or program the chip.

Validation covers mismatched reads, constant-byte reads, size/count bounds, and unchanged input buffers. Separate synthetic-only checks used the retained original, blue Wi-Fi experiment, and failed graphics experiment: each payload matched its own synthetic placement and differed from the other two. The November 3 physical reads now pass these checks; the installed graphics payload matches exactly.
