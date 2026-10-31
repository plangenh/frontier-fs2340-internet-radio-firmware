# Pre-publication validation

Date: October 31, 2026.

- Three synthetic/data tests passed, including DEFLATE round trips at four compression levels and rejection of a load command crossing a block boundary.
- The public extraction tools were run against the private original: 359 compressed blocks, six chains, 23 module records, and 30,084 loader commands.
- Every original block was checked independently for complete commands.
- Language resources were freshly extracted: 15 tables / 15,840 entries.
- Menus were freshly extracted: 39 forms / 102 rows. The result fully matches the curated public JSON file structurally.
- Publication checks passed for prohibited artifact types, local user paths, private network addresses, MAC addresses, and selected credential patterns.
- Raw data and local test outputs are outside the publication repository and are absent from the commit and ZIP.
- The English menu explorer's search and list filters were checked locally after translation.

Tests do not require hardware. GitHub Actions execution and Pages deployment require a connected GitHub repository; neither is claimed to have succeeded yet.
