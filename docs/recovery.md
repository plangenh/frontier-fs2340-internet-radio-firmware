# Failed update and recovery status

An experimental update with replaced Podcast graphics was installed through the web UI. The device then stalled at “Welcome to Internet Radio” and became unreachable on the network. Fully disconnecting power did not resolve it. An earlier small text-change experiment was reported successful; the blue Wi-Fi variant has no separate unambiguous runtime confirmation.

## Concrete defect in the experimental builder

- Original: all 359 decoded blocks contain complete loader commands.
- Blue Wi-Fi base: also 359 of 359.
- Failed image variant: only 246 of 359; 113 blocks violate that property.
- The first affected block, `0x67400`, contains a command extending 52 bytes beyond its end.

The builder converted fill commands into larger load commands, then sliced the expanded stream at old byte boundaries. Its memory-replay check concatenated blocks first, masking the defect. CRC and MD5 values nevertheless remained consistent.

**This is a concrete builder defect and a strong candidate explanation for the startup failure.** Whether the real bootloader fails for exactly this reason remains unproven without its block-reading control flow. A later guard rejects these boundary violations; that does not establish a verified repaired update.

## Planned recovery: not yet performed

The photographed board has an identified cFeon/EON EN25QH64A-104HIP: 64 Mbit / 8 MiB, nominally 3.3 V. Hardware revisions may differ; verify the actual chip before working on a device.

An external SPI programmer could first obtain multiple identical full-chip reads. Flash layout, bootloader, configuration, and device-specific regions must then be identified before constructing a suitable repair image. In-circuit access is not guaranteed; desoldering may be necessary.

**An ISU update file is not a complete flash dump and must not be treated as one.** This project currently has no confirmed recovery procedure or successful recovery test.

## Settings-storage follow-up

A later static trace identifies settings record `0x2e` and separate runtime/serialized fields for language and time-update source. Its physical flash location is still unresolved. This strengthens the need to preserve configuration during recovery, without providing a ready-to-write flash map. See [the settings investigation](source-dispatch-and-settings.md).
