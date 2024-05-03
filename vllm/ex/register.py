import torch
import types

from typing import Callable, Optional, Union
from vllm.logger import init_logger

logger = init_logger(__name__)

SUPPORTED = set()
FUSABLE = dict()


def operator_name(op: Union[str, Callable]) -> Optional[str]:
    if isinstance(op, str):
        return op
    elif (isinstance(op, types.FunctionType) or
          isinstance(op, types.BuiltinFunctionType) or
          isinstance(op, types.BuiltinMethodType)):
        return f"{op.__module__}.{op.__name__}"
    else:
        return None


def register_supported(op: Union[str, Callable]):
    op_name = operator_name(op)
    if op_name is None:
        raise Exception(f"{op} has unsupported type.")
    logger.info(f"register supported {op_name}")
    SUPPORTED.add(op)


def register_fusable(op: Union[str, Callable], is_compute: bool = False):
    op_name = operator_name(op)
    if op_name is None:
        raise Exception(f"{op} has unsupported type.")
    assert op_name not in FUSABLE or FUSABLE[op_name] == is_compute
    logger.info(f"register fusable {op_name}, is_compute {is_compute}")
    register_supported(op_name)
    FUSABLE[op_name] = is_compute


def register_defaults():
    logger.info("REGISTER DEFAULTS")
    register_fusable('_operator.add')
    register_fusable('_operator.mul')
    register_fusable('_operator.getitem')
    register_fusable('torch.relu')
    register_fusable('torch.nn.functional.silu')
    register_fusable('torch.ops.vllm.silu_and_mul')
    register_fusable('torch.matmul', True)
    register_fusable('torch._C._nn.linear', True)


register_defaults()