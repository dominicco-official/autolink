# Patch_Set index

This folder holds every modification AutoLink applies to the vendored JoinABLe
repository (`third_party/JoinABLe`, pinned at the commit recorded in
`third_party/JOINABLE_COMMIT`). The clone itself is kept pristine apart from
these recorded changes, so that applying the Patch_Set to a fresh checkout at
the pinned commit reproduces the vendored tree byte-for-byte with zero rejected
hunks. Each entry consists of one diff file named `NNNN-<slug>.diff` plus a row
in the table below, and each entry records: the file path relative to the
JoinABLe repository root, the unified diff of the change, and a reason for the
change of at least one sentence.

## Entries

None yet. The Patch_Set is empty; the vendored JoinABLe tree is unmodified.
