#!/bin/bash

python main.py \
  --ema \
  --image_size=512 \
  --center_crop \
  --random_flip \
  --batch_size=1 \
  --grad_accum_steps=4 \
  --grad_checkpoint \
  --max_steps=1 \
  --learning_rate=1e-5 \
  --grad_norm=1 \
  --random_seed=42 \
  --scheduler="constant" \
  --warmup_steps=0 \
  --output_direction="sd-model" \
  --cache_direction data/tmp \
  --tf32 \