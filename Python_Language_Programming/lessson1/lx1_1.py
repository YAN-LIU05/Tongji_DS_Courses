def diamond(n,m):
    for _ in range(n):  # 循环n次
        for i in range(m):
            # 计算空格数
            spaces = ' ' * (m - i - 1)
            # 计算星号数量，不超过m
            stars = '*' * (2 * i + 1)
            print(spaces + stars)

            # 打印下半部分
        for i in range(m - 2, -1, -1):
            spaces = ' ' * (m - i - 1)
            stars = '*' * (2 * i + 1)
            print(spaces + stars)

# 调用函数测试
if __name__ == '__main__':
    n = int(input("n="))
    m = int(input("m="))
    diamond(n, m)