#include <iostream>
#include <cstring>
using namespace std;

int map[6][6];         // 邻接矩阵
int cnt = 0;           // 计数器，记录一笔画的总数
char path[20];         // 用于存储路径
int path_index = 0;    // 路径的当前长度
void dfs(int x, int k);  // 深度优先搜索（DFS）

int main() 
{
    memset(map, 0, sizeof(map)); // 初始化邻接矩阵为0

    for (int i = 1; i <= 5; i++) 
        for (int j = i + 1; j <= 5; j++) 
            if (i != j) 
                map[i][j] =  map[j][i] = 1; // 非对角线元素先设置为1

    // 两端点没有路径则置0
    map[1][4] = map[4][1] = 0;
    map[2][4] = map[4][2] = 0;
    
    
    path[path_index++] = '1'; // 初始路径以1开头
    cout << "欧拉路径如下:" << endl;
    dfs(1, 0);
    cout << "此图欧拉路径总数:" << cnt << endl;
    return 0;
}

/**
 * @brief           深度优先搜索（DFS）函数，用于寻找欧拉路径
 * @param x         当前顶点
 * @param k         已遍历的边数
 */
void dfs(int x, int k) 
{
    if (k >= 8) { // 如果已经遍历了 8 条边
        cnt++;
        path[path_index] = '\0'; // 确保路径是一个合法的字符串
        cout << path << endl;    // 输出路径
        return;
    }

    for (int y = 1; y <= 5; y++) { // 遍历所有可能的下一个顶点
        if (map[x][y] == 1) {      // 如果顶点 x 和 y 之间有边
            map[x][y] = 0;         // 标记边为已访问
            map[y][x] = 0;

            // 添加当前顶点到路径中
            path[path_index++] = '0' + y;

            dfs(y, k + 1); // 递归处理下一个顶点

            // 回溯，移除路径中的顶点
            path[--path_index] = '\0';

            map[x][y] = 1; // 恢复边的状态
            map[y][x] = 1;
        }
    }
}

