# Install on another Mac

## Requirements

- macOS 12 or later
- Logi Options+ installed and running normally
- two compatible Easy-Switch devices configured for matching host slots
- `/usr/bin/python3`

Confirm the system Python before installing:

```sh
/usr/bin/python3 --version
```

## Verify the download

Download both the release ZIP and `SHA256SUMS` into the same directory, then:

```sh
cd ~/Downloads
shasum -a 256 -c SHA256SUMS
```

The command must report `OK` for the ZIP.

## Install

1. Expand the ZIP.
2. Copy `Switch to Host 1.app`, `Switch to Host 2.app`, and
   `Switch to Host 3.app` to `/Applications`.
3. Keep a built-in trackpad, physical Easy-Switch control, or spare input
   device available for the first test.
4. Control-click the required app in Finder and choose **Open**. If macOS still
   blocks it, use **System Settings → Privacy & Security → Open Anyway**.
5. Opening the app immediately requests a switch and shows no window.

The apps use identity-free ad-hoc signatures. They are not notarized because
Apple notarization requires a registered developer identity. Do not bypass a
warning unless the checksum matches and you trust this repository.

## Assign to a device button

In Logi Options+:

1. Select the customizable button or key.
2. Choose **Open Application**.
3. Select the matching `/Applications/Switch to Host N.app`.

Install the launchers on every Mac from which you want to initiate a switch.
The physical host numbers must describe the same computers on both devices.
