# Command-aligned loader partitioning

The failed graphics experiment contained 113 compressed blocks whose decoded contents did not independently form complete loader-command sequences. Whole-chain replay had hidden commands crossing block boundaries. See the [failure investigation](recovery.md).

## Correction

The new offline primitive, `tools/loader_partition.py`, partitions a known command stream at command boundaries. It preserves command bytes and order, retains an explicitly requested number of nonempty blocks, and limits each decoded block to 20,480 bytes. It rejects malformed streams, an oversized individual command, or a stream that cannot fit the available block count. It does not split or reinterpret oversized commands.

The algorithm first greedily groups consecutive complete commands within the size limit. If fewer groups than existing IDs are needed, it splits groups only between commands until the required count is reached. Every resulting block is checked again, and joining the blocks must reproduce the input stream exactly. This changes partition boundaries rather than slicing at old byte lengths.

The local experimental builder now retains valid original boundaries for unchanged-length streams and otherwise uses this partitioner. Its low-level rebuild also rejects incomplete command sequences before compression, including unchanged malformed blocks. Those local integration scripts remain private; the public primitive and synthetic regression tests contain no manufacturer firmware.

## Actual retained-artifact validation

An offline rebuild used the retained blue Wi-Fi base and the same retained graphics blob from the failed experiment. It produced a private analysis-only ISU artifact, without a web-upload envelope or device access.

| Check | Result |
|---|---|
| Independently parseable decoded blocks | 359 / 359 |
| Recompressed blocks | 113 |
| Module count | 23, unchanged |
| Module/configuration command records | Unchanged |
| Loaded address coverage | Unchanged |
| Replayed memory differences from blue Wi-Fi base | 11,684 bytes, all within the intended icon blob |
| Container parsing | MD5, block CRCs, decoded lengths, and physical layout checks passed |

The rebuilt decoded graphics blob also matches the requested blob exactly. The original firmware remains byte-identical under an unchanged guarded rebuild, and the old failed artifact is rejected by the new rebuild guard.

Synthetic tests cover the previous boundary-splitting failure, exact block counts and command order, malformed input, oversized commands, and insufficient capacity.

## Limits

This is a repair of one demonstrated packaging defect, not a complete bootloader emulator. Checks use locally reconstructed formats and shared parsing code; agreement is not independent proof of the device's implementation. Block-ID/next-ID semantics, unavailable external loader code, boot metadata, and other acceptance conditions remain incompletely understood.

**No hardware boot has been tested, no recovery has been demonstrated, and no installable release is offered.** The analysis artifact is retained privately for later comparison. Its valid checksums and command boundaries must not be treated as permission or evidence to flash it.

## Preserving unchanged prefix and suffix blocks

A follow-up primitive, `partition_preserving_blocks`, keeps byte-matching original prefix and suffix blocks and repartitions only the middle. When the middle cannot fit its existing ID count, it progressively releases suffix blocks, then prefix blocks if necessary. It retains command order, complete commands, block count, and the 20,480-byte limit. It is a preservation heuristic, not a general minimum-change optimizer.

Synthetic tests demonstrate unchanged-block retention, middle changes, growth requiring more capacity, appended commands, exact stream reconstruction, and rejection of impossible inputs.

### Retained graphics experiment: no reduction

The original affected chain has 349 blocks. Comparing the rewritten stream identifies 236 matching prefix blocks and 112 matching suffix blocks: the actual resource rewriting is concentrated in the remaining original block.

Within that block, 43 load commands change, and six fill commands are replaced with 14 load commands. The stream grows by **2,428 bytes**, from 7,079,980 to 7,082,408 bytes. The net command-count increase is eight.

The preservation attempt nevertheless produces exactly the same analysis artifact as the previous command-aligned rebuild: 113 recompressed blocks and 246 unchanged compressed blocks across the complete container. It provides no size or change-count improvement for this input.

The capacity trace explains why preserving the matching suffix does not succeed:

| Available middle blocks | Stream bytes | Arithmetic capacity | Whole-command groups required |
|---:|---:|---:|---:|
| 1 | 22,752 | 20,480 | 2 |
| 16 | 327,684 | 327,680 | 17 |
| 32 | 653,112 | 655,360 | 33 |
| 64 | 1,303,660 | 1,310,720 | 65 |
| 112 | 2,280,504 | 2,293,760 | 113 |
| 113 | 2,284,128 | 2,314,240 | 113 |

Total free bytes alone are insufficient: consecutive complete commands must fit individual blocks. The original last block supplies enough usable room to complete the ordered grouping. These numbers explain this algorithm's result for this retained stream, not an impossibility theorem for every alternative command rewrite.

Further reduction would require changing the rewritten command representation or another packing strategy, rather than merely moving boundaries around the same commands. That would require fresh semantic validation. No smaller artifact, hardware test, or installable release is claimed.
