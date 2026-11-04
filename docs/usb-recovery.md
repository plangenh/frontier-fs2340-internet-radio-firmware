# USB recovery: confirmed entry, pending connection

Scope: the documented Majority Touro FS2340-0000-0444 firmware and the recovered unit. November 4, 2026. Static code evidence and owner observations are separated below. No USB firmware transfer has been performed.

## Entry confirmed on the radio

The owner tested this without a USB cable:

1. Switch off the radio at its rear power switch or disconnect its external supply.
2. Hold **Standby/Mode and Alarm** together.
3. Restore power while holding both keys until the display changes.

The owner reported **Waiting for PC wizard**. This confirms a practical entry into the recovery UI on this particular device. It does not establish USB enumeration, wiring compatibility or a successful DFU transfer.

### How the entry was derived

The primary loader compares two sampled 16-bit values against thresholds in its configuration. The normal application ADC table maps the interior of recovery ranges to raw driver keys 4 and 10; the local key map identifies these as Standby/Mode and Alarm.

- Recovery sample ranges are approximately channel 0: 384–491 and channel 1: 170–280. Exact boundary behavior differs from the ordinary key classifier; these are not voltage specifications.
- The ordinary ADC threshold arrays start at data address `0x32b4ec78`. Channel 0 has nine thresholds and channel 1 eight; the second channel's cumulative key indexes begin at nine.
- Evaluating example samples `(440, 225)` follows the primary branch to the secondary loader, rather than the separate branch setting status bit `0x40`.
- META condition `CS/LO` represents unsigned less-than in the retained ISA reference. Applying ARM carry conventions would misinterpret these comparisons.

The hardware report corroborates the key mapping. It should not be generalized into an untested list of recovery/factory-reset combinations for other radios.

## What the firmware provides

The [secondary loader](bootloader.md) registers a USB DFU implementation with VID:PID **`10a4:c3bc`**, read/write callbacks and 4096-byte transfers. Its ordinary callback address formula is:

```text
physical flash offset = 0x12000 + block_number * 4096
```

Accepted complete blocks nominally span `[0x12000, 0x781000)`. This covers the application window but excludes the primary/secondary prefix, startup bitmap and configured settings area. The interface is not a full-chip backup substitute.

The expected transfer data begins at the raw application payload, not the outer 124-byte ISU header or an XML web-upload envelope. No USB write procedure or accepted image format has been tested here.

A software helper at execution PC `0xb2008090` sets recovery bit `0x10` in MMIO `0x0201503c` and reaches the reset path. A generic restart event can also propagate a mask into that status mechanism. No user-accessible menu, web or FSAPI entry for this helper has been established; no software trigger was executed.

## Controller reuse: strong static evidence, not board continuity

The DFU configuration registers the function-controller driver named `syn_hsfc`; the main application contains the host-controller path named `syn_hshc`. Both examined configurations refer to resource index 0, type 2, MMIO base **`0x02020000`**. This supports use of the same controller in different firmware roles.

Frontier's [Venice X product brief](https://www.frontiersmart.com/wp-content/uploads/2021/10/Venice-X_PB.pdf) specifies USB 2.0 High Speed device/host capability and USB field upgrades. It does not establish the socket wiring or power-switch implementation of this particular product.

The owner reports only the USB-A music socket, with no separate service connector. Available photographs show the Frontier module, not a sufficiently traced connection from the external socket through the carrier board. Exact D+/D− continuity, VBUS switching, VBUS sensing and any additional internal connection remain unverified.

Before selecting a PC connection, establish the radio socket's VBUS behavior in recovery mode and the carrier board's power routing. Do not infer electrical compatibility merely from the shared controller or the waiting screen. In particular, an arbitrary direct powered USB-A-to-USB-A connection has not been validated.

## Owner VBUS measurement

While the radio was displaying the recovery waiting screen and without a PC USB connection, the owner reported measuring approximately **5 V at the USB-A socket**. This establishes voltage at the socket, not the supply's current capacity or complete circuit topology. Treat it as a powered socket; a direct cable that joins the PC and radio VBUS rails is not an approved test setup.

The next enumeration experiment requires a verified separation of the two VBUS rails while retaining D+, D− and common ground, or a suitably engineered isolated interface. This is a proposed connection constraint, not an electrically validated cable recipe. A power-blocking adapter must not be confused with a USB data blocker, which disconnects the very data signals needed here. VBUS sensing or device attach requirements can still prevent enumeration even with the power rails separated.

The normal host driver contains port-power-like set/clear paths at MMIO `0x02020440` (bit `0x1000`). The examined DFU initialization does not establish an equivalent VBUS-disable action. This is consistent with the need for the physical measurement, rather than proof of any particular board power-switch design.

The reconstructed DFU descriptor uses interface class/subclass/protocol `FE/01/02`, 4096-byte transfers, and raw `bcdDFU=0x0101`. These are code-derived values, not descriptors captured from a USB connection; do not relabel the raw version as `0x0110`.

## Host-side preparation completed

`dfu-util` 0.11 is installed on the research Mac. Only listing was run:

```sh
dfu-util -l -d 10a4:c3bc,10a4:c3bc
```

No matching device was listed. Since no verified radio-to-PC USB connection was present, this is not a negative test of the radio's DFU implementation. No detach, reset, upload or download was initiated.

The [official dfu-util manual](https://dfu-util.sourceforge.net/dfu-util.1.html) defines `-l` as listing, `-U` as reading from a device and `-D` as writing to a device. These directions are easy to confuse. The `-s` option belongs to DfuSe addressing; no DfuSe command recipe is established for this radio.

## Next observations needed

1. With 5 V now measured in PC-Wizard mode, establish a test connection that separates PC/radio VBUS and verify the data/ground routing.
2. Once the electrical connection is understood, perform listing only and capture VID/PID, interface, protocol and transfer-size descriptors.
3. If enumeration is stable, test a read-only upload of the available application window and compare it against the preserved SPI backup.
4. Develop a write procedure only after those checks; retain the original loader and full-chip backups.

The key-entry result is owner-observed. Controller/transfer details are static analysis. USB enumeration and recovery transfers remain untested.
