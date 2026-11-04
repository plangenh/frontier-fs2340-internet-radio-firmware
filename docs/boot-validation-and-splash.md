# Boot validation, recovered runtime helpers and Welcome image

Follow-up to the [physical bootloader investigation](bootloader.md), November 3, 2026. All work in this pass uses retained files offline. No bootloader, splash or other device bytes were modified.

## Welcome screen: located and connected to rendering

The actual startup image is outside the ordinary application update, at the boot header's FSSP location:

| Field | Observed value |
|---|---|
| Record start | `0x781000`, four-byte `FSSP` magic |
| Compressed length | Little-endian word at +4: `0x116b` / 4,459 bytes |
| Compressed pixel stream | `[0x781008, 0x782173)`, MSB-first DEFLATE |
| CRC16 | Big-endian `0x3086` at `0x782173`; `crc_hqx(encoded, 0xffff) ^ 0xffff` matches |
| Decoded size | 153,600 bytes |
| Renderer geometry | 320 × 240, 640 bytes per row, 240 rows |
| Pixel interpretation | Big-endian RGB565 |
| Decoded pixel SHA-256 | `fd6afc52b26b6d667be7bede84d8c2f6a88236c1768bdd56f4d551965a6512f0` |

The decoded pixels visibly contain the requested Welcome wording and layout. The private preview has white/gray lettering on black; the supplied photograph appears white on blue. Exact physical panel color behavior is not established by the pixel preview.

This attribution is code-backed. Primary configuration at physical `0x323c/0x3240` supplies the FSSP start and maximum window. Startup reaches reader `0xb01e9188`, checks magic at `0xb01e9228…0xb01e9238`, checks CRC at `0xb01e927c`, and decompresses at `0xb01e92a4` to `0xb0090000`. That buffer is passed through `0xb01e8f1c` to display setup `0xb01ebd78` and renderer `0xb01ebfc4`, which sends 640-byte rows through its SPI writer. Thus this is an identified early startup asset, not a later application overlay inferred from similar dimensions.

Immediately after the image CRC, another structure begins with `FLK1` at `0x782175`. Its format is not reconstructed here. A future replacement must preserve that neighboring data; increasing compressed image length cannot simply overwrite it. The normal DFU callback window ends exactly at `0x781000`, so the examined ordinary DFU block path does not include this splash record. The ordinary web-update payload likewise does not cover it.

The manufacturer bitmap, raw pixels and disassembly remain private. A metadata-only inspector is available:

```sh
python3 tools/inspect_boot_splash.py private/full-chip.bin \
  --layout fs2340-touro-v4.10.18 --output private/splash-inspection.json
```

The inspector checks the record bounds, compressed-data CRC, complete DEFLATE stream and exact pixel count. It emits metadata and a hash, not pixels, and never contacts hardware. Tests use synthetic pixels and corrupted/bounded records only.

## FLK1 neighbor follow-up: November 4, 2026

The full `[0x781000, 0x7a1000)` window is byte-identical between the pre-restoration backup and the separately acquired restored-chip readback. The owner has since [confirmed successful startup after reinstalling the chip](recovery.md).

Immediately after the splash CRC, offset `0x782175` contains ten consecutive non-erased bytes: `46 4c 4b 31 0f 00 00 00 00 00`. This can be read as the marker `FLK1`, a little-endian word 15 at +4 and a 16-bit zero at +8, but their meanings are not established. Ten populated bytes do not establish the formal record length.

Every byte from `0x78217f` through exclusive `0x7a1000` is `0xff`: 126,593 bytes. This is an observation of erased-looking storage, not proof of allocatable space.

A bounded search of the original initialized module images found no literal `FLK1`. Constant-construction searches in the existing primary, secondary, runtime-kernel and main-thread instruction indexes did not establish a consumer. The connected primary splash path consumes the image header, compressed bytes and CRC; no subsequent FLK1 handling is demonstrated there. Unindexed/indirect code or external services remain possible, so the marker must not be classified as unused.

For a future splash candidate, the conservative constraint is to retain the existing **4,459-byte compressed length**, CRC position, absolute FLK1 position and every byte after it. This preserves both the observed physical location and relative adjacency. Merely creating a shorter image would not preserve both, and appending arbitrary padding to DEFLATE is not validated. No splash patch or fixed-size recompressor has been created or hardware-tested by this pass.

The metadata inspector now reports the next known marker, observed non-erased extent, erased suffix and a hash of the following window. It does not decode the FLK1 schema or modify its data. A synthetic neighboring-record test checks that these bytes remain outside the splash decoder and that input is unchanged.

## Correction: some external runtime targets were not missing ROM

Earlier traces stopped at runtime addresses `0x80915ad0`, `0x8091598c`, `0x80915900`, `0x8090f778` and `0x8090f964`, because those targets were absent from the original main-thread instruction index. That was an indexing/address-interpretation limit, not proof of ROM residence.

The original `_lib0` module contains compact instruction bytes starting at storage address `0x80880000`. Corroborated decoding maps this body to execution base `0x80900000`, with `pc = 0x80900000 + 2*(storage - 0x80880000)`. Constructed absolute callback/call addresses and coherent function entries corroborate the mapping. It must not be generalized to unrelated address windows or used to classify every byte as code.

Recovered concrete operations:

| Runtime target | Recovered behavior |
|---|---|
| `0x80915ad0` | Supplies argument zero to status helper `0x80915cd0`; the examined branch clears a high status bit in MMIO `0x02015004` and writes magic values `0xabcd1234` / `0x4321dcba` to `0x02015008/0x0201500c` |
| `0x80915900` | Masks interrupts, acquires a lock and reaches reset code `0x80915b3c` |
| `0x80915b3c` | Writes 1 to MMIO `0x02015000` and spins |
| `0x8091598c` | Reads/transforms status bits and passes the result to a status-write helper before the later reset call |
| `0x8090f778` | CRC16 routine; referenced nibble table at `0x8201584c` has the non-reflected CCITT polynomial `0x1021` |
| `0x8090f964` | Three-byte big-endian serialization helper; it was previously treated too broadly as a final transaction boundary |

These observations resolve several previously unavailable web-update calls. The pre-write helper's examined body performs MMIO status/magic writes, not an observed Flash-header update. Hardware register semantics and retention across reset remain partly inferred.

This does not recover the complete processor reset ROM. Primary-stage external veneers targeting other address families still require separate carrier/address evidence. A call target alone is insufficient to decide whether an implementation lives in ROM, another loaded module or an unindexed mode.

## Integrity checks and authentication: bounded conclusions

Several different checks must be distinguished:

- The primary boot header, linked loader records, secondary carrier, splash carrier and normal compressed application blocks use CRC16 checks. Primary wrapper `0xb01e8988` checks the complete-message residue `0x1d0f` with seed `0xffff`.
- The ordinary web-upload path computes a 16-byte MD5 digest over the ISU payload and compares it to outer-header bytes +`0x6c`. The traced MD5 initialization/update/finalization path is keyless.
- The examined normal application producer checks compressed-block CRCs, decompresses each block, queues it to the command consumer and eventually hands off to the returned entry address. No additional cryptographic validation call appears in the examined final handoff.
- The examined DFU callbacks and worker reach SPI-shaped read/program/erase operations. No image-name or cryptographic signature verification was identified inside those bounded paths.

CRC16 and keyless MD5 verify consistency; they are not cryptographic signatures. These traces do not prove that every possible path, configuration, opaque external service or processor ROM lacks authentication. The earlier user-reported successful resource-text modification is compatible with resource personalization; it does not establish that arbitrary executable replacements are accepted.

## Practical consequence

The Welcome asset can now be targeted independently and several runtime/reset/validation paths are understood more precisely. A custom processor bootloader remains a separate, larger task: external services, early hardware initialization, the complete trust chain and recovery behavior still need validation. No modified loader, splash patch or generally usable recovery procedure is supplied by this investigation.
