# Rev A Fixed vs. Upstream Comparison

Baseline: upstream commit `66e5f08` (`origin/main` when the repair branch was created).

## Source netlist differences

### Keyboard

| Item | Upstream | Rev A Fixed | Reason |
|---|---|---|---|
| Flash select net name | `N$12` | `QSPI_SS_N` | Give the repaired dedicated interface an explicit name. |
| Flash select members | U3.1, R4.1, R6.2 | U1.56, U3.1, R4.1, R6.2 | Connect RP2040 `QSPI_SS_N` to W25Q128 `!CS`. |
| Flash select routing | 3 bottom-copper segments | 14 bottom-copper segments | Add one continuous 0.2032 mm trace outside the existing QSPI bundle. |
| Components / footprints | No change | No change | The repair is copper-only. |

No other keyboard signal membership changed.

### Main board

| Item | Upstream | Rev A Fixed | Reason |
|---|---|---|---|
| `PWR_BUTTON` members | U1.92, X1203 `PWR_SW`, J16.B3 | Same plus TP15 | Accessible X1203 button wire pad. |
| `PWR_BUTTON` vias | 5 | 4 | The 0.35 mm via at (66.04, 33.655) is replaced by plated through-hole TP15 at the same coordinate. |
| `GND` members | Existing ground members | Same plus TP16 | Second accessible X1203 button wire pad. |
| DSI J1.22 | Direct member of `CM5_3.3V` | Removed from `CM5_3.3V` | Prevent display back-powering by default. |
| JP5.1 | Absent | `CM5_3.3V` | Host side of series jumper. |
| `DSI_3V3` | Absent | JP5.2 and J1.22 | Isolated connector-side supply net. |
| New board elements | None | TP15, TP16, JP5 | Two wire pads and one normally-open solder jumper. |

No other main-board signal membership changed.

## Footprint differences

- TP15 and TP16 use `testpad:P1-13`: 1.3208 mm plated hole, 2.159 mm octagonal pad.
- JP5 uses `CMDeck-Jumpers:SJ_2_NO`: two 1.2 x 1.5 mm top pads on 1.5 mm centers, producing a 0.3 mm default copper gap. Both pads have paste disabled.
- JP5 contains no copper wire, polygon, or rectangle joining its pads; it is physically normally open.
- Added top silkscreen identifies `X1203 BTN`, `PWR`, and `GND`. JP5 carries its reference designator.

## BOM and pick-and-place comparison

No assembled electrical component was added:

- TP15 and TP16 are plated PCB wire pads.
- JP5 is a bare solder-jumper land pattern.
- All three are DNP and require no purchased part.

Therefore the assembly BOM is intended to remain electrically identical. A Fusion/EAGLE placement export may list TP15, TP16, and JP5 as front-side board elements; those rows must be marked DNP or filtered from the assembler placement list. Exact fresh BOM and front/back placement comparisons are blocked until Fusion/EAGLE export is available.

## Expected fabrication-layer differences

These are source-derived expectations, not substitutes for Gerber comparison:

- Keyboard bottom copper: the new `QSPI_SS_N` route only.
- Main top copper: JP5 pads and separated DSI 3V3 traces.
- Main copper/mask/drill: TP15 and TP16 plated wire pads; TP15 replaces one small via.
- Main top silkscreen: X1203 button labels and JP5 reference.
- Main drill data: remove one 0.35 mm via hit; add two 1.3208 mm plated hits, for a net increase of one drilled hole.
- Main plane clearances/thermals: must be regenerated around both new plated holes by Fusion/EAGLE.

## Existing upstream fabrication files

`git diff 66e5f08 -- pcbs/keyboard/fab pcbs/main\ board/fab boms` is empty. The checked-in Gerbers, drills, BOMs, PnP files, ODB++ data, and zip archives therefore remain the original unsafe upstream outputs. They were deliberately not relabeled or repackaged as corrected exports.

Fresh Gerber, Excellon, BOM, and PnP comparison is **blocked** because Autodesk Fusion/EAGLE 9.7-compatible electronics tooling is not installed on the workstation.
