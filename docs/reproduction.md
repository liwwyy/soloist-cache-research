# Experimental reproduction

These are snapshots of the working research probes, not a finished downloader. They require an authorized Soloist session and the exact pinned Linux x86_64 binary. GDB offsets are validated against the binary hash by `run_track.py`.

Requirements: Python 3, GDB with Python support, FFmpeg, and `cryptography` available both to Python and GDB's embedded Python. Obtain Soloist from Spotify. The pinned binary is not redistributed. A newer build will require fresh analysis rather than bypassing the hash check.

## Workspace

From the cloned repository:

```
python -m pip install -r requirements.txt
mkdir -m 700 .soloist-investigation
cp tools/*.py .soloist-investigation/
```

The probe snapshots intentionally use this private workspace layout. Keep the API key in a local file outside Git. Pass its path using `--api-key-file`; do not put its value in a command you intend to share. The runner redacts that value from its captured output, but diagnostics can still contain account information.

Follow Spotify's [pairing instructions](https://developer.spotify.com/documentation/soloist) for a device using `.soloist-investigation/data` as its data directory. The experimental runner restores that paired session. It uses its own cache directory under `.soloist-investigation/tracks/TRACK_ID/cache`.

The inspected binary was at `/tmp/soloist-investigation/soloist`; use `--binary /absolute/path/to/soloist` to select another location containing the exact same build.

## Populate and identify the cache

Start the selected track briefly so Soloist can populate its cache. Do not assume a short run downloads the complete file: connection speed and cache state matter. A partial cache cannot produce a complete export.

For example, after pairing:

```
python .soloist-investigation/run_track.py TRACK_ID \
  --binary /absolute/path/to/soloist \
  --api-key-file /absolute/path/to/local-key.txt \
  --seconds 25 --probe page_probe.py
```

This initial run also captures pages during playback. `--seconds` is a process timeout, not a completeness guarantee. The runner can change the active Spotify Connect device.

Collect storage parameters from a cached run:

```
python .soloist-investigation/run_track.py TRACK_ID \
  --binary /absolute/path/to/soloist \
  --api-key-file /absolute/path/to/local-key.txt \
  --seconds 8 --probe storage_probe.py
```

Pause at the initialized content transform:

```
python .soloist-investigation/run_track.py TRACK_ID \
  --binary /absolute/path/to/soloist \
  --api-key-file /absolute/path/to/local-key.txt \
  --seconds 12 --probe decrypt_probe.py
```

Find storage parameters that reproduce the observed content-input prefix:

```
python tools/find_storage_parameters.py .soloist-investigation/tracks/TRACK_ID
```

This writes a private `outer-results.json`. A match establishes prefix consistency; complete container validation is still required.

## Bulk transformation

```
python .soloist-investigation/run_track.py TRACK_ID \
  --binary /absolute/path/to/soloist \
  --api-key-file /absolute/path/to/local-key.txt \
  --seconds 25 --probe decrypt_probe.py --export
```

The export script selects the largest matching cached file, verifies that its unwrapped prefix agrees with the fresh context, allocates a buffer in Soloist and invokes the native content transform once. Output: private `native-decrypted.bin` and a timing/result JSON file. `native-export-error.txt` records failures. Older error files can remain; check timestamps and the actual debugger output.

For the demonstrated stream, the main Ogg audio begins at byte 167, after a separate normalization stream. Do not assume that offset for every format or track. Use `extract_ogg` in `tools/offline_cache_decrypt.py` to require consecutive pages, CRC validity and EOS before writing an export. Confirm the result with `ffprobe` and a full `ffmpeg -v error -i exported.ogg -f null -` decode. Renaming or converting a Vorbis stream to `.flac` does not make the source lossless.

## Offline reconstruction

`tools/offline_cache_decrypt.py` accepts a private JSON bundle and output path. The bundle contains:

- `cache_file`: local cache-file path.
- `cache_sha256`: SHA-256 of that exact cache file.
- `storage_key`, `storage_iv`: captured AES parameters encoded as hexadecimal.
- `storage_offset`: start of the encrypted bytes in that file.
- `keystream_file`: path relative to the bundle directory.
- `audio_offset`: validated start of the main Ogg audio in the transformed stream.

No working bundle or keystream is distributed. For the experiment, the content keystream was the bytewise XOR of the unwrapped encrypted bytes and their successful native plaintext output. Its length must match that encoded stream. This is equivalent in storage cost to retaining the export; it is a proof of independent reconstruction, not compact key extraction.

```
python tools/offline_cache_decrypt.py /private/path/material.json exported.ogg
```

This script does not invoke Soloist or access the network. Reproduction of the live native stage still requires Spotify authorization. Complete new-track preparation without Soloist has not been demonstrated.

## Local validation tests

```
python -m unittest discover -s tests -v
```

Fixtures are synthetic container pages, not copyrighted music. They test integrity checks and rejection behavior; they do not constitute independent replication of the native reverse-engineering result.
