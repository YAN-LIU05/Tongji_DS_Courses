/**
 * @file    template.cpp
 * @name    p138模板程序
 * @date    2022-11-20
*/

#include <iostream>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <string>
#include <vector>
#include <queue>
#include <stack>
#include <map>
#include <set>
using namespace std;


/********************************/
/*     以下是你需要提交的代码     */
/********************************/
class Solution {
public:
    int solve(vector<vector<string>>& old_chart, vector<vector<string>>& new_chart) {
        int n = old_chart.size();
        int m = old_chart[0].size();
        int total_size = n * m;
 
        // 将二维数组转为一维数组
        vector<string> old_vec, new_vec;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                old_vec.push_back(old_chart[i][j]);
                new_vec.push_back(new_chart[i][j]);
            }
        }
 
        // 使用 map 来记录 new_vec 中学生的目标位置
        map<string, int> position_map;
        for (int i = 0; i < total_size; i++) {
            position_map[new_vec[i]] = i;
        }
 
        // 创建目标位置数组
        vector<int> target_pos(total_size);
        for (int i = 0; i < total_size; i++) {
            target_pos[i] = position_map[old_vec[i]];
        }
 
        // 使用 visited 数组来检查每个学生是否已经在正确的位置
        vector<bool> visited(total_size, false);
        int swap_count = 0;
 
        // 计算最小交换次数
        for (int i = 0; i < total_size; i++) {
            // 如果该位置已经访问过，或者已经在正确的位置，跳过
            if (visited[i] || target_pos[i] == i)
                continue;
 
            // 计算环的长度
            int cycle_length = 0;
            int current = i;
 
            while (!visited[current]) {
                visited[current] = true;
                current = target_pos[current];
                cycle_length++;
            }
 
            // 如果环的长度大于 1，那么需要进行 `cycle_length - 1` 次交换
            if (cycle_length > 1) {
                swap_count += cycle_length - 1;
            }
        }
 
        return swap_count;
    }
};
/********************************/
/*     以上是你需要提交的代码     */
/********************************/

int main() {
    int n, m;
    std::cin >> n >> m;
    std::vector<std::vector<std::string>> old_chart(n, std::vector<std::string>(m));
    std::vector<std::vector<std::string>> new_chart(n, std::vector<std::string>(m));

    for( int i = 0; i < n; i ++ ) {
        for( int j = 0; j < m; j ++ ) {
            std::cin >> old_chart[i][j];
        }
    }
    for( int i = 0; i < n; i ++ ) {
        for( int j = 0; j < m; j ++ ) {
            std::cin >> new_chart[i][j];
        }
    }

    Solution s;
    std::cout << s.solve(old_chart, new_chart) << std::endl;
    return true;
}
