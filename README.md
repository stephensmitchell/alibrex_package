# alibrex package

[![PyPI version](https://img.shields.io/pypi/v/alibrex.svg)](https://pypi.org/project/alibrex/)
[![Python versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://pypi.org/project/alibrex/)

`alibrex` is a Python wrapper for the Alibre Design V29+ **AlibreX** automation API. The native AlibreX is a COM interface exposed to .NET
`alibrex` turns it into a typed, idiomatic Python module.

**Features**

- **Full IDE support.** Every interface, enum, and method is declared in PEP 561 type stubs - autocomplete, hover docs, and type-checking work out of the box in VS Code, PyCharm, or any pyright/Pylance-aware editor.
- **Single namespace.** Everything is at the top level: `CurrentPart()`, `CurrentAssembly()`, `connect()`, plus ~280 typed AlibreX interfaces and enums.
- **Example and demo driven.** The repository includes Jupyter notebooks, plus dozens of test scripts, demos and reference utilities.

## Installation

### From PYPI

[alibrex ](https://pypi.org/project/alibrex/)

**What's in this repository**

| Folder | Description |
|---|---|
| `notebooks/` | Jupyter tutorial sequence (00-11) plus topic references (connecting, cleanup, 2D/3D sketches, parameters, configurations, property reading, PDM) |
| `demo/` | Self-verifying scripts - feature CRUD, sketch / assembly constraints, parameters, configurations, events, profile library |
| `demo/muffler/` | Bundled multi-part industrial assembly used by the `asm_*` and `crud_13..18*` demos |
| `demo/profiles/` | Profile library (steel, wood, threads, pipe) consumed by the `prof_*` demos |
| `demo/cad-files/` | Reference CAD artifacts referenced by the demos |
| `examples/` | Demonstration scripts - numbered intro `00..27`, plus the subfolders below |
| `examples/advanced/` | Reference geometry, 2D/3D sketch showcases, import/export utilities |
| `examples/advanced/py/` | Python implementations |
| `examples/advanced/md/` | Companion markdown originals for each script |
| `examples/ported/` | Ports of the official AlibreScript samples |
| `examples/ported/library/` | Standalone utilities (gear generator, STL exporter, equation sketcher, etc.) |
| `examples/probes/` | Property-probe reports for the major object types |
| `examples/pdm/` | PDM (Product Data Management) walk-through - 13 progressive scripts: connect - safes - property defs / classes / templates - projects / libraries / folder tree - file properties + version history - locked-file scan, session ↔ PDM cross-ref, full Program.cs port |
| `examples/_sample_files/` | Sample `.AD_PRT` / `.AD_ASM` materialized on first use by file-loading examples |

**Requirements**

- Windows + a licensed installation of Alibre Design (V29 or newer)
- Old versions of Alibre Design may work, but are not tested
- Python 3.9-3.13
- `pythonnet>=3.0,<4` (installed automatically)

`AlibreX.dll` is not redistributed at import time `alibrex` locates it by checking, in order, the `$ALIBREX_DLL` env var, the Windows registry (`AlibreX.AutomationHook` COM ProgID, then `HKLM\SOFTWARE\Alibre, Inc.\Alibre Design\…\HomeDirectory`), and finally a `%ProgramFiles%\Alibre Design*\Program\AlibreX.dll` 

see `notebooks/diagnose_setup.ipynb` to inspect what each source returns on your machine.

**Quick start**

Open Alibre Design and any part document, then:

```python
from alibrex import CurrentPart

part = CurrentPart()
print(part.Name, part.FeatureCount, part.Bodies.Count)
```

See `notebooks/00_hello.ipynb` and `notebooks/connect_methods.ipynb` to get oriented.

**License**

MIT.
