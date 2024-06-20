"""Utilities for selecting and loading models."""
import contextlib
import functools
from typing import Callable, Tuple, Type

import torch
from torch import nn

from vllm.config import ModelConfig
from vllm.model_executor.models import ModelRegistry


@contextlib.contextmanager
def set_default_torch_dtype(dtype: torch.dtype):
    """Sets the default torch dtype to the given dtype."""
    old_dtype = torch.get_default_dtype()
    torch.set_default_dtype(dtype)
    yield
    torch.set_default_dtype(old_dtype)


def get_model_architecture(
        model_config: ModelConfig) -> Tuple[Type[nn.Module], str]:
    architectures = getattr(model_config.hf_config, "architectures", [])
    # Special handling for quantized Mixtral.
    # FIXME(woosuk): This is a temporary hack.
    if (model_config.quantization is not None
            and model_config.quantization != "fp8"
            and "MixtralForCausalLM" in architectures):
        architectures = ["QuantMixtralForCausalLM"]

    for arch in architectures:
        model_cls = ModelRegistry.load_model_cls(arch)
        if model_cls is not None:
            return (model_cls, arch)
    raise ValueError(
        f"Model architectures {architectures} are not supported for now. "
        f"Supported architectures: {ModelRegistry.get_supported_archs()}")


def get_architecture_class_name(model_config: ModelConfig) -> str:
    return get_model_architecture(model_config)[1]


def handle_oom(section_name: str) -> Callable:

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except torch.cuda.OutOfMemoryError as e:
                msg = f"CUDA OutOfMemoryError occurred in: {section_name}\n"
                msg += "Possible solutions:\n"
                msg += "1. Use more devices with tensor_parallel_size\n"
                msg += "2. Use a quantized checkpoint to reduce memory usage\n"
                msg += "3. Use a machine with more device memory\n"
                raise torch.cuda.OutOfMemoryError(msg) from e

        return wrapper

    return decorator
