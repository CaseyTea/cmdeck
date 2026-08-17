#!/usr/bin/env python3
"""Structural regression checks for the CMDeck Rev A PCB repairs."""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEYBOARD_SCH = ROOT / "pcbs/keyboard/src/Keyboard _Schematic.sch"
KEYBOARD_BRD = ROOT / "pcbs/keyboard/src/Keyboard _Board.brd"
MAIN_SCH = ROOT / "pcbs/main board/src/Main_Board_Schematic.sch"
MAIN_BRD = ROOT / "pcbs/main board/src/Main Board _Board.brd"
UPSTREAM_COMMIT = "66e5f08"


def parse(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def parse_upstream(path: Path) -> ET.Element:
    relative = path.relative_to(ROOT).as_posix()
    source = subprocess.check_output(
        ["git", "show", f"{UPSTREAM_COMMIT}:{relative}"], cwd=ROOT
    )
    return ET.fromstring(source)


def board_signal(root: ET.Element, name: str) -> ET.Element | None:
    return root.find(f".//board/signals/signal[@name='{name}']")


def board_contacts(signal: ET.Element | None) -> set[tuple[str, str]]:
    if signal is None:
        return set()
    return {
        (ref.attrib["element"], ref.attrib["pad"])
        for ref in signal.findall("contactref")
    }


def schematic_pinrefs(root: ET.Element, net_name: str) -> set[tuple[str, str]]:
    refs: set[tuple[str, str]] = set()
    for net in root.findall(f".//schematic/sheets/sheet/nets/net[@name='{net_name}']"):
        refs.update(
            (pin.attrib["part"], pin.attrib["pin"])
            for pin in net.findall(".//pinref")
        )
    return refs


def board_endpoint_nets(root: ET.Element) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for signal in root.findall(".//board/signals/signal"):
        for ref in signal.findall("contactref"):
            result[(ref.attrib["element"], ref.attrib["pad"])] = signal.attrib["name"]
    return result


def schematic_endpoint_nets(root: ET.Element) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for net in root.findall(".//schematic/sheets/sheet/nets/net"):
        for ref in net.findall(".//pinref"):
            result[(ref.attrib["part"], ref.attrib["pin"])] = net.attrib["name"]
    return result


def existing_element_attributes_unchanged(
    upstream: ET.Element, current: ET.Element
) -> bool:
    current_elements = {
        item.attrib["name"]: item.attrib
        for item in current.findall(".//board/elements/element")
    }
    return all(
        current_elements.get(item.attrib["name"]) == item.attrib
        for item in upstream.findall(".//board/elements/element")
    )


def element(root: ET.Element, name: str) -> ET.Element | None:
    return root.find(f".//board/elements/element[@name='{name}']")


def part(root: ET.Element, name: str) -> ET.Element | None:
    return root.find(f".//schematic/parts/part[@name='{name}']")


def package(root: ET.Element, library: str, name: str) -> ET.Element | None:
    return root.find(
        f".//board/libraries/library[@name='{library}']"
        f"/packages/package[@name='{name}']"
    )


def board_references_are_valid(root: ET.Element) -> bool:
    libraries = {
        library.attrib["name"]: library
        for library in root.findall(".//board/libraries/library")
    }
    elements = {
        item.attrib["name"]: item
        for item in root.findall(".//board/elements/element")
    }
    element_pads: dict[str, set[str]] = {}
    for name, item in elements.items():
        library = libraries.get(item.attrib["library"])
        if library is None:
            return False
        footprint = library.find(
            f"./packages/package[@name='{item.attrib['package']}']"
        )
        if footprint is None:
            return False
        element_pads[name] = {
            child.attrib["name"]
            for child in footprint
            if child.tag in {"pad", "smd"}
        }
    for ref in root.findall(".//board/signals/signal/contactref"):
        if ref.attrib["element"] not in element_pads:
            return False
        if ref.attrib["pad"] not in element_pads[ref.attrib["element"]]:
            return False
    return True


def check(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS: {message}")
    else:
        print(f"FAIL: {message}")
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    keyboard_sch = parse(KEYBOARD_SCH)
    keyboard_brd = parse(KEYBOARD_BRD)
    main_sch = parse(MAIN_SCH)
    main_brd = parse(MAIN_BRD)
    upstream_keyboard_sch = parse_upstream(KEYBOARD_SCH)
    upstream_keyboard_brd = parse_upstream(KEYBOARD_BRD)
    upstream_main_sch = parse_upstream(MAIN_SCH)
    upstream_main_brd = parse_upstream(MAIN_BRD)

    for label, schematic, board in (
        ("keyboard", keyboard_sch, keyboard_brd),
        ("main board", main_sch, main_brd),
    ):
        schematic_parts = {
            item.attrib["name"]
            for item in schematic.findall(".//schematic/parts/part")
        }
        board_elements = {
            item.attrib["name"]
            for item in board.findall(".//board/elements/element")
        }
        check(
            board_elements <= schematic_parts,
            f"every {label} board element has a matching schematic part",
            failures,
        )
        check(
            board_references_are_valid(board),
            f"every {label} board contact reference resolves to an embedded footprint pad",
            failures,
        )

    check(
        existing_element_attributes_unchanged(upstream_keyboard_brd, keyboard_brd),
        "all pre-existing keyboard component footprints and placements are unchanged",
        failures,
    )
    check(
        existing_element_attributes_unchanged(upstream_main_brd, main_brd),
        "all pre-existing main-board component footprints and placements are unchanged",
        failures,
    )

    flash_expected_board = {
        ("U1", "56"),
        ("U3", "1"),
        ("R4", "1"),
        ("R6", "2"),
    }
    flash_expected_schematic = {
        ("U1", "QSPI_SS_N"),
        ("U3", "!CS"),
        ("R4", "1"),
        ("R6", "2"),
    }
    flash_board = board_signal(keyboard_brd, "QSPI_SS_N")
    check(
        flash_expected_board == board_contacts(flash_board),
        "keyboard QSPI_SS_N contains exactly U1.56, U3.1, R4.1, and R6.2",
        failures,
    )
    check(
        flash_expected_schematic == schematic_pinrefs(keyboard_sch, "QSPI_SS_N"),
        "keyboard schematic QSPI_SS_N contains exactly the matching logical pins",
        failures,
    )
    check(
        board_signal(keyboard_brd, "N$12") is None
        and not schematic_pinrefs(keyboard_sch, "N$12"),
        "anonymous keyboard flash-select net N$12 is eliminated",
        failures,
    )
    flash_board_endpoints = {("U1", "56"), ("U3", "1"), ("R4", "1"), ("R6", "2")}
    flash_schematic_endpoints = {
        ("U1", "QSPI_SS_N"),
        ("U3", "!CS"),
        ("R4", "1"),
        ("R6", "2"),
    }
    check(
        {
            endpoint: net
            for endpoint, net in board_endpoint_nets(keyboard_brd).items()
            if endpoint not in flash_board_endpoints
        }
        == {
            endpoint: net
            for endpoint, net in board_endpoint_nets(upstream_keyboard_brd).items()
            if endpoint not in flash_board_endpoints
        },
        "all unrelated keyboard board endpoint-to-net assignments match upstream",
        failures,
    )
    check(
        {
            endpoint: net
            for endpoint, net in schematic_endpoint_nets(keyboard_sch).items()
            if endpoint not in flash_schematic_endpoints
        }
        == {
            endpoint: net
            for endpoint, net in schematic_endpoint_nets(upstream_keyboard_sch).items()
            if endpoint not in flash_schematic_endpoints
        },
        "all unrelated keyboard schematic endpoint-to-net assignments match upstream",
        failures,
    )

    for name, net_name in (("TP15", "PWR_BUTTON"), ("TP16", "GND")):
        board_part = element(main_brd, name)
        schematic_part = part(main_sch, name)
        check(
            board_part is not None
            and board_part.get("library") == "testpad"
            and board_part.get("package") == "P1-13",
            f"main-board {name} uses testpad P1-13 footprint",
            failures,
        )
        check(
            schematic_part is not None
            and schematic_part.get("library") == "testpad"
            and schematic_part.get("device") == "PAD1-13",
            f"main schematic {name} uses matching PAD1-13 device",
            failures,
        )
        check(
            (name, "TP") in board_contacts(board_signal(main_brd, net_name)),
            f"main-board {name} is on {net_name}",
            failures,
        )
        check(
            (name, "TP") in schematic_pinrefs(main_sch, net_name),
            f"main schematic {name} is on {net_name}",
            failures,
        )

    wire_pad_package = package(main_brd, "testpad", "P1-13")
    tp_pad = None if wire_pad_package is None else wire_pad_package.find("pad[@name='TP']")
    check(
        tp_pad is not None
        and tp_pad.get("drill") == "1.3208"
        and tp_pad.get("diameter") == "2.159",
        "X1203 wire-pad footprint has a 1.3208 mm plated hole and 2.159 mm pad",
        failures,
    )

    jp5_board = element(main_brd, "JP5")
    jp5_schematic = part(main_sch, "JP5")
    check(
        jp5_board is not None and jp5_board.get("package") == "SJ_2_NO",
        "main-board JP5 uses dedicated SJ_2_NO footprint",
        failures,
    )
    check(
        jp5_schematic is not None and jp5_schematic.get("device") == "",
        "main schematic JP5 uses matching normally-open jumper device",
        failures,
    )
    jumper_package = package(main_brd, "CMDeck-Jumpers", "SJ_2_NO")
    jumper_pads = [] if jumper_package is None else jumper_package.findall("smd")
    jumper_copper = (
        []
        if jumper_package is None
        else [
            item
            for item in jumper_package
            if item.tag in {"wire", "polygon", "rectangle"}
            and item.get("layer") in {"1", "16"}
        ]
    )
    check(
        {pad.get("name") for pad in jumper_pads} == {"1", "2"}
        and all(pad.get("cream") == "no" for pad in jumper_pads)
        and not jumper_copper,
        "JP5 has two no-paste pads and no default copper bridge",
        failures,
    )
    check(
        ("JP5", "1") in board_contacts(board_signal(main_brd, "CM5_3.3V"))
        and ("J1", "22") not in board_contacts(board_signal(main_brd, "CM5_3.3V")),
        "CM5_3.3V terminates at JP5.1 instead of DSI J1.22",
        failures,
    )
    check(
        {("JP5", "2"), ("J1", "22")}
        == board_contacts(board_signal(main_brd, "DSI_3V3")),
        "DSI_3V3 contains only the isolated jumper side and DSI supply pin",
        failures,
    )
    check(
        ("JP5", "1") in schematic_pinrefs(main_sch, "CM5_3.3V")
        and {("JP5", "2"), ("J1", "22")}
        <= schematic_pinrefs(main_sch, "DSI_3V3"),
        "main schematic represents the same DSI 3V3 series split",
        failures,
    )

    main_board_changed_endpoints = {
        ("J1", "22"),
        ("JP5", "1"),
        ("JP5", "2"),
        ("TP15", "TP"),
        ("TP16", "TP"),
    }
    main_schematic_changed_endpoints = main_board_changed_endpoints
    check(
        {
            endpoint: net
            for endpoint, net in board_endpoint_nets(main_brd).items()
            if endpoint not in main_board_changed_endpoints
        }
        == {
            endpoint: net
            for endpoint, net in board_endpoint_nets(upstream_main_brd).items()
            if endpoint not in main_board_changed_endpoints
        },
        "all unrelated main-board endpoint-to-net assignments match upstream",
        failures,
    )
    check(
        {
            endpoint: net
            for endpoint, net in schematic_endpoint_nets(main_sch).items()
            if endpoint not in main_schematic_changed_endpoints
        }
        == {
            endpoint: net
            for endpoint, net in schematic_endpoint_nets(upstream_main_sch).items()
            if endpoint not in main_schematic_changed_endpoints
        },
        "all unrelated main schematic endpoint-to-net assignments match upstream",
        failures,
    )

    firmware_diff = subprocess.run(
        ["git", "diff", "--quiet", UPSTREAM_COMMIT, "--", "firmware"],
        cwd=ROOT,
        check=False,
    ).returncode
    check(firmware_diff == 0, "firmware is byte-for-byte unchanged", failures)

    if failures:
        print(f"\n{len(failures)} validation check(s) failed.")
        return 1
    print("\nAll Rev A Fixed structural checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
