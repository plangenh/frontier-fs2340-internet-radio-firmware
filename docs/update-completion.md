# Web-update completion and restart

This is a static trace of the documented FS2340 firmware's buffered web-upload path. It explains the visible completion sequence; it does not establish that an installed image will boot. No device was contacted or written during this investigation.

## Completion chain

| Stage | Observed instructions |
|---|---|
| Payload writer returns | Worker calls `0xb2090ba0` at `0xb2090e40`. |
| Worker reports completion | It writes status `5`, progress `100`, and invokes the registered callback with code `9`. |
| Web callback | Registration at `0xb209765c` supplies `0xb20da318` through `0xb20fd254`. The callback posts a changed code plus `0x800`, so code `9` becomes event `0x809`. |
| Web event dispatch | Dispatcher `0xb20dac40` subtracts `0x802`; its event-`0x809` entry reaches `0xb20dad5c`, selecting state `15`. |
| Completion state | State setter `0xb20da60c` dispatches state `15` to `0xb20da8e0`, writes auxiliary status `5`, prepares a dialog, and branches to the shared tail at `0xb20dab6c`. |
| Shared terminal tail | It builds the dialog, calls `0xb20ea9b0`, passes `2000` to helper `0xb20da5c8`, then calls `0xb20b8204` and `0xb20b7bd4`. |

The last two calls are trampolines to **`0x8091598c`** and **`0x80915900`**. These targets were absent from the initial main-thread instruction database. The [later runtime-kernel decoding](boot-validation-and-splash.md) locates both in the supplied `_lib0` module: the first prepares MMIO status and the second reaches the reset-register write. Their ordering remains established. The sequence is consistent with the reported automatic restart, but static analysis alone does not observe that restart.

State `14` also reaches this terminal tail, through `0xb20daad0`. It must not be mistaken for the completion state's entry. A separate update UI uses other callbacks and states; those must not be substituted for this web path.

## What the progress bar proves

The short worker completion tail follows the payload writer's return. It contains no visible read-back, decompression test, or next-boot execution test before reporting status `5` and progress `100`.

This is a bounded observation about that tail. It does **not** prove that all lower-level verification is absent: a later [runtime-kernel trace](boot-validation-and-splash.md) recovers the pre-write/status/reset helpers, but it does not establish a complete boot trust policy. It also does not establish the helper's `2000` argument as milliseconds.

A completed write display and a subsequent boot failure are therefore compatible. The earlier experimental package's invalid compressed-block command boundaries remain a concrete independently identified defect; this completion trace does not establish any additional cause of the failure.

## Follow-up status

The [later investigation](boot-validation-and-splash.md) resolves the previously unindexed pre-write and terminal status/reset routines. The [physical readout](recovery.md) also established that the failed graphics payload was present byte for byte. The primary application loader's block-oriented parser is now [reconstructed](bootloader.md), corroborating the command-boundary failure mechanism.

Remaining questions include exact hardware retention/meaning of MMIO status fields, the complete reset-ROM trust policy and a physically validated USB recovery entry. The owner has since [reported successful startup after chip reinstallation](recovery.md); this is separate from the earlier static completion trace.

## Evidence scope

Execution addresses refer to the original version documented in [the findings](findings.md). The private evidence bundle retains exact decoded instruction ranges for the worker, callback registration, callback, state dispatcher, event dispatcher, and both trampolines. Public documentation intentionally excludes firmware bytes and full disassembly.
