# Loaded-memory comparison through the second parser

`tools/compare_loaded_memory.py` uses the [second structural parser](independent-loader-check.md) to replay load and fill commands into separate module address spaces. It does not import the packer's memory replay implementation.

```sh
python3 tools/compare_loaded_memory.py private/base.isu.bin private/candidate.isu.bin \
  --allow 'example.elf:0x32001000:0x32001100' \
  --output private/memory-comparison.json
```

The example range is illustrative, not a radio patch location. Allowed ranges are explicit caller input, have exclusive ends, and are recorded in the report. With no allowed ranges, every changed mapped byte is outside scope.

The comparison distinguishes unmapped bytes from mapped zero bytes, applies writes in loader order, and preserves the phase of repeated 32-bit fill values across page boundaries. It reports changed jointly mapped bytes separately from coverage changes, counts changes by module, and retains at most 32 changed addresses. Metadata command sequences are compared by SHA-256 of their exact bytes. Reports contain no firmware payload bytes but should remain private because addresses and module names come from the input.

Memory replay is capped at 16,384 pages of 4 KiB per image, or 64 MiB of address coverage including page rounding; occupancy masks require additional memory. The tool creates only a new report and never accesses a radio.

## Limits

The result models load/fill effects, not execution or startup initialization. Module address spaces remain distinct and no hardware alias normalization is applied. Metadata sequence equality is not a complete semantic model of configuration. The DEFLATE transcoder remains shared with other tools. A scope check is not a firmware acceptance, bootability, or Flash-write authorization.

Tests cover fill phase across page boundaries, fill-to-load equivalence, changed coverage containing zeros, scoped byte changes, last-write order, unchanged inputs, and full synthetic-container comparisons.

## Retained graphics rebuild result

The retained blue Wi-Fi experiment was compared against the corrected graphics rebuild. Allowed ranges were restricted to palette and pixel bytes of Podcast assets 42, 43, and 44, excluding each three-byte asset header.

| Check | Result |
|---|---|
| Changed mapped bytes | 11,684 |
| Changes outside the three palette/pixel ranges | 0 |
| Coverage differences | 0 |
| Metadata command byte sequence | Equal |

Thus the asset headers and all other reconstructed memory bytes remain unchanged relative to that base. The blue Wi-Fi changes already present in the base are preserved, not revalidated as correct hardware behavior. The detailed comparison and ranges remain in the private evidence bundle. No firmware was uploaded or booted.

## Container identity checks

The report also compares the ordered block IDs and `(ID, next-ID)` pairs, block count, the entire pre-table header excluding only the outer MD5 field, and the complete 20-byte table terminator. When ordered IDs agree, it separately counts relocated blocks, compressed-size changes, decoded-size changes, and changed compressed-block bytes (using SHA-256).

These checks are independent of loaded-memory equality: two images can load the same bytes while having different IDs or headers. Synthetic tests exercise that distinction. A passing memory scope check must not be read as a passing container-identity check.

In the original, the six observed chains all terminate at `0xffffffff`. Across their 353 internal links, the ID differences match neither the preceding decoded block size nor its compressed on-disk size. This rules out those two simple offset interpretations for the observed links; it does not resolve the full meaning of IDs. The checker therefore does not invent a general ID recalculation rule or whitelist terminals for other images.

For the retained blue Wi-Fi base versus the corrected graphics rebuild, the extended checker reports:

| Container property | Result |
|---|---|
| Block count, ordered IDs, ordered links | Equal |
| Pre-table header excluding outer MD5 | Equal |
| Table terminator | Equal |
| Relocated blocks | 122 |
| Changed compressed block bytes | 113 |
| Changed compressed-size fields | 112 |
| Changed decoded-size fields | 33 |

Relocation and recompression are counted separately: a moved block need not contain changed compressed bytes, and recompression can change bytes without changing length. These results establish what this rebuild preserved; they do not prove that decoded-size changes or repartitioning meet every requirement of the unavailable loader implementation.
