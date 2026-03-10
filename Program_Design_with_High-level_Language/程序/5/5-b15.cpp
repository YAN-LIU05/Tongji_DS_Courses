/* 2352018 信06 刘彦 */
#include <iostream>

using namespace std;

int main() 
{
    char strL3[3][128];   //定义一个二维字符数组，用于存储三行输入的文本
    int count[5] = { 0 };   //计数
    int i, j;

    cout << "请输入第1行" << endl;
    cin.getline(strL3[0], 128);
    cout << "请输入第2行" << endl;
    cin.getline(strL3[1], 128);
    cout << "请输入第3行" << endl;
    cin.getline(strL3[2], 128);

    // 遍历三行文本，统计字符
    for (i = 0; i < 3; ++i)
    {
        for (j = 0; strL3[i][j] != '\0'; ++j) 
        {
            if (strL3[i][j] >= 'A' && strL3[i][j] <= 'Z') 
            {
                count[0]++; // 英文大写字母
            }
            else if (strL3[i][j] >= 'a' && strL3[i][j] <= 'z') 
            {
                count[1]++; // 英文小写字母
            }
            else if (strL3[i][j] >= '0' && strL3[i][j] <= '9') 
            {
                count[2]++; // 数字
            }
            else if (strL3[i][j] == ' ') 
            {
                count[3]++; // 空格
            }
            else {
                count[4]++; // 其他字符
            }
        }
    }

    cout << "大写 : " << count[0] << endl;
    cout << "小写 : " << count[1] << endl;
    cout << "数字 : " << count[2] << endl;
    cout << "空格 : " << count[3] << endl;
    cout << "其它 : " << count[4] << endl;

    return 0;
}