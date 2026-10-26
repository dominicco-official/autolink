# AutoLink environment specifications

Always attempt the upstream JoinABLe environment first, using `third_party/JoinABLe/environment_cpu.yml`. Record each attempt in `docs/experiments.md`, including the command, date, outcome, and complete error output on failure.

Do not use or create `environment/autolink_cpu_modern.yml` unless the upstream environment creation command or smoke test has failed on two consecutive Windows attempts. Both failures must be logged first, including every package that failed to resolve, install, or import. Only then may `autolink_cpu_modern.yml` be used as the alternative environment specification required by Requirement 2.9.

Install the Python test and schema-validation tools from `environment/requirements-tools.txt`; every dependency in that file is exactly pinned for Python 3.7 compatibility.

Resolved environment lockfiles belong in `environment/lock/` after successful environment creation and verification.
