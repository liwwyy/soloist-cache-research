# Soloist cache research

**AI-assisted research into local, faster-than-real-time export of cached Spotify audio through Spotify Soloist.** The experiments, reverse engineering and code were developed with an OpenAI Codex AI assistant, directed by the repository owner. This is a single-machine research result, not an independently replicated implementation.

We recovered a complete 274.192-second track from a populated Soloist cache. Bulk content decryption took about **0.135 seconds**. Starting Soloist, initializing the track context and exporting took **3.13 seconds**. The output preserved the encoded Ogg Vorbis pages without transcoding or capturing audio output.

The tested account delivered **320 kbps Vorbis**, including when the lossless preference was selected. We did not obtain or demonstrate source FLAC export.

## What was demonstrated

| Result | Evidence | Limit |
| --- | --- | --- |
| Complete source-format export | 2,662 consecutive Ogg pages; all CRCs valid; EOS present; complete FFmpeg decode passed | One pinned Soloist build and one full bulk-export track |
| Faster-than-real-time processing | 11,383,181 bytes processed in 0.134967 seconds; run including setup took 3.13 seconds | Cache population time excluded; uses an initialized Soloist context |
| Offline reconstruction of a prepared cache | Separate Python process reproduced the byte-identical output in approximately 3.14–3.17 seconds | Requires previously saved track-specific material, including a file-sized keystream |
| Delivery quality check | Three tracks exposed Vorbis headers reporting nominal 320,000 bits/s | No verified lossless delivery; the reason was not independently established |

**This does not establish a generic offline decryptor for previously unprepared caches.** The saved content keystream is roughly as large as the encoded track, so keeping it offers little storage benefit over keeping the exported audio.

## How it works

There are two layers to distinguish:

1. Soloist's storage layer transforms cache-file bytes. Capturing the storage cipher's schedule and per-file IV allowed AES-CTR removal of that layer with Python's `cryptography` package.
2. Soloist's content decryptor transforms the resulting encoded-stream ciphertext. We located its native entry point, paused when Soloist had initialized the track context, and called it over the entire unwrapped cache in one operation.

The decoded container begins with a Spotify normalization Ogg stream. For the tested track, removing that 167-byte stream leaves the original encoded audio pages. Completeness was established using page sequence, CRC, end-of-stream and final granule checks, followed by an actual FFmpeg decode.

Read [the technical findings](docs/findings.md), [experimental reproduction notes](docs/reproduction.md), [machine-readable measurements](docs/measurements.json), and [AI disclosure](AI_USAGE.md).

## Locality and detection

The export code runs locally. Initial preparation still uses Soloist's Spotify authentication, track authorization and audio downloads. Starting playback is needed for the demonstrated setup; listening to the whole track is not. The entire file must be available in the cache before a complete bulk export can succeed.

The separate offline reconstruction script reads only local files and needs no Soloist process or account login. The tested offline process had a Python audit hook rejecting socket operations and subprocess creation. That check was not a network audit of the native Soloist preparation stage.

**Detectability is untested.** We did not audit Soloist's complete telemetry, diagnostics, debugger checks or Spotify's server-side detection. Local processing is not evidence of invisibility or account safety.

## Scope and distribution

This repository contains research documentation and experimental scripts. It contains no Spotify binaries, credentials, account/session data, cache files, decryption bundles, keystreams or exported music. Obtain Soloist directly from [Spotify](https://developer.spotify.com/documentation/soloist/reference/downloads-and-updates).

The scripts use binary-specific addresses and fail the runner's SHA-256 check on other builds. This is not a maintained compatibility promise for later Soloist versions.

## Credits

- [Spotify Soloist](https://github.com/spotify/soloist): the playback engine inspected.
- [Spotifast](https://github.com/crmne/spotifast): integration documentation and the initial lead.
- [Music Assistant's Soloist backend](https://github.com/music-assistant/server/tree/dev/music_assistant/providers/spotify_connect/soloist): quality-preference research used for the tests.
- [casualsnek/onthespot](https://github.com/casualsnek/onthespot), [ots-downloader/onthespot](https://github.com/ots-downloader/onthespot) and [librespot-python](https://github.com/justin025/librespot-python): comparison of the older key-request and decryption path. Their code was not copied into this repository.
- [foonerd/alsa_soloist_connect](https://github.com/foonerd/alsa_soloist_connect): its audio shim was evaluated in an unsuccessful pacing experiment; that shim is not redistributed here.

Original repository code and documentation are MIT licensed. Upstream software retains its own licenses and terms.
