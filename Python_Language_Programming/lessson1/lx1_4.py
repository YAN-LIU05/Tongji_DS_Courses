import qrcode

def generate_qrcode(url):
    # 创建二维码对象
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # 添加数据
    qr.add_data(url)
    qr.make(fit=True)

    # 创建一个图片
    img = qr.make_image(fill_color="black", back_color="white")

    # 保存图片
    img.save("tongji_qrcode.png")


if __name__ == '__main__':
    url = "https://www.tongji.edu.cn"
    generate_qrcode(url)