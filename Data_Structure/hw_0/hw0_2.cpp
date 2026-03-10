#include <iostream>

using namespace std;

// 计算数据包的校验值
int calculateChecksum(const char* dataPacket) {
    int checksum = 0;
    int position = 1; // 位置从1开始

    // 遍历数据包中的每个字符
    while (*dataPacket != '\0') {
        char charAtIndex = *dataPacket;
        int value;
        if (charAtIndex == ' ') {
            value = 0;
        } 
        else if ((charAtIndex>='A' && charAtIndex<='Z'))
        {
            value = charAtIndex - 'A' + 1;
        }
        checksum += position * value;
        position++;
        dataPacket++;
    }

    return checksum;
}

int main() {
    char line[2560]; // 假设每行数据包的最大长度为255个字符（加上1个字符的终结符）

    // 读取所有输入行
    while (cin.getline(line, sizeof(line))) {
        if (line[0] == '#' && line[1] == '\0') {
            break;
        }

        // 计算校验值
        int checksum = calculateChecksum(line);
        
        // 输出结果
        cout << checksum << endl;
    }

    return 0;
}
