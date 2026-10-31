# Findings and evidence

Experiment date: 2026-11-01. Platform: Linux x86_64.

## Pinned binary

Official Soloist version: `1.3.10.31`, build date `20261030`.

SHA-256: `3805746df067ebd586b9bdbd84e54fe49090df200ab430da2d7d29949ce2b540`.

The ELF binary is stripped, but retains readable strings and some dynamic symbols. Stripping alone does not establish deliberate obfuscation. We did not fully classify its protection or recover its source.

## Addresses established experimentally

Offsets are relative to the executable's mapping with file offset zero. They are not portable API entry points.

| Offset | Observed role | Relevant arguments/state |
| --- | --- | --- |
| `0x119a487` | Ogg page checksum-success branch | `RAX` points to a complete page before subsequent instructions overwrite it |
| `0x1175cf0` | Format-sniffing helper | Buffer in `RDI`, size in `RSI`; the observed call can describe the normalization stream rather than the main audio |
| `0xe562e1` | Storage cipher IV-set call site | Cipher object in `RDI`, 16-byte IV in `RSI`; storage context and nested schedule were captured here |
| `0x10f9400` | Initialized track content transform | `RDI`: context; `RSI`: byte offset; `RDX`: input; `RCX`: output; `R8`: length |

At the content entry point, the observed input did not appear directly in the on-disk cache. Removing the separately observed storage layer reproduced the exact content-input prefix. Bulk native transformation then produced a complete, validated source container. This is stronger evidence than simply finding an audio signature in arbitrary output.

## Full-track evidence

Target: `spotify:track:6AI3ezQ4o3HUoP6Dhudph3` — “Not Like Us,” Kendrick Lamar.

- Native operation input/output buffer: 11,383,181 bytes.
- Removed normalization stream: 167 bytes.
- Source export: 11,383,014 bytes, Ogg Vorbis, 44,100 Hz stereo, nominal 320 kbps.
- Pages: 2,662, consecutive sequence numbers, every CRC valid.
- End-of-stream present; final granule: 12,091,871.
- Duration: 274.192086 seconds.
- Full FFmpeg decode: passed without decoding errors.
- Export SHA-256: `4307c961669a30f354e41a235d0ec5e8f31f0fd2a1f978b4fbd0df97c789724f`.

The export hash is included as a measurement; the recording itself is not distributed. Container integrity and duration checks do not independently prove the provenance of Spotify's master. Attribution to this track comes from the controlled Soloist session and track identifier.

## Timing boundaries

Bulk native call: approximately 0.135 seconds. Starting the debugger and Soloist, restoring the session, initializing the requested track and exporting: 3.13 seconds. The cached file was already populated. These numbers do not measure a cold network download or a statistical performance distribution.

Soloist was stopped at the beginning of playback, and the entire encoded file was processed directly. This avoids waiting for the audio device to consume the track. The exported Ogg does not use a PCM capture path.

Offline reconstruction took approximately 3.14–3.17 seconds and produced a byte-identical result. A Python audit hook rejected socket operations and subprocess creation during that run. This check applies to that Python reconstruction process, not the preceding Soloist session or its diagnostics.

## What offline means here

The offline script has a cache, a storage key/IV and a content keystream saved for this specific encoded stream. It unwraps storage encryption, applies the keystream and validates the output.

The keystream was derived from the known input/output of a successful native transformation. It is file-sized and offers little storage benefit over keeping the export. This does not establish extraction of a compact content key, a generic master key, or preparation of an unseen track without Soloist.

## Negative and inconclusive experiments

- Both OnTheSpot repositories examined delegated Spotify streaming to librespot-python and selected Vorbis. Track identifiers were not cryptographic keys. No Soloist cache extractor was found in those inspected paths.
- 264 distinct AES initialization candidates did not reveal audio when tested directly against the stored cache with selected legacy-IV/offset hypotheses. The later-discovered storage layer explains why those direct tests were insufficient.
- Searches for the legacy librespot IV in two writable-memory snapshots found no matches; this was not an exhaustive history or proof of absence.
- Periodic memory scans recovered genuine CRC-valid Ogg pages, but left gaps. Intercepting the parser's CRC-success branch allowed complete export during playback.
- One counter-mode trace ended in a GDB internal error. It was not treated as exhaustive evidence about Soloist's cipher implementation.
- A PulseAudio-to-ALSA null-output shim and a modified poll wait did not remove Soloist's pacing. The successful accelerated method instead calls the content transform directly.
- Selecting quality tier 5 produced 320 kbps Vorbis for “Not Like Us,” “Blinding Lights,” and “Shape of You.” Actual FLAC delivery was not obtained. Account/region limitations were not independently established by these tests.

## Unresolved

Generic offline preparation of an unseen cached track, compact content-key recovery, other Soloist builds/platforms, actual source-FLAC export, and Spotify's ability to detect this activity remain unverified.
