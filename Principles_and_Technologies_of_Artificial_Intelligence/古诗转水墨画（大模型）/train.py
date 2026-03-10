import math
import os
import torch
import torch.nn.functional as F
import shutil
from contextlib import nullcontext
from tqdm.auto import tqdm
from diffusers import StableDiffusionPipeline
from diffusers.training_utils import compute_dream_and_update_latents, compute_snr
from diffusers.utils.torch_utils import is_compiled_module
from diffusers.optimization import get_scheduler
import swanlab
from accelerate.logging import get_logger

# 创建日志记录器实例
logger = get_logger(__name__, log_level="INFO")

def setup_optimizer_and_scheduler(args, unet, train_dataloader, accelerator):
    """设置优化器和学习率调度器
    
    Args:
        args: 包含训练配置的参数对象
        unet: 需要优化的UNet模型
        train_dataloader: 训练数据加载器
        accelerator: 分布式训练加速器
    
    Returns:
        tuple: (optimizer, lr_scheduler) - 优化器和学习率调度器
    """
    # 如果启用学习率缩放，根据批次大小和设备数调整学习率
    if args.lrscale:
        args.learning_rate = (
            args.learning_rate * args.grad_accum_steps * args.batch_size * accelerator.num_processes
        )
    
    # 创建AdamW优化器
    optimizer_cls = torch.optim.AdamW
    optimizer = optimizer_cls(
        unet.parameters(),
        lr=args.learning_rate,
        betas=(args.adamb1, args.adamb2),  # Adam优化器的beta参数
        weight_decay=args.adam_decay,      # 权重衰减率
        eps=args.adameps,                  # epsilon值防止除零
    )

    # 计算每轮的更新步数
    num_update_steps_per_epoch = math.ceil(len(train_dataloader) / args.grad_accum_steps)
    if args.max_steps is None:
        args.max_steps = args.epochs * num_update_steps_per_epoch

    # 创建学习率调度器
    scheduler = get_scheduler(
        args.scheduler,                    # 调度器类型
        optimizer=optimizer,
        num_warmup_steps=args.warmup_steps * accelerator.num_processes,  # 预热步数
        num_training_steps=args.max_steps * accelerator.num_processes,   # 总训练步数
    )
    
    return optimizer, scheduler

def val_model(vae, text_encoder, tokenizer, unet, args, accelerator, weight_dtype, epoch):
    """执行验证并生成示例图像
    
    Args:
        vae: 变分自编码器用于图像编码/解码
        text_encoder: 文本编码器用于处理提示词
        tokenizer: 分词器用于处理文本输入
        unet: UNet模型
        args: 训练参数配置
        accelerator: 分布式训练加速器
        weight_dtype: 模型权重的数据类型
        epoch: 当前训练轮次
    
    Returns:
        list: 生成的验证图像列表
    """
    logger.info("正在运行验证...")
    
    # 构建Stable Diffusion推理管线
    pipeline = StableDiffusionPipeline.from_pretrained(
        args.model_path,
        vae=accelerator.unwrap_model(vae),
        text_encoder=accelerator.unwrap_model(text_encoder),
        tokenizer=tokenizer,
        unet=accelerator.unwrap_model(unet),
        safety_checker=None,  # 禁用安全检查器以提高速度
        model_revision=args.model_revision,
        model_variant=args.model_variant,
        torch_dtype=weight_dtype,
    )
    
    # 配置推理设备和优化
    pipeline = pipeline.to(accelerator.device)
    pipeline.set_progress_bar_config(disable=True)  # 禁用进度条
    if args.xformers:
        pipeline.xformers()  # 启用xformers优化
        
    # 设置随机数生成器
    generator = None if args.random_seed is None else torch.Generator(device=accelerator.device).manual_seed(args.random_seed)

    # 用于存储生成的图像
    images = []
    
    # 创建验证图像保存目录
    if accelerator.is_main_process:
        validation_dir = os.path.join(args.output_direction, "validation_images")
        os.makedirs(validation_dir, exist_ok=True)

    # 为每个验证提示词生成图像
    for i in range(len(args.validation_prompts)):
        # 处理MPS设备的特殊情况
        if torch.backends.mps.is_available():
            autocast_ctx = nullcontext()
        else:
            autocast_ctx = torch.autocast(accelerator.device.type)
            
        # 生成图像
        with autocast_ctx:
            image = pipeline(args.validation_prompts[i], num_inference_steps=20, generator=generator).images[0]
            
        # 保存图像并记录到swanlab
        if accelerator.is_main_process:
            image.save(os.path.join(validation_dir, f"epoch_{epoch}_prompt_{i}.png"))
        images.append(swanlab.Image(image, caption=f"{i}: {args.validation_prompts[i]}"))

    # 记录到swanlab用于可视化
    swanlab.log({"验证": images})
    
    # 清理内存
    del pipeline
    torch.cuda.empty_cache()
    
    return images

def train_loop(args, accelerator, unet, ema_unet, vae, text_encoder, tokenizer, 
               train_dataset, train_dataloader, optimizer, scheduler, noise_scheduler):
    """执行Stable Diffusion模型的训练循环
    
    该函数实现了完整的训练流程，包括:
    1. 模型和优化器的设备分配与初始化
    2. 训练状态的恢复(如果需要)
    3. 训练循环的执行
    4. 损失计算和优化
    5. 检查点保存
    6. 验证和日志记录
    
    Args:
        args: 包含所有训练配置的参数对象
        accelerator: 分布式训练加速器对象
        unet: 主要训练的U-Net模型
        ema_unet: EMA版本的U-Net模型(可选)
        vae: 用于图像编码/解码的VAE模型
        text_encoder: 用于文本编码的CLIP模型
        tokenizer: 用于文本处理的分词器
        train_dataset: 训练数据集
        train_dataloader: 训练数据加载器
        optimizer: 优化器(通常是AdamW)
        scheduler: 学习率调度器
        noise_scheduler: 噪声调度器，用于扩散过程
        
    Returns:
        tuple: (global_step, first_epoch) - 总训练步数和起始轮次
    """
    # 1. 模型优化配置
    if args.grad_checkpoint:
        unet.enable_gradient_checkpointing()  # 启用梯度检查点以节省显存
    if args.tf32:
        torch.backends.cuda.matmul.allow_tf32 = True  # 启用TF32加速计算
        
    # 2. 准备模型和优化器
    unet, optimizer, train_dataloader, scheduler = accelerator.prepare(
        unet, optimizer, train_dataloader, scheduler
    )
    if args.ema:
        ema_unet.to(accelerator.device)  # 将EMA模型移到正确设备
        
    # 3. 设置模型精度
    weight_dtype = torch.float32
    if accelerator.mixed_precision == "fp16":
        weight_dtype = torch.float16
        args.precision = accelerator.mixed_precision
    elif accelerator.mixed_precision == "bf16":
        weight_dtype = torch.bfloat16
        args.precision = accelerator.mixed_precision
        
    # 4. 将其他模型转移到目标设备和精度
    text_encoder.to(accelerator.device, dtype=weight_dtype)
    vae.to(accelerator.device, dtype=weight_dtype)
    
    # 5. 计算训练步数和轮次
    num_update_steps_per_epoch = math.ceil(len(train_dataloader) / args.grad_accum_steps)
    args.epochs = math.ceil(args.max_steps / num_update_steps_per_epoch)
    
    # 6. 初始化训练追踪器
    if accelerator.is_main_process:
        tracker_config = dict(vars(args))
        tracker_config.pop("validation_prompts")
        accelerator.init_trackers(args.project_name, tracker_config)
        
    # 7. 辅助函数：解包装模型
    def unwrap_model(model):
        model = accelerator.unwrap_model(model)
        model = model._orig_mod if is_compiled_module(model) else model
        return model
        
    # 8. 计算总批次大小并打印训练信息
    total_batch_size = args.batch_size * accelerator.num_processes * args.grad_accum_steps
    logger.info("***** 正在运行训练 *****")
    logger.info(f"  样本数量 = {len(train_dataset)}")
    logger.info(f"  训练轮数 = {args.epochs}")
    logger.info(f"  每个设备的瞬时批次大小 = {args.batch_size}")
    logger.info(f"  总训练批次大小（包括并行、分布式和累积） = {total_batch_size}")
    logger.info(f"  梯度累积步数 = {args.grad_accum_steps}")
    logger.info(f"  总优化步数 = {args.max_steps}")
    
    # 9. 初始化或恢复训练状态
    global_step = 0
    first_epoch = 0
    if args.resume_ckpt:  # 如果需要从检查点恢复
        if args.resume_ckpt != "latest":
            path = os.path.basename(args.resume_ckpt)
        else:
            # 找到最新的检查点
            dirs = os.listdir(args.output_direction)
            dirs = [d for d in dirs if d.startswith("checkpoint")]
            dirs = sorted(dirs, key=lambda x: int(x.split("-")[1]))
            path = dirs[-1] if len(dirs) > 0 else None
            
        if path is None:
            accelerator.print(f"检查点 '{args.resume_ckpt}' 不存在。开始新的训练运行。")
            args.resume_ckpt = None
            initial_global_step = 0
        else:
            # 加载检查点状态
            accelerator.print(f"从检查点 {path} 恢复")
            accelerator.load_state(os.path.join(args.output_direction, path))
            global_step = int(path.split("-")[1])
            initial_global_step = global_step
            first_epoch = global_step // num_update_steps_per_epoch
    else:
        initial_global_step = 0
        
    # 10. 创建进度条
    progress_bar = tqdm(
        range(0, args.max_steps),
        initial=initial_global_step,
        desc="步数",
        disable=not accelerator.is_local_main_process,
    )
    
    # 11. 主训练循环
    for epoch in range(first_epoch, args.epochs):
        train_loss = 0.0
        swanlab.log({"轮次": epoch}, step=epoch)
        
        # 12. 批次训练循环
        for step, batch in enumerate(train_dataloader):
            if batch is None:
                continue
                
            # 13. 梯度累积上下文
            with accelerator.accumulate(unet):
                # 13.1 获取图像潜在表示
                latents = vae.encode(batch["pixel_values"].to(weight_dtype)).latent_dist.sample()
                latents = latents * vae.config.scaling_factor
                
                # 13.2 生成和处理噪声
                noise = torch.randn_like(latents)
                if args.noise_shift:  # 应用噪声偏移
                    noise += args.noise_shift * torch.randn(
                        (latents.shape[0], latents.shape[1], 1, 1), device=latents.device
                    )
                if args.input_noise:  # 应用输入噪声
                    new_noise = noise + args.input_noise * torch.randn_like(noise)
                    
                # 13.3 采样时间步并添加噪声
                bsz = latents.shape[0]
                timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (bsz,), device=latents.device)
                timesteps = timesteps.long()
                noisy_latents = noise_scheduler.add_noise(latents, 
                                                        new_noise if args.input_noise else noise, 
                                                        timesteps)
                
                # 13.4 获取文本编码
                encoder_hidden_states = text_encoder(batch["input_ids"], return_dict=False)[0]
                
                # 13.5 设置预测类型
                if args.prediction_type is not None:
                    noise_scheduler.register_to_config(prediction_type=args.prediction_type)
                    
                # 13.6 确定训练目标
                if noise_scheduler.config.prediction_type == "epsilon":
                    target = noise
                elif noise_scheduler.config.prediction_type == "v_prediction":
                    target = noise_scheduler.get_velocity(latents, noise, timesteps)
                else:
                    raise ValueError(f"未知的预测类型 {noise_scheduler.config.prediction_type}")
                
                # 13.7 应用DREAM训练方法(如果启用)
                if args.dream_training:
                    noisy_latents, target = compute_dream_and_update_latents(
                        unet,
                        noise_scheduler,
                        timesteps,
                        noise,
                        noisy_latents,
                        target,
                        encoder_hidden_states,
                        args.dream_preservation,
                    )
                
                # 13.8 模型预测
                model_pred = unet(noisy_latents, timesteps, encoder_hidden_states, return_dict=False)[0]
                
                # 13.9 计算损失
                if args.snr_weight is None:
                    # 普通MSE损失
                    loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")
                else:
                    # 带SNR权重的损失
                    snr = compute_snr(noise_scheduler, timesteps)
                    mse_loss_weights = torch.stack([snr, args.snr_weight * torch.ones_like(timesteps)], dim=1).min(dim=1)[0]
                    if noise_scheduler.config.prediction_type == "epsilon":
                        mse_loss_weights = mse_loss_weights / snr
                    elif noise_scheduler.config.prediction_type == "v_prediction":
                        mse_loss_weights = mse_loss_weights / (snr + 1)
                    loss = F.mse_loss(model_pred.float(), target.float(), reduction="none")
                    loss = loss.mean(dim=list(range(1, len(loss.shape)))) * mse_loss_weights
                    loss = loss.mean()
                
                # 13.10 处理损失
                avg_loss = accelerator.gather(loss.repeat(args.batch_size)).mean()
                train_loss += avg_loss.item() / args.grad_accum_steps
                
                # 13.11 反向传播和优化
                accelerator.backward(loss)
                if accelerator.sync_gradients:
                    accelerator.clip_grad_norm_(unet.parameters(), args.grad_norm)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                
            # 14. 同步后的操作
            if accelerator.sync_gradients:
                if args.ema:
                    ema_unet.step(unet.parameters())
                progress_bar.update(1)
                global_step += 1
                
                # 14.1 记录训练指标
                swanlab.log({"训练损失": train_loss}, step=global_step)
                swanlab.log({"学习率": scheduler.get_last_lr()[0]}, step=global_step)
                train_loss = 0.0
                
                # 14.2 保存检查点
                if global_step % args.ckpt_steps == 0:
                    if accelerator.is_main_process:
                        # 检查点数量限制
                        if args.ckpt_limit is not None:
                            checkpoints = os.listdir(args.output_direction)
                            checkpoints = [d for d in checkpoints if d.startswith("checkpoint")]
                            checkpoints = sorted(checkpoints, key=lambda x: int(x.split("-")[1]))
                            if len(checkpoints) >= args.ckpt_limit:
                                num_to_remove = len(checkpoints) - args.ckpt_limit + 1
                                removing_checkpoints = checkpoints[0:num_to_remove]
                                logger.info(f"已有 {len(checkpoints)} 个检查点，将移除 {len(removing_checkpoints)} 个检查点")
                                logger.info(f"移除的检查点：{', '.join(removing_checkpoints)}")
                                for removing_checkpoint in removing_checkpoints:
                                    removing_checkpoint = os.path.join(args.output_direction, removing_checkpoint)
                                    shutil.rmtree(removing_checkpoint)
                                    
                        # 保存新检查点
                        save_path = os.path.join(args.output_direction, f"checkpoint-{global_step}")
                        accelerator.save_state(save_path)
                        logger.info(f"状态已保存至 {save_path}")
            
            # 15. 更新进度条
            logs = {"损失": loss.detach().item(), "学习率": scheduler.get_last_lr()[0]}
            progress_bar.set_postfix(**logs)
            
            # 16. 检查是否达到最大步数
            if global_step >= args.max_steps:
                break
                
        # 17. 执行验证(如果配置)
        if accelerator.is_main_process:
            if args.validation_prompts is not None and epoch % args.validation_epochs == 0:
                if args.ema:
                    ema_unet.store(unet.parameters())
                    ema_unet.copy_to(unet.parameters())
                val_model(
                    vae,
                    text_encoder,
                    tokenizer,
                    unet,
                    args,
                    accelerator,
                    weight_dtype,
                    global_step,
                )
                if args.ema:
                    ema_unet.restore(unet.parameters())
                    
    return global_step, first_epoch

def parse_training_args(parser):
    """解析与训练相关的参数"""
    parser.add_argument(
        "--input_noise", type=float, default=0, help="The scale of input perturbation. Recommended 0.1."
    )
    parser.add_argument("--random_seed", type=int, default=None, help="A random_seed for reproducible training.")
    parser.add_argument(
        "--image_size",
        type=int,
        default=512,
        help="The image_size for input images, all images will be resized to this image_size."
    )
    parser.add_argument(
        "--center_crop",
        default=False,
        action="store_true",
        help="Whether to center crop the input images to the image_size."
    )
    parser.add_argument(
        "--random_flip",
        action="store_true",
        help="Whether to randomly flip images horizontally."
    )
    parser.add_argument(
        "--batch_size", type=int, default=16, help="Batch size (per device) for the training dataloader."
    )
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument(
        "--max_steps",
        type=int,
        default=None,
        help="Total number of training steps to perform. If provided, overrides epochs."
    )
    parser.add_argument(
        "--grad_accum_steps",
        type=int,
        default=1,
        help="Number of updates steps to accumulate before performing a backward/update pass."
    )
    parser.add_argument(
        "--grad_checkpoint",
        action="store_true",
        help="Whether to use gradient checkpointing to save memory at the expense of slower backward pass."
    )
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=1e-4,
        help="Initial learning rate (after the potential warmup period) to use."
    )
    parser.add_argument(
        "--lrscale",
        action="store_true",
        default=False,
        help="Scale the learning rate by the number of GPUs, gradient accumulation steps, and batch size."
    )
    parser.add_argument(
        "--scheduler",
        type=str,
        default="constant",
        help='The scheduler type to use. Choose between ["linear", "cosine", "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"]'
    )
    parser.add_argument(
        "--warmup_steps", type=int, default=500, help="Number of steps for the warmup in the lr scheduler."
    )
    parser.add_argument(
        "--snr_weight",
        type=float,
        default=None,
        help="SNR weighting gamma to be used if rebalancing the loss. Recommended value is 5.0."
    )
    parser.add_argument(
        "--dream_training",
        action="store_true",
        help="Use the DREAM training method for more efficient and accurate training."
    )
    parser.add_argument(
        "--dream_preservation",
        type=float,
        default=1.0,
        help="Dream detail preservation factor p (should be greater than 0; default=1.0)."
    )
    parser.add_argument(
        "--use_8bit_adam", action="store_true", help="Whether to use 8-bit Adam from bitsandbytes."
    )
    parser.add_argument(
        "--tf32",
        action="store_true",
        help="Whether to allow TF32 on Ampere GPUs for faster training."
    )
    parser.add_argument("--ema", action="store_true", help="Whether to use EMA model.")
    parser.add_argument(
        "--num_workers",
        type=int,
        default=0,
        help="Number of subprocesses to use for data loading. 0 means data loaded in the main process."
    )
    parser.add_argument("--adamb1", type=float, default=0.9, help="The beta1 parameter for the Adam optimizer.")
    parser.add_argument("--adamb2", type=float, default=0.999, help="The beta2 parameter for the Adam optimizer.")
    parser.add_argument("--adam_decay", type=float, default=1e-2, help="Weight decay to use.")
    parser.add_argument("--adameps", type=float, default=1e-08, help="Epsilon value for the Adam optimizer.")
    parser.add_argument("--grad_norm", default=1.0, type=float, help="Max gradient norm.")
    parser.add_argument(
        "--prediction_type",
        type=str,
        default=None,
        help="The prediction_type for training. Choose between 'epsilon' or 'v_prediction' or leave `None`."
    )
    parser.add_argument("--noise_shift", type=float, default=0, help="The scale of noise offset.")
    parser.add_argument(
        "--precision",
        type=str,
        default="fp16",
        choices=["no", "fp16", "bf16"],
        help="Whether to use mixed precision. Choose between fp16 and bf16 (bfloat16)."
    )

def save_final_model(args, accelerator, unet, ema_unet, text_encoder, vae):
    """
    保存最终模型并运行推理以生成验证图像。

    参数:
        args: 命令行参数
        accelerator: Accelerate 对象
        unet: UNet 模型
        ema_unet: EMA UNet 模型（如果启用）
        text_encoder: 文本编码器模型
        vae: 变分自编码器模型
    """
    accelerator.wait_for_everyone()
    if accelerator.is_main_process:
        unet = accelerator.unwrap_model(unet)
        if args.ema:
            ema_unet.copy_to(unet.parameters())
        pipeline = StableDiffusionPipeline.from_pretrained(
            args.model_path,
            text_encoder=text_encoder,
            vae=vae,
            unet=unet,
            model_revision=args.model_revision,
            model_variant=args.model_variant,
        )
        pipeline.save_pretrained(args.output_direction)