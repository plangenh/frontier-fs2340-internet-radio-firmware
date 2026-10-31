# Pre-publication validation

Date: October 31, 2026.

- Synthetic/data tests passed, including DEFLATE round trips at four compression levels and rejection of a load command crossing a block boundary.
- The public extraction tools were run against the private original: 359 compressed blocks, six chains, 23 module records, and 30,084 loader commands.
- Every original block was checked independently for complete commands.
- Language resources were freshly extracted: 15 tables / 15,840 entries.
- Menus were freshly extracted: 39 forms / 102 rows. The result fully matches the curated public JSON file structurally.
- Publication checks passed for prohibited artifact types, local user paths, private network addresses, MAC addresses, and selected credential patterns.
- Raw data and local test outputs are outside the publication repository and are absent from the commit and ZIP.
- The English menu explorer's search and list filters were checked locally after translation.

Tests do not require hardware. GitHub Actions execution and Pages deployment require a connected GitHub repository; neither is claimed to have succeeded yet.

## Follow-up correction

The menu extractor now joins declared zero-fill with initialized bytes. This recovers Network wizard and changes the static label count from 95 to 96. A synthetic end-to-end regression test covers the exact boundary pattern. The corrected extractor was also rerun against the private original.

## Read-only dump inspector

Seven public tests now pass. The additional synthetic dump tests cover input size, bounded candidate search, input preservation, and non-decoding of encrypted, cross-sector, and truncated candidates. No physical flash dump was supplied or tested.
