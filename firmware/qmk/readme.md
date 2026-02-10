

⚠️ Copy the `cmdeck` folder to your qmk directory → `qmk_firmware/keyboards/cmdeck`
____

Flashing example for this keyboard:
s
    qmk flash -kb cmdeck -km default

See the [build environment setup](https://docs.qmk.fm/#/getting_started_build_tools).
Brand new to QMK? Start with our [Complete Newbs Guide](https://docs.qmk.fm/#/newbs).

## Bootloader

Enter the bootloader in 3 ways:

* **Bootmagic reset**: Hold down the key at top right and plug in the keyboard
* **Physical reset button**: Briefly press the button on the the PCB
* **Keycode in layout**: Press the key mapped to `QK_BOOT` if it is available
