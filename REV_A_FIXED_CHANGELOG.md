# CMDeck Rev A Fixed Changelog

Baseline: upstream commit `66e5f08`.

## Keyboard PCB

### Flash chip select

- Renamed anonymous net `N$12` to `QSPI_SS_N` in both schematic and board.
- Connected RP2040 U1 logical pin `QSPI_SS_N`, physical pad 56, to the existing flash-select network.
- The completed net contains:
  - U1 pad 56: RP2040 `QSPI_SS_N`
  - U3 pad 1: W25Q128JVSIM `!CS`
  - R4 pad 1: 10 kOhm pull-up branch to 3V3
  - R6 pad 2: BOOT-button series branch
- Added a 0.2032 mm bottom-copper route around the outside of the existing QSPI bundle. Centerline spacing follows the board's existing 0.1524 mm QSPI clearance pattern.
- Firmware is unchanged. RP2040's boot ROM and QSPI/XIP hardware use this dedicated pin; QMK pin configuration is not involved.

## Main PCB

### X1203 external power-button pads

- Added TP15 on `PWR_BUTTON` at board coordinate (66.04 mm, 33.655 mm).
- Added TP16 on `GND` at board coordinate (68.84 mm, 33.655 mm).
- Both use `testpad:P1-13`, with a 1.3208 mm plated hole and a 2.159 mm octagonal pad.
- TP15 replaces the existing same-net 0.35 mm via at its coordinate, preserving the original top-to-bottom electrical transition.
- Added top-silkscreen labels: `X1203 BTN`, `PWR`, and `GND`.

Assembly instructions:

1. Use two insulated wires suitable for the enclosure routing.
2. Connect TP15 (`PWR`) and TP16 (`GND`) to the X1203's two-pin external power-button connector.
3. Polarity is not significant for this dry-contact switch connection.
4. Do not connect these pads to an X1203 battery connector or 5 V output connector.
5. Pressing the CMDeck keyboard power button shorts `PWR_BUTTON` to `GND` momentarily, in parallel with the X1203 external-button input.

### DSI 3V3 isolation

- Added JP5 using `CMDeck-Jumpers:SJ_2_NO` at board coordinate (181.94 mm, 46.4796 mm).
- JP5 pad 1 is on `CM5_3.3V`.
- JP5 pad 2 and DSI connector J1 pin 22 are on new net `DSI_3V3`.
- Footprint: two 1.2 x 1.5 mm top pads, 1.5 mm center-to-center, 0.3 mm copper gap, no paste apertures.
- Default assembly state: **OPEN / DO NOT BRIDGE**.
- The documented Waveshare display is powered separately from 5 V and was observed by the creator to back-feed approximately 3 V through DSI when J1.22 was connected. Leave JP5 open for this assembly.
- Bridge JP5 only for a separately verified DSI peripheral that needs host-supplied 3V3 and cannot back-power the carrier.

## Unchanged behavior

- No firmware files changed.
- No existing component placement, board outline, mounting geometry, stackup, connector assignment, or unrelated net membership changed.
- The documented 1.6 mm, four-layer, 1 oz outer/inner stackup file is unchanged.
- Existing upstream fabrication data is unchanged and remains unsafe.

## Validation artifacts

- `tools/validate_rev_a_fixed.py` checks schematic/board part consistency, embedded footprint pads, exact repaired net membership, all unrelated endpoint-to-net assignments, pre-existing component placements, jumper default geometry, and unchanged firmware.
- `verification/upstream-comparison/README.md` explains every source-level difference and the blocked manufacturing comparisons.
