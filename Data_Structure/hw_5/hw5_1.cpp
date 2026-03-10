#include <iostream>
using namespace std;

// 手动实现排序函数（冒泡排序）
void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n - 1; ++i) {
        bool swapped = false;  // 添加标志位
        for (int j = 0; j < n - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = true;
            }
        }
        if (!swapped) break;  // 没有交换，提前退出
    }
}


/**
 * @brief           二分查找函数
 * @param prefix_sum 前缀和数组
 * @param n          数组长度
 * @param target     目标值
 * @return          返回满足条件的最大长度
 */
int binarySearch(int prefix_sum[], int n, int target) 
{
    int left = 0, right = n;
    while (left < right) 
    {
        int mid = (left + right + 1) / 2;
        if (prefix_sum[mid] <= target) 
            left = mid;  // 尝试扩大范围
        else 
            right = mid - 1;
    }
    return left; // 返回满足条件的最大长度
}

int main() 
{
    // 输入数组大小 n 和 m
    int n, m;
    cin >> n >> m;

    // 定义数组
    int nums[1000], queries[1000], prefix_sum[1001], result[1000];

    // 输入 nums 数组
    for (int i = 0; i < n; ++i) 
        cin >> nums[i];

    // 输入 queries 数组
    for (int i = 0; i < m; ++i) 
        cin >> queries[i];

    // Step 1: 对 nums 排序
    bubbleSort(nums, n);

    // Step 2: 计算前缀和
    prefix_sum[0] = 0;
    for (int i = 1; i <= n; ++i) 
        prefix_sum[i] = prefix_sum[i - 1] + nums[i - 1];

    // Step 3: 处理每个 query，使用二分查找
    for (int i = 0; i < m; ++i) 
        result[i] = binarySearch(prefix_sum, n, queries[i]);

    // 输出结果
    for (int i = 0; i < m; ++i) 
    {
        if (i > 0) cout << " ";
        cout << result[i];
    }
    cout << endl;

    return 0;
}
