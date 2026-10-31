# Contributing

1. Include the firmware version and SHA-256; do not attach firmware files.
2. Support findings with addresses, records, reproducible commands, or sanitized observation logs.
3. Label evidence as static, observed at runtime, inferred, or unresolved.
4. Do not publish MAC addresses, private IP addresses, Wi-Fi names or keys, personal files, or complete device reports.
5. Do not infer flash safety from valid CRC or MD5 values alone. Loader structure and hardware state require separate checks.
6. Before submitting a pull request, run the tests and `python3 tools/publication_check.py`.

The public explorer in `site/` intentionally contains only menu excerpts and original research descriptions. Complete extracted resources belong in the ignored `private/` directory.
