这个是Stable Diffusion的模型代码和数据集，本实验在Linux-5.4.0-155-generic-x86_64-with-glibc2.35系统下进行，环境是Ubuntu 22.02 LTS，Python 3.12。CPU是12 vCPU Intel(R) Xeon(R) Platinum 8352V CPU @ 2.10GHz，GPU是NVIDIA vGPU-32GB，PyTorch版本为2.5.1，CUDA版本为12.4。

/root
├── Paint4Poem-Web-famous-subset
│   ├── images
│   └── POEM_IMAGE.csv
├── stable-diffusion-v1-5
│   ├── feature_extractor
│   ├── safety_checker
│   ├── scheduler
│   ├── text_encoder
│   ├── tokenizer
│   ├── unet
│   ├── vae
│   ├── model_index.json
│   ├── README.md
│   ├── v1-5-pruned-emaonly.safetensors
│   ├── v1-5-pruned.safetensors
│   └── v1-inference.yaml
├── predict.py
├── utils.py
├── model_utils.py
├── dataset_utils.py
├── train.py
├── logging_utils.py 
├── main.py
├── sd_config.py
├── run.sh
├── validation_prompts.txt
├── validation_prompts_simple_cn.txt
├── validation_prompts_en.txt
├── requirments.txt
└── README.txt

其中Paint4Poem-Web-famous-subset是数据集目录，stable-diffusion-v1-5是模型目录
运行下方指令即可开始实验：
bash run.sh
运行下方指令即可开始检验：
python predict.py
