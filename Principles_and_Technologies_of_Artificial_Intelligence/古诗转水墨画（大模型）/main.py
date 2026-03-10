import os
import torch
from accelerate import Accelerator
from accelerate.utils import set_seed
from packaging import version
import accelerate
from diffusers import UNet2DConditionModel
from diffusers.training_utils import EMAModel
from utils import setup_logging, initialize_accelerator, logger
from model_utils import load_all_of_models_schedulers_and_others
from dataset_utils import prepare_dataset, convert_png_to_jpeg
from train import setup_optimizer_and_scheduler, train_loop, save_final_model
from logging_utils import parse_logging_validation_args
from config import parse_args
import swanlab

def main():
    """
    主函数，协调 Stable Diffusion 模型的训练流程。
    """
    args = parse_args()
    if args.random_seed is not None:
        set_seed(args.random_seed)
    accelerator = initialize_accelerator(args)
    if accelerator.is_main_process:
        if args.output_direction is not None:
            os.makedirs(args.output_direction, exist_ok=True)
    setup_logging(args)
    noise_scheduler, tokenizer, text_encoder, vae, unet, ema_unet = load_all_of_models_schedulers_and_others(args)
    train_dataset, train_dataloader = prepare_dataset(args, accelerator, tokenizer)
    optimizer, scheduler = setup_optimizer_and_scheduler(args, unet, train_dataloader, accelerator)
    if version.parse(accelerate.__version__) >= version.parse("0.16.0"):
        def save_model_hook(models, weights, output_direction):
            if accelerator.is_main_process:
                if args.ema:
                    ema_unet.save_pretrained(os.path.join(output_direction, "unet_ema"))
                for i, model in enumerate(models):
                    model.save_pretrained(os.path.join(output_direction, "unet"))
                    weights.pop()
        def load_model_hook(models, input_dir):
            if args.ema:
                load_model = EMAModel.from_pretrained(os.path.join(input_dir, "unet_ema"), UNet2DConditionModel)
                ema_unet.load_state_dict(load_model.state_dict())
                ema_unet.to(accelerator.device)
                del load_model
            for _ in range(len(models)):
                model = models.pop()
                load_model = UNet2DConditionModel.from_pretrained(input_dir, subfolder="unet")
                model.register_to_config(**load_model.config)
                model.load_state_dict(load_model.state_dict())
                del load_model
        accelerator.register_save_state_pre_hook(save_model_hook)
        accelerator.register_load_state_pre_hook(load_model_hook)
    global_step, first_epoch = train_loop(
        args, accelerator, unet, ema_unet, vae, text_encoder, tokenizer,
        train_dataset, train_dataloader, optimizer, scheduler, noise_scheduler
    )
    save_final_model(args, accelerator, unet, ema_unet, text_encoder, vae)
    swanlab.finish()

if __name__ == "__main__":
    convert_png_to_jpeg("./Paint4Poem-Web-famous-subset/images/")
    main()