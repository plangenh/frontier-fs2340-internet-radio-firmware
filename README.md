# Frontier Venice X / FS2340 Firmware Research — Majority Touro

Independent research into Frontier Venice X / FS2340 internet radio firmware, currently based on one specific Majority Touro firmware version. Coverage of other devices is unverified. This is not an official manufacturer project.

**Status: November 3, 2026.** This repository documents findings and provides offline analysis tools. It does not provide installable custom firmware or a confirmed recovery procedure.

## Findings

- Verified 359 compressed blocks in the examined original update.
- Identified 15 language tables containing 1,056 text resources each.
- Recovered 39 static list/menu forms with 102 declared entries: 96 labels resolved statically; six remain dynamic.
- Identified 65 bitmap resources using 4 bpp indices and RGB565 palettes; internal PNG round trips reproduced the original records byte for byte.
- Traced the Podcast icons to renderer indices 42–44.
- Located and decoded the 320×240 Welcome startup image in the separate FSSP window and traced its primary-loader display path.
- Reconstructed the CRC-protected primary boot loader and compressed secondary USB DFU loader; traced application block parsing and bounded DFU read/write callbacks. Physical recovery entry and USB routing remain unverified.
- Identified a loader-command repartitioning defect in an experimental modification that preceded a startup failure.
- Obtained two identical physical 8 MiB reads, confirmed the failed payload, restored the original payload while preserving all other memory bytes, and verified a separate full-chip readback. Reinstallation and a successful boot test remain pending.

**The presence of text or tables does not prove that a feature is enabled on a particular device.** Some menus are populated dynamically. Static analysis is not observed execution.

## Roadmap: firmware personalization

The goal is to make it possible to personalize text, icons, and colors on compatible devices. Resource formats are understood, and a small text modification was reported working on hardware. Reliable, recoverable custom firmware is still a development target—not an available release.

The next milestones are device recovery, command-boundary-safe packaging, and repeatable hardware validation. See the [roadmap](docs/roadmap.md) for scope, prerequisites, and release criteria. There is no committed release date.

## Public menu explorer

[Open the menu explorer](https://plangenh.github.io/frontier-fs2340-internet-radio-firmware/) · [Repository](https://github.com/plangenh/frontier-fs2340-internet-radio-firmware)

## Documentation

- [Findings and evidence](docs/findings.md)
- [Menu structures](docs/menus.md)
- [Buttons, rotary input and context-dependent actions](docs/input-controls.md)
- [Feature visibility and dynamic menus](docs/feature-visibility.md)
- [Source dispatch and saved settings](docs/source-dispatch-and-settings.md)
- [Configured settings window and dump inspection](docs/storage-layout.md)
- [Local-update payload to Flash mapping](docs/update-flash-mapping.md)
- [Web-update completion and restart](docs/update-completion.md)
- [Container and loader](docs/container.md)
- [Boot prefix, application loader and USB recovery](docs/bootloader.md)
- [Boot checks, recovered runtime helpers and Welcome image](docs/boot-validation-and-splash.md)
- [Command-aligned partition repair](docs/loader-partition.md)
- [Second structural loader checker](docs/independent-loader-check.md)
- [Second-parser loaded-memory comparison](docs/loaded-memory-comparison.md)
- [Display resources](docs/display.md)
- [Failed update and recovery status](docs/recovery.md)
- [Personalization roadmap](docs/roadmap.md)
- [Reproducing the analysis](docs/reproduce.md)
- [Connecting GitHub and enabling Pages later](docs/publishing.md)
- [Publication scope and privacy](docs/publication-scope.md)

Open the [menu explorer](site/index.html) using a local web server, or publish `site/` through GitHub Pages. The public explorer contains short menu-label excerpts and technical metadata; complete language packs and original graphics are not included. English is the primary interface language; original German labels remain alongside English labels as evidence.

## Quick start

Python 3.10 or newer; standard library only:

```sh
python3 -m unittest discover -s tests -v
python3 tools/publication_check.py
python3 tools/analyze_firmware.py /path/to/your/original.isu.bin --output private/analysis
python3 tools/extract_resources.py private/analysis/manifest.json --output private/resources
```

The analysis is specific to the documented firmware and does not contact a device. There is no upload or flash command in this repository. Local extracted data stays in the Git-ignored `private/` directory.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Distinguish observations, static evidence, and hypotheses. Remove credentials and device identifiers before sharing attachments.

## License and provenance

Original scripts and original documentation: [MIT](LICENSE). Manufacturer firmware, extracted labels, product names, and third-party contributions are outside that license; see [NOTICE](NOTICE). Tools were developed with AI assistance. Tests verify selected properties, not general suitability for arbitrary firmware.
