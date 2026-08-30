"""Geo-Sentry BLE proximity anchor (Part B).

Runs on a SECOND laptop (not the one running the FastAPI backend) that has a
Bluetooth adapter genuinely capable of advertising -- verified working via the
same BluetoothLEAdvertisementPublisher API used here, on a real machine, before
this script was written. The backend's own dev machine failed that same test
with RADIO_NOT_AVAILABLE; not every Windows Bluetooth adapter/driver supports
the peripheral/advertiser role, even when scanning/pairing works fine.

Advertises a fixed manufacturer-data payload continuously. Both inspection
phones (running the Inspection PWA) scan for this exact signature via
navigator.bluetooth.requestLEScan() and report the RSSI they see back to the
backend as relative signal-strength proximity -- never converted into a
fabricated "distance in meters" figure, since no path-loss calibration for
that exists (see docs/research/vault/00 MASTER CONTROL/Geo-Sentry Sourced
Parameter Register.md).

Setup (run once, on the anchor machine):
    pip install winrt-Windows.Devices.Bluetooth.Advertisement ^
                winrt-Windows.Foundation ^
                winrt-Windows.Devices.Bluetooth ^
                winrt-Windows.Storage.Streams ^
                winrt-Windows.Foundation.Collections

Run:
    python ble_anchor.py

Stop with Ctrl+C. If it prints ABORTED instead of STARTED, this machine's
adapter cannot advertise either -- see the RADIO_NOT_AVAILABLE note above and
docs/INDUSTRIAL_ROADMAP.md's Part B entry.
"""

import sys
import time

# Manufacturer ID 0xFFFF is the Bluetooth SIG's reserved "for testing" value --
# real products must register their own, but this is a hackathon prototype
# anchor, not a product. ANCHOR_SIGNATURE is the fixed byte payload the
# Inspection PWA's requestLEScan() filter matches against
# (apps/dashboard/src/InspectionApp.jsx) -- keep these two in sync.
MANUFACTURER_ID = 0xFFFF
ANCHOR_SIGNATURE = b"GSAX"  # "Geo-Sentry Anchor" magic bytes


def main() -> None:
    try:
        from winrt.windows.devices.bluetooth.advertisement import (
            BluetoothLEAdvertisement,
            BluetoothLEAdvertisementPublisher,
            BluetoothLEAdvertisementPublisherStatus,
            BluetoothLEManufacturerData,
        )
        from winrt.windows.storage.streams import DataWriter
    except ImportError as error:
        print(f"SETUP INCOMPLETE -- missing package: {error}")
        print("Run the pip install command in this file's module docstring, then retry.")
        sys.exit(1)

    advertisement = BluetoothLEAdvertisement()
    writer = DataWriter()
    for byte in ANCHOR_SIGNATURE:
        writer.write_byte(byte)
    advertisement.manufacturer_data.append(
        BluetoothLEManufacturerData(MANUFACTURER_ID, writer.detach_buffer())
    )

    publisher = BluetoothLEAdvertisementPublisher(advertisement)

    def on_status_changed(_sender, args) -> None:
        status = args.status
        if status == BluetoothLEAdvertisementPublisherStatus.STARTED:
            print("STARTED -- advertising the Geo-Sentry anchor signature.")
        elif status == BluetoothLEAdvertisementPublisherStatus.ABORTED:
            print(f"ABORTED -- BluetoothError code {int(args.error)}. See this file's docstring.")

    publisher.add_status_changed(on_status_changed)
    publisher.start()

    try:
        print("Anchor running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        publisher.stop()
        print("Stopped.")


if __name__ == "__main__":
    main()
