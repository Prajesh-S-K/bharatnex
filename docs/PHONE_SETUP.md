# Inspection phone setup

## Supported demonstration devices

- Unit Alpha: OnePlus Nord CE5, Android 16, OxygenOS
  `CPH2717_16.0.5.1002(EX01B100P01)`.
- Unit Bravo: Moto G86 Power 5G, Android 16, 2712×1220,
  `W1VNS36H.60-82-6`.

## Connect

1. Put the laptop and both phones on the same private Wi-Fi or laptop hotspot.
2. Start the prototype. The environment check prints the phone URL.
3. Open `http://<laptop-ip>:5173/inspection` in Chrome on each phone.
4. Select Alpha on the OnePlus and Bravo on the Moto, then enter the prototype PIN.
5. In Chrome, choose **Add to Home screen** to install the PWA.

The default closed-network demonstration PIN is `2468`. Override it before a public demo:

```text
SMART_MINE_DEMO_PIN=<your-local-pin>
SMART_MINE_GATEWAY_KEY=<your-local-gateway-key>
```

Keep these values in the local environment; never commit them.

## BLE-anchor proximity scan (Part B)

Requires a separate second laptop running `tools/ble_anchor.py` (its own
Bluetooth adapter must support advertising — this repo's own dev machine
doesn't; test with `ble_advertise_test.py` first if unsure) and a one-time
Chrome flag on each phone:

1. On each phone, open `chrome://flags/#enable-experimental-web-platform-features`
   and set it to **Enabled**, then restart Chrome. Re-check this before a demo —
   it can reset on a Chrome update.
2. Start `tools/ble_anchor.py` on the second laptop and confirm it prints
   `STARTED`, not `ABORTED`.
3. Open the Inspection PWA on each phone as usual, tap **Start proximity scan**
   in the header.
4. The Field Proximity panel on the dashboard should show real RSSI values for
   both units within 30 seconds, updating as the phones move relative to the
   anchor. This is relative signal strength only, never a distance in meters —
   no path-loss calibration exists for that.

## Offline behaviour

The PWA caches its shell and the current assignment. If Wi-Fi drops, it displays OFFLINE,
retains the assignment and queues lifecycle updates. It retries when the browser reports that
the connection has returned. Keep the page open during a demonstration for the best result.

## Reset a phone

Use the change-unit icon in the phone header. If necessary, clear site data for the laptop URL
in Chrome settings and reload the page.
