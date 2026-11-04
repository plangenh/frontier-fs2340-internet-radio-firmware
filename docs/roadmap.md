# Roadmap: firmware personalization

Our goal is to enable owners of compatible radios to personalize selected display text, icons, and colors. The underlying resource formats are understood, but a reliably bootable, recoverable customization workflow is not yet available. There is no committed release date.

## Current foundation

- Version-specific container extraction and integrity checks.
- Language-table and menu-descriptor recovery.
- Bitmap record and palette format identification.
- Podcast icon lookup and variant mapping.
- A small text modification reported working on hardware.
- A documented packaging defect from an unsuccessful graphics experiment.
- Two matching physical backups, verified original-payload restoration, and owner-confirmed startup after chip reinstallation on November 4, 2026.

These are research milestones, not a general claim that modified firmware is safe to install.

## Milestone 1: recovery and a reliable baseline

**Achieved for the affected unit:** the owner reports that the radio works after the verified original-payload restoration and chip reinstallation. The preserved post-write image is the current recovery baseline. Broader compatibility and comprehensive runtime validation remain open.

- Obtain multiple matching reads of the affected device's SPI flash.
- Identify application, bootloader, configuration, and device-specific regions.
- Recover the device and document a tested recovery procedure.
- Establish a known-good original baseline for repeatable comparisons.

**Exit criterion:** demonstrated recovery on the actual hardware, with original device-specific data preserved.

## Milestone 2: packaging that preserves loader boundaries

- Preserve complete loader commands within each compressed block.
- Check both individual block parsing and the resulting memory map.
- Add regression coverage for the known cross-block command failure.
- Confirm update acceptance and successful startup on hardware with a recovery path.

**Exit criterion:** a repeatable, recoverable hardware test of a minimal modification—not just matching checksums.

## Milestone 3: small personalization experiments

Initial targets:

- Custom text labels with explicit length, encoding, and reference constraints.
- Palette changes, including Wi-Fi icon colors.
- Replacement source icons within the existing dimensions and pixel format.
- Offline previews and a change manifest showing exactly what changed.

**Exit criterion:** each supported change is validated separately on the documented hardware and firmware version.

## Milestone 4: a documented customization workflow

- A version-checked offline tool that rejects unsupported inputs.
- Clear separation of previews, analysis outputs, and hardware-tested artifacts.
- Backup, verification, rollback, and compatibility instructions.
- User-supplied original firmware instead of redistributed manufacturer images.

A complete redesigned UI, arbitrary animation/video playback, boot-screen replacement, and support for other models are exploratory topics, outside the initial scope. Community findings may change priorities.
