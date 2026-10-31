# Reproducing the analysis locally

Python 3.10+ and its standard library are sufficient. No additional programs or device access are required.

1. Obtain your own lawful copy of the documented original update.
2. Run the parser with a new private output directory:

```sh
python3 tools/analyze_firmware.py /path/to/original.isu.bin --output private/analysis
python3 tools/extract_resources.py private/analysis/manifest.json --output private/resources
```

The parser verifies the expected SHA-256, ISU MD5, block CRCs, sizes, and complete commands within each decoded block. It produces local module regions, a manifest, and string lists. The source firmware is read-only. Existing output directories are rejected; a failed run may leave an incomplete new output directory.

The resource reader resolves 15 language tables through the root at `0x32b12b58`. These complete private language resources do not belong in the public repository.

## Extract menu descriptors again

```sh
python3 tools/extract_menus.py private/analysis/manifest.json private/resources/locales_complete.json --output private/menus
```

The search pattern is strict and version-specific. Other UI formats and dynamic entries are outside its coverage. The public data file was derived from the same original version.

## View the public site locally

```sh
python3 -m http.server 8000 --directory site
```

Open the local port in a browser. No build step, external fonts, or external scripts are required.

## Tests

```sh
python3 -m unittest discover -s tests -v
python3 tools/publication_check.py
```

Public tests use synthetic data and the curated menu file. The full firmware test requires the original file, which is not distributed, and was additionally run locally. All findings refer to the documented SHA-256; this is not a general parser for arbitrary Frontier versions.
