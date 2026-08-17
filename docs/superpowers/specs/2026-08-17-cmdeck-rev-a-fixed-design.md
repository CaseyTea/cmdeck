# CMDeck Rev A Fixed Design

## Scope

Correct only the three PCB defects documented in the upstream README. Preserve unrelated electrical, mechanical, manufacturing, and firmware behavior.

## Keyboard flash chip select

Rename the anonymous flash-select net `N$12` to `QSPI_SS_N` and connect RP2040 U1 pin `QSPI_SS_N` (physical pad 56) to it. The same net must contain W25Q128JVSIM U3 pin `!CS` (physical pad 1), pull-up R4 pin 1, and BOOT-series resistor R6 pin 2.

Route the new pad-56 connection on the keyboard bottom copper using the existing 0.2032 mm QSPI width. Follow the outside of the existing QSPI bundle with the board's 0.1524 mm clearance instead of crossing another QSPI trace.

No firmware changes are permitted because this is RP2040's dedicated external-flash interface.

## X1203 power-button pads

Add two enlarged plated through-hole wire/test pads to the main board:

- TP15: `PWR_BUTTON`
- TP16: `GND`

Use the existing `testpad:TP` device with its `PAD1-13` device / `P1-13` package: one 1.3208 mm plated hole in a 2.159 mm octagonal pad. Place the pair outside the X1203 module footprint and label the board silkscreen `X1203 BTN`, `PWR`, and `GND`. TP15 replaces an existing same-net 0.35 mm via so the original top-to-bottom connection remains intact without stacking a solder pad over a via.

TP15 is wired in parallel with the existing keyboard power switch and X1203 `PWR_SW` pad. TP16 connects to ground. The external two-pin X1203 power-button connector is wired to these pads without polarity; pressing the keyboard switch produces a momentary short between them.

Both test pads are DNP PCB features, not BOM line items or pick-and-place parts.

## DSI 3V3 isolation jumper

Add main-board JP5 as a dedicated two-terminal, normally-open solder jumper with two 1.2 x 1.5 mm top SMD pads separated by a 0.3 mm copper gap. It has no paste apertures and is not an assembled component.

Insert JP5 in series immediately before DSI connector J1 pin 22:

- JP5 pad 1: `CM5_3.3V`
- JP5 pad 2 and J1 pin 22: `DSI_3V3`

Default state is open. Do not apply solder. Closing JP5 is optional only for a separately verified DSI peripheral that requires host-supplied 3V3 and cannot back-power the carrier.

## Verification and fabrication policy

Use XML/netlist assertions before and after editing. Validate that the Eagle schematic and board agree on every new part, footprint, and target net. Compare BOM, pick-and-place, drill, Gerber, and logical netlist outputs against upstream and explain every change.

Run Autodesk Fusion/EAGLE ERC and DRC and export fresh manufacturing data when the tool is available. If it is unavailable or any CAD/export check remains incomplete, `FABRICATION_READINESS.md` must conclude **DO NOT FABRICATE** and identify the missing verification explicitly.
