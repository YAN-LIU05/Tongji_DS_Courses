文件夹结构如下：

project_root/
├── config/
│   └── din_config/
│       ├── model_config.yaml
│       └── DIN_microlens_mmctr_tuner_config_01.yaml
├── data/
│   ├── MicroLens_1M_x1/
│   │   ├── train.parquet
│   │   ├── test.parquet
│   │   ├── item_info.parquet
│   │   └── valid.parquet
│   ├── item_emb.parquet
│   ├── item_feature.parquet
│   ├── item_seq.parquet
│   └── item_images.rar 
├── src/
│   ├── __init__.py
│   ├── DIN.py
│   ├── mmctr_dataloader.py
│   └── QIN.py
├── gen_item_info.py  
├── inference_optimized_v2.py  
├── prediction.py  
├── requirements.txt  
├── run_expid.py  
├── run_param_tuner.py  
├── run_task1.sh  
└── run_task2.sh

下载模型并放到主目录  
https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct

下载模型transformers.zip并放到主目录
https://github.com/huggingface/transformers

完成Task 1：
bash run_task1.sh
完成Task 2：
bash run_task2.sh
完成Task 1&2：
python inference_optimized_v2.py
python run_expid.py


