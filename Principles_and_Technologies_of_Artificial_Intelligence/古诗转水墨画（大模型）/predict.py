import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os
import swanlab

# 手动输入模型路径
model_path = "sd-naruto-model"

# 检查路径是否存在
if not os.path.exists(model_path):
    raise ValueError(f"模型路径 {model_path} 不存在，请检查路径是否正确！")

# 设置权重数据类型（根据你的训练配置）
weight_dtype = torch.float16  # 如果训练时使用了混合精度（fp16），可以改为 torch.float32 或 torch.bfloat16

# 加载模型
pipeline = StableDiffusionPipeline.from_pretrained(
    model_path,
    torch_dtype=weight_dtype,
    safety_checker=None,  # 禁用安全检查器（可选）
).to("cuda")

# 启用 xformers（如果在训练时使用）
try:
    pipeline.xformers()
except:
    print("xformers 未启用，可能未安装或不可用。")

# 设置生成参数
prompt_name = "en"
with open(f"validation_prompts_{prompt_name}.txt", "r", encoding="utf-8") as f:
    prompts = [line.strip() for line in f if line.strip()]  # 去除空行和前后空格
# prompts = [ "The sun sets behind the mountains, and the Yellow River flows into the sea.",
#             "The mountains are covered with green and the rivers are full of white. In the sound of Zi GUI, the rain is like smoke." ,
#             "The setting sun and solitary wild goose fly together, and the autumn water blends with the distant sky in one color." ,
#             "The mountain air is pleasant at dusk and day, and birds return to each other." ,
#             "In spring, one sleeps without realizing dawn; everywhere one hears the chirping of birds. ",
#             "When the sun rises, the river flowers are redder than fire; when spring comes, the river water is greener than blue." ,
#             "Beyond the mountains, there are green mountains; beyond the towers, there are towers. When will the singing and dancing of West Lake come to an end?" ,
#             "The moon sets, crows cry, and frost fills the sky; by the river, maple trees and fishing lights, I sleep in sorrow." ,
#             "A night of longing is far from the ends of the earth; a dream of a thousand miles is bright and cold under the moon." ] 

# 创建保存生成图像的目录
output_direction = f"validation_images_{prompt_name}"
os.makedirs(output_direction, exist_ok=True)

# 初始化 swanlab（可选，用于记录生成图像）
swanlab.init(
    project="SD-Poem-Validation",
    experiment_name="Manual_Validation",
    description="手动验证训练好的古诗图像生成模型"
)

# 生成并保存图像
generator = torch.Generator(device="cuda").manual_seed(42)  # 固定种子以保证可重复性
for i, prompt in enumerate(prompts):
    with torch.autocast("cuda"):
        image = pipeline(
            prompt,
            num_inference_steps=50,  # 推理步数，越大图像质量越高
            guidance_scale=7.5,     # 提示词引导尺度
            generator=generator
        ).images[0]
    
    # 保存图像
    image_path = os.path.join(output_direction, f"prompt_{i}.png")
    image.save(image_path)
    
    # 记录到 swanlab
    swanlab.log({"validation_image": swanlab.Image(image, caption=prompt)})

    print(f"已生成并保存图像：{image_path}")

# 结束 swanlab 记录
swanlab.finish()

# 可选：显示图像
for i in range(len(prompts)):
    image = Image.open(os.path.join(output_direction, f"prompt_{i}.png"))
    image.show()