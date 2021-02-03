"""Generate C++ headers for use in QMK firmware."""

import io

from toolbox.keyboard_pb2 import Keyboard

generator = "github.com/kleinpa/kb"


def make_qmk_header_file(kb):
    if kb.controller == Keyboard.CONTROLLER_PROMICRO:
        pin_names = [
            "D3", "D2", "D1", "D0", "D4", "C6", "D7", "E6", "B4", "B5", "B6",
            "B2", "B3", "B1", "F7", "F6", "F5", "F4"
        ]
    else:
        raise RuntimeError("unknown controller")

    usb_vid = "0xFEED"
    usb_pid = "0x6060"
    usb_ver = "0x0001"

    # Build sets of row and column controller pin indices
    rows = set(k.controller_pin_low for k in kb.keys)
    cols = set(k.controller_pin_high for k in kb.keys)

    # Do a sanity check on controller pins
    if rows & cols:
        raise RuntimeError(
            f"pin in both row and column list rows={rows} cols={cols}")
    if not rows.issubset(range(len(pin_names))):
        raise RuntimeError(f"rows contains out-of-range pin rows={rows}")
    if not cols.issubset(range(len(pin_names))):
        raise RuntimeError(f"Rows contains out-of-range pin cols={cols}")
    if len(set((k.controller_pin_low, k.controller_pin_high)
               for k in kb.keys)) != len(kb.keys):
        raise RuntimeError(f"controller pin index assignments not unique")

    config = {
        "PRODUCT": kb.name,

        # USB Device descriptor
        "VENDOR_ID": usb_vid,
        "PRODUCT_ID": usb_pid,
        "DEVICE_VER": usb_ver,

        # Matrix Definition
        "MATRIX_ROWS": len(rows),
        "MATRIX_ROW_PINS": "{" + ", ".join(pin_names[x] for x in rows) + "}",
        "MATRIX_COLS": len(cols),
        "MATRIX_COL_PINS": "{" + ", ".join(pin_names[x] for x in cols) + "}",
        "DIODE_DIRECTION": "COL2ROW",  # COL2ROW or ROW2COL

        # Other options
        "DEBOUNCE": 5,
    }

    def c_list(xs):
        """Transform a nested list of numbers into a c list literal."""
        if isinstance(xs, str):
            return xs
        try:
            return "{" + ",".join(c_list(x) for x in xs) + "}"
        except TypeError:
            return xs

    matrix = {}
    layout_params = []
    for i, k in enumerate(kb.keys):
        p = f"k{i}"
        layout_params.append(p)
        matrix[(k.controller_pin_low, k.controller_pin_high)] = p

    matrix_layout = [[matrix.get((r, c), "KC_NO") for c in cols] for r in rows]
    config[f"LAYOUT({c_list(layout_params)[1:-1]})"] = (
        f"{c_list(matrix_layout)}")

    fn = io.TextIOWrapper(io.BytesIO())
    print(f"/* generated by {generator} */", file=fn)
    print("#pragma once", file=fn)
    print("#include \"config_common.h\"", file=fn)
    for k, v in config.items():
        print(f"#define {k} {v}", file=fn)
    fn.seek(0)
    return fn.detach()
