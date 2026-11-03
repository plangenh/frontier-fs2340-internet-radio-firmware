# Boot prefix, application loader and USB recovery investigation

Offline analysis of the verified 8 MiB physical dump, November 3, 2026. The prefix is unchanged between the pre-restoration reads and the separate post-restoration readback. This investigation performs no hardware operation. Manufacturer code, complete disassembly and private dumps remain outside this repository.

## Physical layout established from the dump

| Flash interval | Observed structure |
|---|---|
| `0x000000–0x000010` | Header with magic `0x01aa5500`, first-record pointer `0x100`, main marker pointer `0x12080`, and CRC16 |
| `0x000010–0x000030` | Four tag/value pairs listed below |
| `0x000080…` | Firmware/customization filename |
| `0x000100–0x003700` | 108 linked, CRC-protected records carrying the primary loader |
| `0x003700–0x011366` | CRC-protected compressed secondary loader |
| `0x011366–0x012000` | Zero-filled gap in this dump |
| `0x012000…` | Application payload; `enco` marker at `0x12080` |

Interval ends are exclusive. Header tag values are `APPN=0x12000`, `LNVS=0x7a1000`, `FSSP=0x781000`, and `PEND=0x403c6b`. APPN and LNVS corroborate the independently traced application and settings locations. FSSP's full semantics and PEND's consumer are unresolved; names alone do not establish partition behavior.

The header's final two bytes are a big-endian CRC16 over its first 14 bytes. Each primary record consists of 120 data bytes, a little-endian next-record offset, a little-endian 16-bit length of 128, and a big-endian CRC16 over the first 126 bytes. The observed CRC expression is `binascii.crc_hqx(data, 0xffff) ^ 0xffff`. All 108 records validate. Their data concatenates to 12,960 bytes; blindly decoding their physical carrier would mistakenly treat link/CRC trailers as instructions.

A `SECLCONF` structure in that reconstructed body identifies the secondary carrier's offset and length. The carrier contains 56,420 bytes of MSB-first DEFLATE followed by a two-byte CRC16. Removing the CRC and converting the DEFLATE bit order produces exactly 135,168 bytes. This establishes compression; the structure's name is not evidence of encryption or secure boot.

## Reconstructed primary execution

Address reconstruction is corroborated by literal cross-references and entry branches. Primary storage/data base is `0xb00f4000`; MinIM execution base is `0xb01e8000`. For this body, compact byte offset `o` maps to execution PC `0xb01e8000 + 2*o`. These are execution/data addresses, not SPI offsets.

The entry reaches `0xb01e8670`. Startup creates an IO handler and a task whose retained name identifies the Master Loader; its entry is `0xb01eb410`. The task-creation interpretation follows arguments, task names and queue/wait usage, rather than an exported symbol.

External veneers target `0xb01ff838…` and `0xb0000180…0xb0000350`. Their implementations are outside the extracted primary body. They must not be described as completely recovered reset-ROM code.

## Normal application loading and the failed experiment

The primary contains the normal application-loading path, including construction/comparison of the `enco` magic at execution PC `0xb01eb8c0`, reading 20-byte table entries, checking compressed-block CRCs and decompressing blocks. Around `0xb01eb9ec`, decoded buffer pointers and declared decoded lengths are sent through a message queue.

The Master Loader consumes those buffers and parses commands within each block (`0xb01eb574…0xb01eb61c`), dispatching through `0xb01ea614`. Its loop subtracts the command header/argument/payload footprint from the block's remaining byte count. No cross-block partial-command accumulator has been identified in this path.

This is direct code evidence supporting the earlier [command-boundary defect](loader-partition.md): the failed graphics update has 113 blocks whose commands cross block boundaries. Whole-chain replay concealed that property. In the first failing block (`0x67400`), only 212 bytes remain, while the next load command consumes 264 bytes. The actual consumer copies the declared payload without clamping it to that block and subtracts the command footprint, leaving unsigned `0xffffffcc` (−52). Its nonzero loop condition then continues parsing past the declared block. The actual primary loader's block-oriented producer/consumer path therefore confirms the static failure mechanism. It does not reproduce the exact runtime hang or prove that no other defect contributes.

A separate observation: PEND in the unchanged boot header still equals the original payload end, while the failed graphics payload was longer. Whether any loader actually uses PEND as a bound is unresolved; do not classify this mismatch as the proven cause or patch the field speculatively.

## Conditional secondary loader

The secondary is a conditional path, not established as an unconditional stage before every application start. Primary code checks bit `0x10` of MMIO address `0x0201503c`; the set-bit branch reaches the secondary path. An error helper at `0xb01e8820` writes `0x10` there and writes `1` to `0x02015000` before spinning. This resembles recovery-flag/reset handling; the register meanings and persistence are not verified on hardware.

Another secondary-entry decision compares two sampled 16-bit values against configuration thresholds. The sampling helper touches `0x020173xx` registers and appears ADC-like. No physical button names, header pins or reliable user-facing key combination have been established.

The secondary path reads the configured carrier, checks CRC at `0xb01e912c`, decompresses through `0xb01e97fc` to data/storage address `0xb0090000`, then transfers control to MinIM execution address `0xb0120000` at `0xb01e9174`.

The secondary contains connected USB DFU code, not only resource strings. A configured provider of type 13 dispatches through `0xb012aa04` into initializer `0xb0125794`, which registers download/upload callbacks, a flash worker and a display task. The display has waiting, upgrading and completion states; its completion path calls reset-like code.

| Property | Static evidence |
|---|---|
| USB identity | VID `0x10a4`, PID `0xc3bc`; initialization constants are copied into USB device-descriptor VID/PID fields |
| Transfer size | Configured as `0x1000` / 4096 bytes |
| Host-to-device download | Callback `0xb01254a8`; sequential block numbers, examined nonzero-data path accepts block numbers through `0x76e` |
| Device-to-host upload | Callback `0xb0125638`; bounded block addressing and flash-read helper calls |
| Flash destination formula | `0x12000 + (block_number << 12)` |
| Window for complete 4 KiB transfers | `[0x12000, 0x781000)`; upper bound equals the header's FSSP value |
| Completion | Zero-length download completes the examined sequential transfer; worker/display eventually reaches reset-like code |

The initial loader area is outside that ordinary DFU block window, as is the configured settings area. The callback trace is not a complete hostile-input validation audit: generic USB transfer-length validation and all external service behavior remain separate questions.

No image-name or cryptographic signature validation was found in the traced download callback/worker path itself. This bounded observation does not establish the full boot chain's authentication policy. Generic DFU vendor-verification error descriptions are not evidence of an implemented signature check.

No USB enumeration has been observed. The existing external USB socket's connection to device-mode signals is unknown. Identifying physical USB routing, a reproducible recovery entry and a compatible host-side transfer procedure remains necessary before attempting USB recovery. A standard-looking class implementation alone does not validate an off-the-shelf host command or justify connecting an arbitrary cable.

## What this enables and what remains open

The prefix is now structurally recoverable and its main application/secondary branches are visible. We can inspect the actual block-loading rules, preserve and compare loader versions, and investigate a potential recovery route without modifying startup code.

Still unresolved: complete reset ROM, external service implementations, exact physical recovery controls, hardware USB routing, the complete trust/signature policy, and a successful boot after chip reinstallation. CRC16 and DEFLATE are not cryptographic authentication, but their presence does not prove that every boot stage accepts unsigned modifications. No modified bootloader or recovery utility is offered.

## Reproduce structural inspection

```sh
python3 tools/inspect_boot_prefix.py private/full-chip.bin \
  --layout fs2340-touro-v4.10.18 --output private/boot-prefix.json
```

The tool requires an explicitly selected 8 MiB layout, checks header/record/carrier CRCs, follows bounded noncyclic record links and bounds secondary decompression. It emits structural metadata and hashes, not firmware bytes. It never contacts a programmer. Tests use synthetic records only, including corrupt CRCs, cyclic/unaligned/out-of-range links, decompression limits and input preservation.
