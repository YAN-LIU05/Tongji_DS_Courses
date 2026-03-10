def tablem(n):
    for i in range(1, n + 1):
        # 打印当前行的乘法结果
        for j in range(1, i + 1):
            print(j * i, end=' ' if j < i else '\n')  # 使用end=' '来分隔同一行的数字

# 调用函数测试
if __name__ == '__main__':
    n = int(input("n="))
    tablem(n)