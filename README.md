<!-- markdownlint-disable MD029 MD033 MD041 -->
<p align="center">
    <img src="assets/freecad-logo.png" alt="FreeCAD logo" width="300">
</p>

<h1 align="center">FreeCAD Weekly Updater</h1>

<p align="center">
    <a href="https://github.com/Franky1/FreeCAD-Weekly-Updater/stargazers">
        <img src="https://img.shields.io/github/stars/Franky1/FreeCAD-Weekly-Updater?style=flat-square" alt="GitHub stars">
    </a>
    <a href="https://github.com/Franky1/FreeCAD-Weekly-Updater/issues">
        <img src="https://img.shields.io/github/issues/Franky1/FreeCAD-Weekly-Updater?style=flat-square" alt="GitHub issues">
    </a>
    <a href="https://github.com/Franky1/FreeCAD-Weekly-Updater/commits/main">
        <img src="https://img.shields.io/github/last-commit/Franky1/FreeCAD-Weekly-Updater?style=flat-square" alt="Last commit">
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
    </a>
    <a href="https://docs.astral.sh/uv/">
        <img src="https://img.shields.io/badge/managed%20with-uv-5C6AC4?style=flat-square" alt="Managed with uv">
    </a>
    <a href="https://docs.astral.sh/ruff/">
        <img src="https://img.shields.io/badge/lint-ruff-D7FF64?style=flat-square" alt="Linted with Ruff">
    </a>
    <a href="https://mypy-lang.org/">
        <img src="https://img.shields.io/badge/type%20checked-mypy-1A73E8?style=flat-square" alt="Type checked with mypy">
    </a>
    <a href="LICENSE">
        <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License">
    </a>
</p>

<p align="center"><em>Keep your local FreeCAD weekly build updated with one command</em></p>

## Features :sparkles:

- Installable Python package with a `freecad-weekly-updater` CLI command
- Requires Python >= `3.11`
- No third-party runtime libraries
- Tested on Windows 11 with `x86_64` architecture

## Issues :warning:

Only supports Windows 11 with `x86_64` architecture, not compatible with other operating systems or architectures yet.

## Installation :inbox_tray:

### Using uv (recommended)

Install directly from GitHub into an isolated tool environment:

```bash
uv tool install git+https://github.com/Franky1/FreeCAD-Weekly-Updater.git
```

Or add it as a dependency in your own `uv` managed project:

```bash
uv add git+https://github.com/Franky1/FreeCAD-Weekly-Updater.git
```

### Using pip

```bash
pip install git+https://github.com/Franky1/FreeCAD-Weekly-Updater.git
```

## Usage :rocket:

1. Navigate to the folder where you want FreeCAD to be installed:

```bash
cd C:\FreeCADweekly
```

2. Run the updater:

```bash
freecad-weekly-updater
 ```

The latest FreeCAD weekly build will be downloaded and extracted into the current directory.

3. When a new FreeCAD version is released (usually on a weekly basis on each Wednesday), run the same command again to update.
4. For automation, schedule `freecad-weekly-updater` with a weekly task (e.g. Windows Task Scheduler or a cron job).

## License :page_facing_up:

This project is licensed under the MIT License.

Copyright (c) 2026 Franky1

See [LICENSE](LICENSE) for the full license text.
