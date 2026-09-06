"""Demo: full autocomplete + type info for AlibreX via PythonNet 3.

Hover any symbol below in VS Code (with Pylance) to see typed signatures.
Try `alibrex.<Tab>` to browse all 288 exported types.
"""
from alibrex import (
    ADUnits,
    ADObjectType,
    IADSession,
    IADRoot,
    EventManager,
)

def units_demo() -> int:
    return int(ADUnits.AD_MILLIMETERS)

def describe_session(session: IADSession) -> str:
    return f"{session.Name} ({session.SessionType})"

if __name__ == "__main__":
    print("ADUnits.AD_MILLIMETERS =", units_demo())
    print("ADObjectType members:", [n for n in dir(ADObjectType) if n.startswith("AD_")][:5])
    print("IADSession class loaded:", IADSession.__name__)
    print("EventManager class loaded:", EventManager.__name__)
