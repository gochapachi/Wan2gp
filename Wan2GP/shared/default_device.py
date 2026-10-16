# Copyright (c) 2026 DeepBeepMeep - part of WanGP, WanGP Community License 2.0 (see LICENSE.txt)
from __future__ import annotations

import os
import sys

from collections.abc import MutableSequence


def _arg_name_to_option(arg_name: str) -> str:
    arg_name = str(arg_name or "").strip()
    if not arg_name:
        return ""
    return arg_name if arg_name.startswith("--") else f"--{arg_name}"


def _cuda_visible_device(device: str) -> str:
    device = str(device or "").strip().lower()
    if device.startswith("cuda:"):
        device = device.split(":", 1)[1]
    return device if device.isdigit() else ""


def _rewrite_arg_value(argv: MutableSequence[str], option: str, value: str) -> None:
    for index, arg in enumerate(argv):
        if arg == option and index + 1 < len(argv):
            argv[index + 1] = value
            return
        if str(arg).startswith(f"{option}="):
            argv[index] = f"{option}={value}"
            return


def patch_torch_default_device():
    try:
        import torch
        if hasattr(torch, "get_default_device"):
            orig_get = torch.get_default_device
            def safe_get_default_device():
                try:
                    ctx = getattr(torch._GLOBAL_DEVICE_CONTEXT, "device_context", None)
                    if ctx is not None:
                        device = ctx.device
                        if device.index is not None:
                            return device
                        return torch.tensor([]).device
                    return torch.device("cpu")
                except Exception:
                    return torch.device("cpu")
            torch.get_default_device = safe_get_default_device

        if hasattr(torch, "set_default_device"):
            orig_set = torch.set_default_device
            def safe_set_default_device(device):
                orig_set(device)
                if device is None and hasattr(torch._GLOBAL_DEVICE_CONTEXT, "device_context") and torch._GLOBAL_DEVICE_CONTEXT.device_context is None:
                    try:
                        delattr(torch._GLOBAL_DEVICE_CONTEXT, "device_context")
                    except AttributeError:
                        pass
            torch.set_default_device = safe_set_default_device
    except Exception:
        pass


patch_torch_default_device()


def set_default_cuda_device_from_arg(arg_name: str, default_device: str = "cuda:0") -> bool:
    patch_torch_default_device()
    option = _arg_name_to_option(arg_name)
    if not option:
        return False
    argv = sys.argv
    for index, arg in enumerate(argv[1:], start=1):
        if arg == option and index + 1 < len(argv):
            visible_device = _cuda_visible_device(argv[index + 1])
            break
        if str(arg).startswith(f"{option}="):
            visible_device = _cuda_visible_device(str(arg).split("=", 1)[1])
            break
    else:
        return False

    if not visible_device:
        return False
    os.environ["CUDA_VISIBLE_DEVICES"] = visible_device
    _rewrite_arg_value(argv, option, default_device)
    return True

