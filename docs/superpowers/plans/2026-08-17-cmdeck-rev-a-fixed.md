# CMDeck Rev A Fixed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the three documented CMDeck PCB defects while preserving unrelated behavior and producing an evidence-based fabrication-readiness decision.

**Architecture:** Make minimal native Eagle XML changes to the paired schematic/board sources. Use structural netlist tests as the regression harness, then use Autodesk Fusion/EAGLE for ERC, DRC, and manufacturing exports if available.

**Tech Stack:** Autodesk Eagle/Fusion XML (`.sch`, `.brd`), Python standard-library XML validation, Gerber X2, Excellon, CSV, pick-and-place text.

**Spec:** `docs/superpowers/specs/2026-08-17-cmdeck-rev-a-fixed-design.md`

## Global Constraints

- Work only on branch `rev-a-fixed`.
- Preserve unrelated electrical, mechanical, and firmware behavior.
- Keep schematic and board files mutually consistent.
- Do not modify firmware unless electrical evidence requires it.
- Do not claim fabrication readiness while ERC, DRC, export, or comparison evidence is missing.

---

### Task 1: Structural regression validator

**Files:**
- Create: `tools/validate_rev_a_fixed.py`

**Interfaces:**
- Consumes: the four Eagle source files.
- Produces: exit-zero structural validation with a human-readable assertion summary.

- [x] Write assertions for the required keyboard CS membership, main-board power pads, DSI series split, footprint defaults, and unchanged firmware tree hash.
- [x] Run the validator against upstream and confirm it fails for the three missing repairs.
- [x] Keep the validator as the repeatable source/netlist regression check.

### Task 2: Keyboard flash CS repair

**Files:**
- Modify: `pcbs/keyboard/src/Keyboard _Schematic.sch`
- Modify: `pcbs/keyboard/src/Keyboard _Board.brd`

**Interfaces:**
- Consumes: existing U1, U3, R4, R6, and QSPI routing.
- Produces: net `QSPI_SS_N` containing U1.56, U3.1, R4.1, and R6.2.

- [x] Add U1 `QSPI_SS_N` to the existing flash-select net in the schematic and rename the net.
- [x] Add U1 pad 56 to the board signal and route it around the outside of the existing bottom-layer QSPI bundle.
- [x] Run XML parsing and the keyboard validator; confirm the CS assertion passes.

### Task 3: Main-board X1203 wire pads

**Files:**
- Modify: `pcbs/main board/src/Main_Board_Schematic.sch`
- Modify: `pcbs/main board/src/Main Board _Board.brd`

**Interfaces:**
- Consumes: `PWR_BUTTON`, `GND`, and existing schematic device `testpad:PAD1-13` / package `P1-13`.
- Produces: plated through-hole TP15 (`PWR_BUTTON`) and TP16 (`GND`) with explicit silkscreen assembly labels.

- [x] Add TP15 and TP16 parts and schematic instances on the UPS/interconnect sheet.
- [x] Add their pin references to `PWR_BUTTON` and `GND`.
- [x] Add the used P1-13 package to the board's embedded testpad library and place both pads outside the X1203 footprint.
- [x] Route TP15 to the existing `PWR_BUTTON` trace and connect TP16 to ground.
- [x] Run XML parsing and the power-pad validator.

### Task 4: Main-board DSI 3V3 isolation

**Files:**
- Modify: `pcbs/main board/src/Main_Board_Schematic.sch`
- Modify: `pcbs/main board/src/Main Board _Board.brd`

**Interfaces:**
- Consumes: `CM5_3.3V` and DSI J1 pin 22.
- Produces: JP5 pad 1 on `CM5_3.3V`, JP5 pad 2 and J1.22 on `DSI_3V3`, default open.

- [x] Add a dedicated two-pad normally-open solder-jumper package, symbol, and device.
- [x] Place JP5 directly in the existing J1.22 trace and split that trace into the two named nets.
- [x] Add the schematic instance and series net split.
- [x] Run XML parsing and the DSI validator.

### Task 5: Manufacturing outputs and comparisons

**Files:**
- Update: `pcbs/keyboard/fab/`
- Update: `pcbs/main board/fab/`
- Create: `verification/upstream-comparison/`

**Interfaces:**
- Consumes: corrected Eagle sources and immutable upstream files from commit `66e5f08`.
- Produces: Gerber, Excellon, BOM, front/back PnP, hashes, and explained comparisons.

- [ ] Run Fusion/EAGLE ERC and DRC with the repository design rules. **Blocked: Fusion/EAGLE is unavailable.**
- [ ] Export fresh Gerber and Excellon files for both boards. **Blocked: Fusion/EAGLE is unavailable.**
- [ ] Export BOM and front/back pick-and-place files for both boards. **Blocked: Fusion/EAGLE is unavailable.**
- [x] Compare source logical nets and source-derived expected aperture/feature, drill, BOM, and placement differences against upstream.
- [x] Do not synthesize or relabel upstream outputs as fresh exports; record the native-CAD deliverables as blocked.

### Task 6: Release documentation and final verification

**Files:**
- Create: `REV_A_FIXED_CHANGELOG.md`
- Create: `FABRICATION_READINESS.md`

**Interfaces:**
- Consumes: all source, validation, ERC/DRC, export, and comparison evidence.
- Produces: exact assembly instructions and an unambiguous fabricate/do-not-fabricate conclusion.

- [x] Document exact nets, pins, footprints, jumper defaults, wiring, and assembly instructions.
- [x] Document every source-derived output difference and every missing native-export verification.
- [x] Run the full structural validator, XML parser, git diff checks, and checked-in fabrication-tree comparison.
- [x] Conclude `DO NOT FABRICATE` because CAD and manufacturing checks remain blocked.
