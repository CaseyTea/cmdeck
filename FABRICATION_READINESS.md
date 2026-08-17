# CMDeck Rev A Fixed Fabrication Readiness

## Conclusion

**DO NOT FABRICATE.**

The three source-level electrical repairs are implemented and pass structural checks, but the required Autodesk Fusion/EAGLE verification and fresh manufacturing export have not been completed. Existing upstream fabrication outputs remain unsafe.

## Completed evidence

- Both corrected schematic files and both corrected board files parse as well-formed Eagle 9.7 XML.
- Every board element has a corresponding schematic part.
- Every board signal contact reference resolves to a real pad in its embedded footprint.
- Every pre-existing component footprint and placement matches upstream.
- Every unrelated schematic and board endpoint-to-net assignment matches upstream.
- Keyboard `QSPI_SS_N` contains exactly the required functional endpoints, including RP2040 pad 56.
- Main-board TP15 and TP16 exist in both schematic and board on `PWR_BUTTON` and `GND` respectively.
- JP5 is represented consistently in schematic and board as a series split between `CM5_3.3V` and `DSI_3V3`.
- JP5 has no default copper bridge and no paste apertures.
- Local copper inspection found and corrected an initial wire-pad placement conflict; the final plated-hole locations are clear of non-target routed copper in both outer layers by source geometry inspection.
- Firmware is byte-for-byte unchanged from upstream commit `66e5f08`.
- `git diff --check` reports no whitespace errors.

## ERC result

**NOT RUN - BLOCKED.** Autodesk Fusion/EAGLE is not installed or discoverable in `/Applications`, the user Applications directory, `/opt`, `/usr/local`, `/Users/Shared`, or Spotlight metadata on this workstation.

The Python structural validator is not an ERC substitute. It does not evaluate Eagle pin electrical types, supply conflicts, or schematic warnings.

## DRC result

**NOT RUN - BLOCKED.** The Autodesk routing/design-rule engine is unavailable.

Source-level geometry review is not a DRC substitute. It does not prove every copper-to-copper, copper-to-edge, mask-sliver, annular-ring, differential-pair, or plane-clearance rule.

## Fabrication outputs

**NOT GENERATED - BLOCKED.** No fresh Gerber, Excellon, ODB++, BOM, or pick-and-place export has been produced.

The checked-in files under `pcbs/keyboard/fab/` and `pcbs/main board/fab/` remain byte-for-byte upstream artifacts. They do not contain these repairs and must not be sent to a fabricator.

## Remaining required work

1. Open each corrected `.sch`/`.brd` pair together in Autodesk Fusion/EAGLE 9.7-compatible electronics tooling and confirm forward/back annotation consistency.
2. Inspect all newly added library objects and exact board placement visually in the native editor.
3. Re-pour polygons on both boards.
4. Run ERC and resolve or explicitly waive every warning.
5. Run DRC using the original board rules and resolve or explicitly waive every violation.
6. Export fresh Gerber X2 and Excellon data for both boards.
7. Export fresh BOM plus front/back pick-and-place outputs for both boards. Mark TP15, TP16, and JP5 DNP.
8. Compare every new manufacturing file with upstream as outlined in `verification/upstream-comparison/README.md`.
9. Inspect the corrected exports in an independent Gerber viewer, including layer registration, board outline, mask openings, JP5's open gap, TP15/TP16 drills, and the keyboard CS trace.
10. Update this document to `FABRICATE` only after all preceding evidence passes.

## Assembly defaults after verification

- Keyboard: no rework wire; the U1.56-to-U3.1 CS connection is native copper.
- X1203 button: solder two wires to TP15 (`PWR`) and TP16 (`GND`) and connect them to the X1203 external-button input.
- DSI JP5: leave open for the documented externally powered Waveshare display.
