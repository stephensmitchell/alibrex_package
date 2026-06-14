"""Shared helpers for the PDM examples.

A few PDM members are typed as a plain ``Object`` (for example
``IADPDMSafeRecycleBin.Item(i)``). AlibreX returns those as raw COM
objects, which the alibrex bridge can't auto-wrap - so attribute access
on them fails. ``as_interface`` casts such a raw object to a known
AlibreX interface so it behaves like any other typed alibrex object.
"""
from __future__ import annotations

from typing import Any

from alibrex._com_bridge import _ComProxy, _resolve_alibrex_type


def as_interface(com_obj: Any, interface: Any) -> Any:
    """Cast a raw COM object to a typed AlibreX interface.

    ``interface`` may be an alibrex interface class (e.g. ``IADPDMFolder``)
    or its name as a string, with or without the ``"AlibreX."`` prefix.
    Returns ``None`` if ``com_obj`` is ``None``.
    """
    if com_obj is None:
        return None
    if isinstance(interface, str):
        name = interface if "." in interface else f"AlibreX.{interface}"
        clr_type = _resolve_alibrex_type(name)
        if clr_type is None:
            raise ValueError(f"Unknown AlibreX interface: {interface!r}")
    else:
        import clr  # provided by pythonnet, already loaded by alibrex
        #Todo: "GetClrType" is not a known attribute of module "clr"
        clr_type = clr.GetClrType(interface)
    return _ComProxy(com_obj, clr_type)


def as_folder(com_obj: Any) -> Any:
    """Cast a raw COM object (e.g. a recycle-bin item) to ``IADPDMFolder``."""
    return as_interface(com_obj, "IADPDMFolder")
