# tools/

## `ble_anchor.py` — BLE proximity anchor (Part B)

Runs on a **second** laptop (not the one running the FastAPI backend) to give
the two inspection phones a fixed BLE signal to measure their relative
proximity against — see the file's own docstring for the full explanation of
why this exists (browsers can't make a phone advertise BLE; real GPS is too
imprecise indoors) and exact setup/run steps.

Quick version:

```bash
pip install winrt-Windows.Devices.Bluetooth.Advertisement winrt-Windows.Foundation winrt-Windows.Devices.Bluetooth winrt-Windows.Storage.Streams winrt-Windows.Foundation.Collections
python ble_anchor.py
```

Confirm it prints `STARTED`, not `ABORTED`, before relying on it for a demo —
not every Windows Bluetooth adapter supports the peripheral/advertiser role
(this repo's own dev machine doesn't; a second, verified-working machine does).
