# The Mouse Is Coming Too

**Switch compatible Logitech Easy-Switch keyboards and mice together on macOS.**

One action sends two supported devices to the same Easy-Switch host. It is a
small, local alternative for mixed-generation setups that do not qualify for
Logitech's native Enhanced Easy-Switch—including the tested combination of an
MX Keys S and the original 2015 MX Master.

> Retirement request denied.

This independent project is not affiliated with, sponsored by, or endorsed by
Logitech.

## Download

Download the latest macOS ZIP and `SHA256SUMS` from
[GitHub Releases](https://github.com/ensoenso/the-mouse-is-coming-too/releases/latest).
The archive contains:

- `Switch to Host 1.app`
- `Switch to Host 2.app`
- `Switch to Host 3.app`

Each app contains its own copy of the switching code. It does not refer to the
repository or the computer on which it was built. See [INSTALL.md](INSTALL.md)
for checksum verification, Gatekeeper, and first-run instructions.

## What it solves

Many Logitech keyboards and mice can each remember several computers, but
switching normally means pressing controls on both devices. The included apps
invoke the two-device Easy-Switch action already installed with Logi Options+.
Choose a host once and the keyboard and mouse leave together.

Useful search terms for the same problem include multi-device switching for
Logitech peripherals, switching an MX keyboard and MX Master together,
Easy-Switch with Bolt and Unifying Receiver devices, and synchronized keyboard
and mouse host switching.

## Compatibility

Requirements:

- macOS 12 or later
- Logi Options+ installed and its Plugin Service running
- `/usr/bin/python3` (included with many macOS installations and Apple command-line tools)
- exactly two devices exposed by Options+' `Easy-Switch 2 Devices` action
- matching host-slot assignments on both devices

Verified end to end:

- MX Keys S and first-generation MX Master
- both connected over Bluetooth
- Logi Options+ 2.7.970334 and Plugin Service 6.4.1.3246

Bolt, Bluetooth, and legacy Unifying Receiver configurations may work when
Options+ exposes both devices to the action, but receiver type alone does not
guarantee compatibility. The original MX Master is verified as a legacy device;
its Unifying connection path has not yet been tested by this project.

Run the non-mutating compatibility check:

```sh
/usr/bin/python3 ./switch_pair.py status
```

If exactly two intended devices appear, the launcher apps can select them
automatically. The command-line client also supports explicit selectors.

## Install and assign

Copy the three apps to `/Applications`. In Logi Options+, assign a customizable
button or key to **Open Application**, then choose the app for the required
host. Opening an app immediately requests the switch; no window is shown.

You can also enable the included Karabiner-Elements rule to map these physical
keyboard chords:

- right Option + right Command + 1 → host 1
- right Option + right Command + 2 → host 2
- right Option + right Command + 3 → host 3

For switching in both directions, install the launchers on each Mac. Keep a
physical Easy-Switch control, built-in trackpad, or spare input device available
during initial testing.

## Command line

Inspect compatible choices:

```sh
/usr/bin/python3 ./switch_pair.py status
```

Preview and then execute a switch to physical host slot 2:

```sh
/usr/bin/python3 ./switch_pair.py switch 2
/usr/bin/python3 ./switch_pair.py switch 2 --execute
```

If Options+ exposes more than two choices, select the pair explicitly:

```sh
/usr/bin/python3 ./switch_pair.py switch 2 \
  --first "DEVICE NAME" \
  --second "OTHER DEVICE" \
  --execute
```

## How it works

The client connects only to the local Plugin Service installed by Options+,
discovers choices for its two-device Easy-Switch action, and invokes that fixed
action with a host slot. It does not patch Options+, modify firmware, enable a
debugger, automate the UI, install a daemon, or open a network connection.

The service events confirm that both commands were emitted; they are not
hardware acknowledgements. Commands are sequential rather than atomic, so a
failure can leave only one device switched. The client never retries an
uncertain execution automatically.

## Privacy and security

The normal client:

- opens no network connection or listener
- collects and transmits no telemetry
- stores no device, account, or usage data
- needs no administrator, Accessibility, Automation, or debug permission
- reads device display names and model identifiers only in memory
- modifies no Logitech files, databases, firmware, or socket permissions

The source intentionally exposes no general-purpose raw request command. See
[SECURITY.md](SECURITY.md) for reporting and trust-model details.

## Build and test

```sh
make test
make audit
make dist
```

`make dist` creates three self-contained app bundles, applies identity-free
ad-hoc signatures, and writes a ZIP plus SHA-256 checksum under `dist/`.

## Limitations

- The local Plugin Service protocol is undocumented and may change.
- Downloaded apps are ad-hoc signed, not Developer ID signed or notarized.
- The apps require exactly two action-compatible devices.
- Two identical models may not be distinguishable through the action.
- Device reconnection is not confirmed by the service response.
- This release supports macOS only.

## License and trademarks

MIT. See [LICENSE](LICENSE).

Logitech, Logi, and their logos are trademarks or registered trademarks of
Logitech Europe S.A. and/or its affiliates in the United States and/or other
countries. All other trademarks are the property of their respective owners.
