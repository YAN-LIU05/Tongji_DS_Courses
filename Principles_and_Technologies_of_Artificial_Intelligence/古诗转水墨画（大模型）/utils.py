import logging
import os
import torch
from accelerate import Accelerator
from accelerate.logging import get_logger
from accelerate.state import AcceleratorState
from accelerate.utils import ProjectConfiguration, set_seed
import swanlab
from swanlab.integration.accelerate import SwanLabTracker

logger = get_logger(__name__, log_level="INFO")

def setup_logging(args):
    """
    配置日志记录，包括终端输出和文件日志。

    参数:
        args: 命令行参数，包含输出目录等配置
    """
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
    )
    log_file_handler = logging.FileHandler("log.txt", mode="a", encoding="utf-8")
    log_file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    transformers_logger = logging.getLogger("transformers")
    diffusers_logger = logging.getLogger("diffusers")
    for handler in transformers_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            transformers_logger.removeHandler(handler)
    for handler in diffusers_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            diffusers_logger.removeHandler(handler)
    transformers_logger.addHandler(log_file_handler)
    diffusers_logger.addHandler(log_file_handler)
    transformers_logger.setLevel(logging.INFO)
    diffusers_logger.setLevel(logging.INFO)
    print(torch.cuda.is_available())
    print(torch.cuda.get_device_name(0))

def initialize_accelerator(args):
    """
    初始化 Accelerate 对象，用于分布式训练和混合精度设置。

    参数:
        args: 命令行参数，包含训练配置

    返回:
        accelerator: 配置好的 Accelerate 对象
    """
    logging_direction = os.path.join(args.output_direction, args.logging_direction)
    accelerator_project_config = ProjectConfiguration(project_dir=args.output_direction, logging_dir=logging_direction)
    swanlab.init(
        project="SD-Poem",
        experiment_name="SD1-5_古诗图像生成",
        description="基础模型：sd-v1.5；数据集：Paint4Poem-Web-famous-subset；用于古诗生成图像",
    )
    swanlab_tracker = SwanLabTracker(
        "SD-Poem",
        experiment_name="SD1-5_古诗图像生成",
        description="基础模型：sd-v1.5；数据集：Paint4Poem-Web-famous-subset；用于古诗生成图像",
    )
    accelerator = Accelerator(
        gradient_accumulation_steps=args.grad_accum_steps,
        mixed_precision=args.precision,
        log_with=swanlab_tracker,
        project_config=accelerator_project_config,
    )
    if torch.backends.mps.is_available():
        accelerator.native_amp = False
    logger.info(accelerator.state, main_process_only=False)
    return accelerator