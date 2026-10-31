# Second structural loader checker

`tools/independent_loader_check.py` implements a second container and loader-command parser without importing the packer, partitioner, or extraction parser. It is an offline structural check, not a bootloader emulator.

```sh
python3 tools/independent_loader_check.py private/candidate.isu.bin \
  --output private/independent-check.json
```

The tool reads the ISU file and creates a new JSON report. It performs no firmware execution, device discovery, upload, or Flash access. Existing output files are not overwritten.

## Checks and evidence

- Outer header, payload MD5, fixed `enco` position, bounded table and block sizes.
- Unique block IDs, contiguous physical positions, block prefix, CRC, decoded length, and DEFLATE end-of-stream.
- Chain reachability, cycles and merged chains, preserving module context between blocks.
- Complete command headers and payloads within each individual decoded block.
- Module declaration before memory commands and terminated module names.
- Memory-range arithmetic without wrapping the 32-bit address space.
- Overlapping writes within a module, reported as ranges and write indices.

Module names and addresses in the output come from the selected image; keep reports private. The tool does not export resource bytes. Analysis bounds limit input size to 8 MiB, block count to 4,096, and total advertised decoded content to 64 MiB; overlap reporting is bounded to 100,000 entries.

Synthetic tests include truncated metadata and loads, missing module context, unterminated names, unsupported tags, address wrap, overlapping writes, and module context across block boundaries. Container mutations deliberately refresh the outer MD5 so that deeper checks must detect bad block positions, sizes, links, decoded lengths, prefixes, and CRCs.

## Independence boundary

The vendor DEFLATE bit transcoder is shared with existing tools. Python's zlib and CRC implementation are also shared dependencies. This is a separately implemented structural parser, not a fully independent decoding stack.

Unknown chain terminal IDs remain opaque. No complete valid-address map for RAM/MMIO has been established; a nonwrapping address is not necessarily valid. Overlaps are not automatically corruption and are not yet classified by conflicting values. Resource interpretation, execution semantics, boot metadata, update acceptance, and hardware bootability remain outside this check.

## Retained-file results

The second parser was run on the actual locally retained files, not just synthetic fixtures:

| Input | Structural result | Blocks | Chains | Commands | Overlapping writes |
|---|---|---:|---:|---:|---:|
| Original | Passed | 359 | 6 | 30,084 | 0 |
| Blue Wi-Fi experiment | Passed | 359 | 6 | 30,084 | 0 |
| Failed graphics experiment | Rejected: load crosses block boundary | — | — | — | — |
| Command-aligned graphics rebuild | Passed | 359 | 6 | 30,092 | 0 |

The rebuilt stream contains eight more commands than the original because of the resource rewrite. This count alone does not explain or validate their semantics; the separate [rebuild memory comparison](loader-partition.md) checks the requested resource blob and unchanged other memory. Detailed reports remain private. These outcomes corroborate the known boundary defect and its structural correction, without demonstrating a successful boot.
