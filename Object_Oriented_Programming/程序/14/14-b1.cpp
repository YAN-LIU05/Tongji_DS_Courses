/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <cstring>
#include <iomanip>
#include <climits>

using namespace std;

void print_switches(short state)
{
    const char labels[] = "ABCDEFGHIJ";
    for (int i = 0; i < 11; i++)
        cout << labels[i] << "   ";
    cout << endl;
    // 反向输出开关状态
    for (int i = 0; i < 10; ++i) 
        cout << ((state & (1 << i)) ? "ON  " : "OFF ");
    cout << endl;
}

char change_to_capital(char c) 
{
    if (c >= 'a' && c <= 'z') return c - ('a' - 'A');
    return c;
}

int main() 
{
    short state = 0x0000;
    cout << "初始状态：0x" << hex << setw(4) << setfill('0') << state << endl;
    print_switches(state);
    cout << endl;

    while (1) 
    {
        char input[CHAR_MAX];  
        cout << "请以(\"A ON / J OFF\"形式输入，输入\"Q on/off\"退出): " << endl;
        cin.getline(input, sizeof(input));

        if (input[0] == 'Q' || input[0] == 'q') 
            break;

        char switch_label;
        char on_off[4];  // 存储 "ON" 或 "OFF"

        // 手动解析输入
        switch_label = change_to_capital(input[0]);

        // 查找空格后提取动作
        int num = 2; 
        int on_off_num = 0;  // 用于 on_off 的索引

        // 跳过可能的空格
        while (input[num] == ' ') 
            num++;

        // 提取
        while (input[num] != '\0' && input[num] != ' ' && on_off_num < 3)
            on_off[on_off_num++] = change_to_capital(input[num++]);  // 将动作字符转换为大写
        on_off[on_off_num] = '\0';  // 结束字符串

        // 处理输入检查
        if (switch_label < 'A' || switch_label > 'J' || (strcmp(on_off, "ON") != 0 && strcmp(on_off, "OFF") != 0)) 
            continue;

        int index = switch_label - 'A';
        if (strcmp(on_off, "ON") == 0) 
            state |= (1 << index);  // 设置对应的bit为1
        else 
            state &= ~(1 << index);  // 设置对应的bit为0

        cout << "当前状态：0x" << hex << setw(4) << setfill('0') << state << endl;  // 输出当前状态的十六进制
        print_switches(state);
        cout << endl;
    }

    return 0;
}
