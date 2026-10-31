# Display and graphics resources

Three descriptors at `0x32b722d4` contain 320 × 240 dimensions and consecutive buffers of 153,600 bytes each. A declared zero-fill region covers 460,800 bytes in total. This supports three 16-bit pixel buffers; their exact front, back, or scratch roles remain unresolved.

The contiguous graphics range from `0x32b4ee5c` to exclusive end `0x32b6f5e8` contains 65 records:

1. One header byte: zero in all recovered records; meaning unresolved.
2. Width and height: one byte each.
3. Sixteen big-endian RGB565 colors: 32 bytes in total.
4. 4 bpp pixel indices, high nibble first; each row occupies `ceil(width / 2)` bytes.

Record size: `35 + ceil(width / 2) × height`. For odd widths, the unused row nibble must be preserved. Palette entry zero was displayed as black in local previews; this does not establish transparency semantics.

## Source icons

Eight 28-byte source records begin at `0x32aeea8c`. The lookup routine is at execution PC `0xb20933c4`.

| Source | Mode | Base image index |
|---|---:|---:|
| Internet radio | 1 | 39 |
| Podcasts | 2 | 42 |
| Spotify | 3 | 45 |
| Music player | 4 | 48 |
| DAB | 5 | 51 |
| FM | 6 | 54 |
| Bluetooth | 7 | 60 |
| AUX | 8 | 57 |

Podcast record: `0x32aeeaa8`. Image 42 at `0x32b59955` is 79 × 72; image 43 at `0x32b5a4b8` is also 79 × 72; image 44 at `0x32b5b01b` is 110 × 110 pixels. Static variant selection adds one to the base index for the selected popup state and two for the focused carousel center.

Understanding this format enables offline analysis. It does not prove that newly encoded resources can be installed safely.
