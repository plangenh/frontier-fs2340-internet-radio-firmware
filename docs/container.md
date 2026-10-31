# Update container and loader

## Statically verified

- The ISU header is 124 bytes. Bytes 108–123 match MD5 over all bytes starting at offset 124.
- An embedded `enco` container has 20-byte block-table entries: ID, encoded location, compressed size, next ID, and decoded size.
- Each compressed block starts with marker `0x63`, followed by Frontier MSB-first DEFLATE. Two following bytes contain CRC-16/GENIBUS over the compressed stream, excluding the marker.
- Numeric bit representations can be transcoded to RFC 1951 DEFLATE and independently decompressed using standard-library zlib.
- IDs and next-ID links form a lookup graph. They are not established as cumulative decoded byte offsets.

## Loader commands

Observed commands contain module names, initialized load bytes, fill regions, and configuration records. All 359 original blocks independently parse as complete command sequences. A correct combined memory image is therefore insufficient validation: command boundaries within individual blocks must also be preserved.

## Web upload

The examined local upload route accepted an envelope consisting of XML metadata, two zero bytes, and the complete ISU. Metadata includes version, customization, size, and MD5 of the entire ISU. That checksum is distinct from the MD5 inside the ISU header.

Earlier header variants were rejected with “File check failed! Please select another binary.” After correct packaging, a small text modification was reported working during testing. This does not guarantee acceptance or bootability of further changes.

This public package intentionally contains no firmware builder or upload client. Checksums establish consistency, not bootability or the absence of additional acceptance checks.
