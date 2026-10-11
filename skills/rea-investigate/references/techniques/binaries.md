# Native, Android, managed and firmware techniques

Load only for the matching target modality: S06-S08 or S13. Default is **static**; no untrusted execution, flashing or device login.

## S06 - Native PE / ELF / Mach-O

1. Record bytes, SHA-256, architecture, ABI, OS, sections and mitigation/loader context. Choose a real available provider with `rea providers --json`; do not infer availability from installation path.
2. Seed from an observed symbol, string, procedure name, address or XREF. Under the installed CLI, typical entry points include `rea analyze`, `rea search`, `rea trace`, `rea function`, `rea xrefs`, `rea decompile` with `--provider <id> --json` (check `--help`).
3. Walk callers, callees, branches and data writes until inputs, returns, conditions, error cases and side effects are described. Compare decompiler pseudocode to disassembly and offsets. Indirect dispatch and decompiler ambiguities remain open.
4. Do not claim to recover original source; on stripped/encrypted/misaligned code, report what the provider could not parse.

## S07 - Android APK

1. Verify APK/archive structure by contents; hash it. Inspect manifest entry points, exported components, package identifiers and DEX contents.
2. Check `rea inspect-android-package --help` and JDK/JADX availability. `rea inspect-android-package <apk> --json` can begin inventory; `rea inspect-android-class` and `rea inspect-android-method` require exact class, method and potentially overload selection (check help).
3. Trace manifest/intent/entry activity → methods → storage, permissions, services, interfaces. Flag reflection, dynamic loading, WebView and JNI; a JNI boundary may activate S06 for a matching `.so` build.
4. Static method availability is not evidence of actual invocation. Dynamic testing is separate, permitted, and requires a controlled emulator/device.

## S08 - .NET managed

1. Verify PE/CLI metadata (not merely `.exe`/`.dll` filename), and hash exact build. `rea inspect-managed-artifact <assembly> --json` begins inventory.
2. Use `rea inspect-managed-members --help` and declared method selectors. Collect CIL, method/field signatures, refs, call sites and exception paths. Note token identity is build-local.
3. Inspect P/Invoke with `rea inspect-managed-native-boundaries --help`; existence of the import declaration doesn't establish resolved export or execution. If matched with a native file, open S06.
4. Identify NativeAOT, IL2CPP, obfuscated or missing-body boundaries honestly.

## S13 - Firmware image

1. Hash source image, identify model/build if supplied; perform byte-level signatures without execution. Do not flash or run carved components.
2. Check installed REA firmware support and safe tools only on supported host. Prefer a read-only extractor in a fresh restricted output directory; prevent path traversal, untrusted symlinks and decompression bombs.
3. Record original byte offsets, carve name, digest, architecture guess, extraction warnings and percent/regions not interpreted. Strings alone do not establish a boot path.
4. Investigate one justified nested component through S03/S06/S09 (S09 only after separate execution approval). A carved file's existence does not show the device uses it.

## General gates

If the host or provider cannot perform this branch, mark `blocked` with exact missing dependency; continue with safe inventory and report the gap. Sources must be build-specific and cite offsets/tokens/class/method addresses, not only tool names.
