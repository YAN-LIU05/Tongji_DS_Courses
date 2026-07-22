from kanren import run, var
from kanren.goals import membero, goalify
from itertools import permutations

# 定义 N (棋盘大小，例如 6x6)
N = 8

# 逻辑约束：不在同一对角线
def check_diagonal(queen: tuple):
    for i in range(N):
        for j in range(i + 1, N):
            if i + queen[i] == j + queen[j] or i - queen[i] == j - queen[j]:
                return False
    return True

all_permutations = tuple(permutations(range(N)))

# 创建 N 个变量表示皇后的位置
queens = var("queens")

# 运行求解
solutions = run(
    0,
    queens,
    membero(queens, all_permutations),  # 限制皇后必须在棋盘列范围内
    (goalify(check_diagonal), (queens,), True),  # 约束：不同对角线
)

# 打印解决方案
print(f"Total solutions: {len(solutions)}")
for idx, solution in enumerate(solutions, 1):
    print(f"Solution {idx}: {solution}")
