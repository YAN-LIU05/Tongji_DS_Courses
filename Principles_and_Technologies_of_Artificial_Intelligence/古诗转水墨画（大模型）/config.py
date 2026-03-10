import argparse
import os
from model_utils import parse_model_args
from dataset_utils import parse_dataset_args
from train import parse_training_args
from logging_utils import parse_logging_validation_args

def parse_args():
    """解析所有命令行参数"""
    parser = argparse.ArgumentParser(description="Training script for Stable Diffusion with Paint4Poem dataset.")
    
    # 调用分布在各模块的参数解析函数
    parse_model_args(parser)
    parse_dataset_args(parser)
    parse_training_args(parser)
    parse_logging_validation_args(parser)
    
    args = parser.parse_args()
    
    # 处理 local_rank
    env_local_rank = int(os.environ.get("LOCAL_RANK", -1))
    if env_local_rank != -1 and env_local_rank != args.local_rank:
        args.local_rank = env_local_rank

    # 动态加载验证提示词
    if args.validation_prompts is None:
        try:
            with open("validation_prompts.txt", "r", encoding="utf-8") as f:
                args.validation_prompts = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            # 回退到默认提示词
            args.validation_prompts = [
                "白日依山尽，黄河入海流。",
                "绿遍山原白满川，子规声里雨如烟。",
                "落霞与孤鹜齐飞，秋水共长天一色。",
                "山气日夕佳，飞鸟相与还。",
                "春眠不觉晓，处处闻啼鸟。",
                "日出江花红胜火，春来江水绿如蓝。",
                "山外青山楼外楼，西湖歌舞几时休。",
                "月落乌啼霜满天，江枫渔火对愁眠。",
                "相思一夜天涯远，梦回千里月明寒."
            ]

    # 健全性检查
    if args.dataset is None and args.data_direction is None:
        raise ValueError("Need either a dataset name or a training folder.")
    
    if args.non_ema_model_revision is None:
        args.non_ema_model_revision = args.model_revision

    return args