import torch
import transformers
import accelerate
from accelerate.state import AcceleratorState
from diffusers import AutoencoderKL, DDPMScheduler, UNet2DConditionModel
from diffusers.optimization import get_scheduler
from diffusers.training_utils import EMAModel
from diffusers.utils import deprecate
from transformers import CLIPTextModel, CLIPTokenizer
from transformers.utils import ContextManagers
from accelerate.logging import get_logger

# 创建日志记录器
logger = get_logger(__name__, log_level="INFO")

def parse_model_args(parser):
    """解析与模型相关的命令行参数
    
    Args:
        parser: ArgumentParser对象，用于添加命令行参数
    """
    parser.add_argument(
        "--model_path",
        type=str,
        default="./stable-diffusion-v1-5",
        help="预训练模型路径或huggingface.co/models的模型标识符"
    )
    parser.add_argument(
        "--model_revision",
        type=str,
        default=None,
        required=False,
        help="huggingface.co/models预训练模型的修订版本"
    )
    parser.add_argument(
        "--model_variant",
        type=str,
        default=None,
        help="模型变体类型，如fp16等"
    )
    parser.add_argument(
        "--non_ema_model_revision",
        type=str,
        default=None,
        required=False,
        help="非EMA模型的修订版本"
    )

def load_all_of_models_schedulers_and_others(args):
    """加载Stable Diffusion训练所需的所有模型组件
    
    该函数加载以下组件：
    1. 噪声调度器(DDPM) - 用于添加和移除噪声
    2. 分词器(CLIP) - 用于文本处理
    3. 文本编码器(CLIP) - 用于生成文本嵌入
    4. VAE - 用于图像编码和解码
    5. UNet - 核心扩散模型
    6. EMA UNet - 模型参数的指数移动平均版本（可选）
    
    Args:
        args: 包含模型配置的命令行参数对象
        
    Returns:
        tuple: 返回加载的所有模型组件
            - noise_scheduler: 噪声调度器
            - tokenizer: CLIP分词器
            - text_encoder: CLIP文本编码器
            - vae: 变分自编码器
            - unet: U-Net模型
            - ema_unet: EMA版本的U-Net模型（如果启用）
    """
    # 检查废弃的参数使用
    if args.non_ema_model_revision is not None:
        deprecate(
            "non_ema_model_revision!=None",
            "0.15.0",
            message="从 Hub 的修订分支下载 'non_ema' 权重已被弃用。请确保使用 `--model_variant=non_ema` 替代。",
        )

    # 加载噪声调度器
    noise_scheduler = DDPMScheduler.from_pretrained(args.model_path, subfolder="scheduler")
    
    # 加载CLIP分词器
    tokenizer = CLIPTokenizer.from_pretrained(
        args.model_path, subfolder="tokenizer", revision=args.model_revision
    )

    # 创建DeepSpeed Zero优化上下文管理器
    def deepspeed_ban_init():
        """创建DeepSpeed Zero初始化的禁用上下文
        用于临时禁用DeepSpeed Zero优化，确保大模型加载正确
        """
        deepspeed_plugin = AcceleratorState().deepspeed_plugin if accelerate.state.is_initialized() else None
        return [] if deepspeed_plugin is None else [deepspeed_plugin.zero3_init_context_manager(enable=False)]

    # 在禁用DeepSpeed Zero优化的上下文中加载大型模型
    with ContextManagers(deepspeed_ban_init()):
        # 加载CLIP文本编码器
        text_encoder = CLIPTextModel.from_pretrained(
            args.model_path, subfolder="text_encoder", revision=args.model_revision, variant=args.model_variant
        )
        # 加载VAE模型
        vae = AutoencoderKL.from_pretrained(
            args.model_path, subfolder="vae", revision=args.model_revision, _variant=args.model_variant
        )

    # 加载U-Net模型
    unet = UNet2DConditionModel.from_pretrained(
        args.model_path, subfolder="unet", revision=args.non_ema_model_revision
    )

    # 冻结VAE和文本编码器的参数
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    
    # 设置U-Net为训练模式
    unet.train()

    # 可选：创建EMA版本的U-Net
    ema_unet = None
    if args.ema:
        ema_unet = UNet2DConditionModel.from_pretrained(
            args.model_path, subfolder="unet", model_revision=args.model_revision, model_variant=args.model_variant
        )
        # 将U-Net封装在EMA模型中
        ema_unet = EMAModel(ema_unet.parameters(), model_cls=UNet2DConditionModel, model_config=ema_unet.config)

    return noise_scheduler, tokenizer, text_encoder, vae, unet, ema_unet