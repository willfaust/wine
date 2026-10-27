# Madeira update to Wine 11.20

This branch merges the upstream `wine-11.20` tag, commit
`7298a818b79446bae153b8d5aa27235ab3703bf9`, into the existing Madeira
Wine PR chain through `df1c5ea51e194937ac204bc3120922dc56a61bec` (#64).
The original upstream and fork commits remain in the history.

The paired Madeira source update is required. Do not deploy this Wine revision
with native libraries or PE DLLs from Wine 11.4.

## Mobile compatibility choices

- `WINE_IOS` uses `unix_private_ios.h`. It keeps the TEB-resident thread state,
  syscall frame offsets, Mach stack layout and FEX integration used by Madeira.
  Its `get_thread_data()` view lets updated shared Unix sources use that same
  state. Desktop Wine uses the upstream header and thread storage.
- Madeira keeps its existing GnuTLS/LibTomCrypt bcrypt backend. The iOS build
  does not supply the SymCrypt backend introduced upstream. Configure still
  supports the retained TomCrypt source. This is a deliberate exception to the
  upstream update, not a SymCrypt port.
- Keep per-process WoW64 address windows, pointer conversion, keyed events,
  suspend hooks, memory limits, shared futex queues and fastsync. Keep the
  fixes from #60, #62, #63 and #64.
- Adapt XInput and DirectInput to the updated HID interfaces while keeping
  Madeira's host controller, foreground, vibration and battery paths.
- Keep mobile event/semaphore bookkeeping with the new server object API.

The retained mobile native kernel interface means this is not a port of every
upstream Unix-kernel change to iOS. In particular, the mobile loader and thread
implementation still come from Madeira's existing native source copies.

## Validation and merge gates

The paired Madeira document records the native archive and adapter checks.
The Wine checks in `tools/tests` cover GDI publication, blocking I/O APC routing,
WoW64 window atoms, UCRT policy, orphan locks, async cancellation and the new
iOS thread-data view. These are host checks, not device or game results.

Keep this update as a draft until a complete matching DLL package is built and
tested with the paired native archives. Test 64-bit and WoW64 launch, child
processes, exception and suspend paths, controller input, mouse capture,
GDI/OpenGL/Vulkan rendering, TLS/certificate import and export, and media on an
actual iPad. Repeat standalone and LiveContainer runs. Record device, OS,
game, commit and result. Retain the prior matched package for rollback.
