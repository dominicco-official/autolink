# AutoLink browser demo
`run_demo.cmd` (or `conda run -n autolink-cad python webapp\server.py`) -> http://127.0.0.1:8777. Local only, no authentication.

- Top bar: dropdown of joint sets already extracted; the search box accepts any of the 1,926 test-split ids (extracted from the archive on demand, needs 7-Zip and `data/j1.0.0.7z`).
- Step strip: Dataset -> 1 JoinABLe -> 2 Reconstruct -> 3 Verify -> 4 Classify -> 5 Place -> 6 Relations -> 7 Edit. Next/Back or arrow keys.
- Live vs stored: steps 1 and 3-6 run on the server when their files are missing or when you press "Re-run ... now"; step 7 is always live. Step 2 runs the LLM if `AUTOLINK_LLM_PROVIDER` + credentials are set, otherwise "Request from the agent" writes a REQUEST.json for a human/agent to answer by writing `recon/recon_<id>/part_N.py`.
- Left: three.js viewer (pink = JoinABLe pick, green = designer ground truth, orange = both / shoulder faces). Right: the step's files, or the parameter editor at step 7.
