/* 2352018 信06 刘彦 */
#include <iostream>  
using namespace std;

void Sort(int arr[], int n) 
{
    for (int i = 0; i < n - 1; i++) 
    {
        for (int j = 0; j < n - i - 1; j++) 
        {
            if (arr[j] > arr[j + 1]) 
            {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() 
{
    int scores[1000];
    int score_count = 0;
    int score;

    cout << "请输入成绩（最多1000个），负数结束输入" << endl;

    while (score_count < 1000 && cin >> score && score >= 0) 
    {
        scores[score_count++] = score;
    }

    if (score_count == 0) 
    {
        cout << "无有效输入" << endl;
        return 0;
    }
 
    cout << "输入的数组为:" << endl;
    for (int i = 0; i < score_count; ++i)
    {
        cout << scores[i] << " ";
        if ((i + 1) % 10 == 0)
        {
            cout << endl;
        }
    }
    cout << endl;

    Sort(scores, score_count);

    int r = 1;
    int last_score = scores[0]; // 用于记录上一个成绩
    cout << "分数与名次的对应关系为:" << endl;
    for (int i = score_count - 1; i >= 0; --i)
    {
        if (scores[i] != last_score) // 如果当前成绩与上一个成绩不同
        {
            r = i + 1; // 名次重置为当前的索引加1
            last_score = scores[i]; // 更新上一个成绩
        }
        int rank = score_count - r + 1;
        cout << scores[i] << " " << rank << endl; // 输出成绩和名次
    }

    return 0;
}