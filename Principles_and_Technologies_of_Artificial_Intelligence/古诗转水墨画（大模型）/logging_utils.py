import argparse
from accelerate.logging import get_logger

logger = get_logger(__name__, log_level="INFO")

def parse_logging_validation_args(parser):
    """解析与日志和验证相关的参数"""
    parser.add_argument(
        "--validation_prompts",
        type=str,
        nargs="+",
        default=None,
        help="A set of prompts evaluated every `--validation_epochs` and logged to `--log_to`. If not provided, loaded from validation_prompts.txt."
    )
    parser.add_argument(
        "--output_direction",
        type=str,
        default="sd-model-finetuned-poem",
        help="The output directory where the model predictions and checkpoints will be written."
    )
    parser.add_argument(
        "--cache_direction",
        type=str,
        default=None,
        help="The directory where the downloaded models and datasets will be stored."
    )
    parser.add_argument(
        "--logging_direction",
        type=str,
        default="logs",
        help="TensorBoard log directory."
    )
    parser.add_argument(
        "--log_to",
        type=str,
        default="tensorboard",
        help='The integration to report results and logs to. Supported: "tensorboard", "wandb", "comet_ml", or "all".'
    )
    parser.add_argument(
        "--validation_epochs",
        type=int,
        default=1,
        help="Run validation every X epochs."
    )
    parser.add_argument(
        "--project_name",
        type=str,
        default="poem2image-fine-tune",
        help="The project_name for Accelerator.init_trackers."
    )
    parser.add_argument(
        "--ckpt_steps",
        type=int,
        default=5000,
        help="Save a checkpoint of the training state every X updates."
    )
    parser.add_argument(
        "--ckpt_limit",
        type=int,
        default=None,
        help="Max number of checkpoints to store."
    )
    parser.add_argument(
        "--resume_ckpt",
        type=str,
        default=None,
        help="Whether to resume training from a previous checkpoint. Use a path or 'latest'."
    )
    parser.add_argument(
        "--xformers", 
        action="store_true", 
        help="Whether to use xformers."
    )
    parser.add_argument(
        "--local_rank", 
        type=int, default=-1, 
        help="For distributed training: local_rank"
    )