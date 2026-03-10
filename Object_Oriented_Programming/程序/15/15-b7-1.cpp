/* 2352018 大数据 刘彦 */
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstring>
#if defined(_MSC_VER) || defined(__MINGW32__) 
#include <conio.h>
#endif

using namespace std;

// 定义一个 64 字节的结构体，成员可自行设计
#pragma pack(push, 1)
struct GameData {
    char nickname[16];    // 1-16 玩家昵称
    short hp;             // 17-18 生命值
    short strength;       // 19-20 力量值
    short constitution;   // 21-22 体质
    short agility;        // 23-24 灵巧
    int money;            // 25-28 金钱
    int reputation;       // 29-32 名声值
    int charm;            // 33-36 魅力值
    long long playTime;   // 37-44 累计时间
    char moveSpeed;       // 45 移动速度
    char attackSpeed;     // 46 攻击速度
    char attackRange;     // 47 攻击范围
    char empty;           // 48
    short attackPower;    // 49-50 攻击力
    short defense;        // 51-52 防御力
    char dexterity;       // 53 敏捷
    char intelligence;    // 54 智力
    char experience;      // 55 经验
    char level;           // 56 等级
    short mana;           // 57-58 魔法值
    char manaCost;        // 59 使用魔法消耗
    char magicDamage;     // 60 魔法伤害
    char hitRate;         // 61 命中率
    char magicDefense;    // 62 魔法防御
    char criticalRate;    // 63 暴击率
    char stamina;         // 64 耐力
};
#pragma pack(pop)

/* 此处允许新增函数，数量不限
   1、所有新增的函数，均不允许定义新的 fstream / ifstream / ofstream 流对象，并进行打开/读/写/关闭等操作
   2、所有新增的函数，均不允许用C方式进行文件处理
   3、上述两个限制同样适用于main函数
*/

/***************************************************************************
  函数名称：judge_and_change
  功    能：判断并修改数值
  输入参数：
  返 回 值：
  说    明：四个重载函数
***************************************************************************/
void judge_and_change(GameData& data, char& value, const char attribute[15], int num, char max_border = 100, char min_border = 0)
{
    while (1)
    {
        cout << attribute << "，当前值=" << (int)value << "，范围[" << (int)min_border << ".." << (int)max_border << "]，请输入 : ";
        cin.clear();
        cin >> num;
        if (cin.fail())
        {
            cin.clear();
            cin.ignore(65536, '\n');
            continue;
        }
        if (num > max_border || num < min_border)
        {
            cout << "非法的" << attribute << "值：" << (int)num << endl;
            continue;
        }
        else
        {
            value = num;
            break;
        }
    }
}

void judge_and_change(GameData& data, short& value, const char attribute[15], short num, short max_border, short min_border = 0)
{
    while (1)
    {
        cout << attribute << "，当前值=" << value << "，范围[" << min_border << ".." << max_border << "]，请输入 : ";
        cin.clear();
        cin >> num;
        if (cin.fail()) 
        {
            cin.clear();
            cin.ignore(65536, '\n');
            continue;
        }
        if (num > max_border || num < min_border)
        {
            cout << "非法的" << attribute << "值：" << num << endl;
            continue;
        }
        else
        {
            value = num;
            break;
        }
    }
}

void judge_and_change(GameData& data, int& value, const char attribute[15], int num, int max_border, int min_border = 0)
{
    while (1)
    {
        cout << attribute << "，当前值=" << value << "，范围[" << min_border << ".." << max_border << "]，请输入 : ";
        cin.clear();
        cin >> num;
        if (cin.fail()) 
        {
            cin.clear();
            cin.ignore(65536, '\n');
            continue;
        }
        if (num > max_border || num < min_border)
        {
            cout << "非法的" << attribute << "值：" << num << endl;
            continue;
        }
        else
        {
            value = num;
            break;
        }
    }
}

void judge_and_change(GameData& data, long long& value, const char attribute[15], long long num, long long max_border = 10000000000000000, long long min_border = 0)
{
    while (1)
    {
        cout << attribute << "，当前值=" << value << "，范围[" << min_border << ".." << max_border << "]，请输入 : ";
        cin.clear();
        cin >> num;
        if (cin.fail())
        {
            cin.clear();
            cin.ignore(65536, '\n');
            continue;
        }
        if (num > max_border || num < min_border)
        {
            cout << "非法的" << attribute << "值：" << num << endl;
            continue;
        }
        else
        {
            value = num;
            break;
        }
    }
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：整个函数，只允许出现一次open、一次read（因为包含错误处理，允许多次close）
***************************************************************************/
int read() 
{
    // 属性名称数组
    const char attributes[][22] = {
        "玩家昵称：", "生命值：", "力量值：", "体质值：", "灵巧值：", "金钱值：",
        "名声值：", "魅力值：", "游戏累计时间(us)值：", "移动速度值：", "攻击速度值：",
        "攻击范围值：", "攻击力值：", "防御力值：", "敏捷度值：", "智力值：", 
        "经验值：", "等级值：", "魔法值：", "消耗魔法值：", "魔法伤害力值：", 
        "魔法命中率值：", "魔法防御力值：", "暴击率值：", "耐力值："
    };

    fstream gfile;

    // 打开文件
    gfile.open("game.dat", ios::binary | ios::in);
    if (!gfile) 
    {
        cerr << "无法打开文件 game.dat" << endl;
        return -1;
    }

    GameData data;

    // 一次性读取 64 字节数据
    char temp[sizeof(GameData)];
    gfile.read(temp, sizeof(GameData));
    if (!gfile) 
    {
        cerr << "读取文件失败" << endl;
        gfile.close();
        return -1;
    }
    memcpy(&data, temp, sizeof(GameData));
    // 显示存档内容
    int length = strlen("游戏累计时间(us)值：");
    cout << setw(length) << right << attributes[0] << data.nickname << endl;
    cout << setw(length) << right << attributes[1] << data.hp << endl;
    cout << setw(length) << right << attributes[2] << data.strength << endl;
    cout << setw(length) << right << attributes[3] << data.constitution << endl;
    cout << setw(length) << right << attributes[4] << data.agility << endl;
    cout << setw(length) << right << attributes[5] << data.money << endl;
    cout << setw(length) << right << attributes[6] << data.reputation << endl;
    cout << setw(length) << right << attributes[7] << data.charm << endl;
    cout << setw(length) << right << attributes[8] << data.playTime << endl;
    cout << setw(length) << right << attributes[9] << static_cast<int>(data.moveSpeed) << endl;
    cout << setw(length) << right << attributes[10] << static_cast<int>(data.attackSpeed) << endl;
    cout << setw(length) << right << attributes[11] << static_cast<int>(data.attackRange) << endl;
    cout << setw(length) << right << attributes[12] << data.attackPower << endl;
    cout << setw(length) << right << attributes[13] << data.defense << endl;
    cout << setw(length) << right << attributes[14] << static_cast<int>(data.dexterity) << endl;
    cout << setw(length) << right << attributes[15] << static_cast<int>(data.intelligence) << endl;
    cout << setw(length) << right << attributes[16] << static_cast<int>(data.experience) << endl;
    cout << setw(length) << right << attributes[17] << static_cast<int>(data.level) << endl;
    cout << setw(length) << right << attributes[18] << data.mana << endl;
    cout << setw(length) << right << attributes[19] << static_cast<int>(data.manaCost) << endl;
    cout << setw(length) << right << attributes[20] << static_cast<int>(data.magicDamage) << endl;
    cout << setw(length) << right << attributes[21] << static_cast<int>(data.hitRate) << endl;
    cout << setw(length) << right << attributes[22] << static_cast<int>(data.magicDefense) << endl;
    cout << setw(length) << right << attributes[23] << static_cast<int>(data.criticalRate) << endl;
    cout << setw(length) << right << attributes[24] << static_cast<int>(data.stamina) << endl;

    gfile.close();
    return 0;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：整个函数，只允许出现一次open、一次read、一次write（因为包含错误处理，允许多次close）
***************************************************************************/
int modify() 
{
    // 属性名称数组
    const char attributes[][15] = {
        "a.玩家昵称    ", "b.生命        ", "c.力量        ", "d.体质        ",
        "e.灵巧        ", "f.金钱        ", "g.名声        ", "h.魅力        ",
        "i.游戏累计时间", "j.移动速度    ", "k.攻击速度    ", "l.攻击范围    ",
        "m.攻击力      ", "n.防御力      ", "o.敏捷度      ", "p.智力        ",
        "q.经验        ", "r.等级        ", "s.魔法值      ", "t.消耗魔法值  ",
        "u.魔法伤害力  ", "v.魔法命中率  ", "w.魔法防御力  ", "x.暴击率      ",
        "y.耐力        "
    };
    const char attribute[][15] = {
    "玩家昵称", "生命", "力量", "体质", "灵巧", "金钱", "名声", "魅力",
    "游戏累计时间", "移动速度", "攻击速度", "攻击范围", "攻击力", "防御力", 
    "敏捷度", "智力",  "经验", "等级", "魔法值", "消耗魔法值", "魔法伤害力", 
    "魔法命中率", "魔法防御力", "暴击率", "耐力 "
    };

    fstream gfile;
    
    gfile.open("game.dat", ios::binary | ios::in | ios::out);
    if (!gfile) 
    {
        cerr << "无法打开文件 game.dat" << endl;
        return -1;
    }

    GameData data;
    char temp[sizeof(GameData)];
    gfile.read(temp, sizeof(GameData));

    if (!gfile)
    {
        cerr << "读取文件失败" << endl;
        gfile.close();
        return -1;
    }
    memcpy(&data, temp, sizeof(GameData));
    char choice;
    do {
        cout << "--------------------------------------" << endl;
        cout << "  游戏存档文件修改工具" << endl;
        cout << "--------------------------------------" << endl;
        cout << "  " << attributes[0] << "(" << data.nickname << ")" << endl;
        cout << "  " << attributes[1] << "(" << data.hp << ")" << endl;
        cout << "  " << attributes[2] << "(" << data.strength << ")" << endl;
        cout << "  " << attributes[3] << "(" << data.constitution << ")" << endl;
        cout << "  " << attributes[4] << "(" << data.agility << ")" << endl;
        cout << "  " << attributes[5] << "(" << data.money << ")" << endl;
        cout << "  " << attributes[6] << "(" << data.reputation << ")" << endl;
        cout << "  " << attributes[7] << "(" << data.charm << ")" << endl;
        cout << "  " << attributes[8] << "(" << data.playTime << ")" << endl;
        cout << "  " << attributes[9] << "(" << static_cast<int>(data.moveSpeed) << ")" << endl;
        cout << "  " << attributes[10] << "(" << static_cast<int>(data.attackSpeed) << ")" << endl;
        cout << "  " << attributes[11] << "(" << static_cast<int>(data.attackRange) << ")" << endl;
        cout << "  " << attributes[12] << "(" << data.attackPower << ")" << endl;
        cout << "  " << attributes[13] << "(" << data.defense << ")" << endl;
        cout << "  " << attributes[14] << "(" << static_cast<int>(data.dexterity) << ")" << endl;
        cout << "  " << attributes[15] << "(" << static_cast<int>(data.intelligence) << ")" << endl;
        cout << "  " << attributes[16] << "(" << static_cast<int>(data.experience) << ")" << endl;
        cout << "  " << attributes[17] << "(" << static_cast<int>(data.level) << ")" << endl;
        cout << "  " << attributes[18] << "(" << data.mana << ")" << endl;
        cout << "  " << attributes[19] << "(" << static_cast<int>(data.manaCost) << ")" << endl;
        cout << "  " << attributes[20] << "(" << static_cast<int>(data.magicDamage) << ")" << endl;
        cout << "  " << attributes[21] << "(" << static_cast<int>(data.hitRate) << ")" << endl;
        cout << "  " << attributes[22] << "(" << static_cast<int>(data.magicDefense) << ")" << endl;
        cout << "  " << attributes[23] << "(" << static_cast<int>(data.criticalRate) << ")" << endl;
        cout << "  " << attributes[24] << "(" << static_cast<int>(data.stamina) << ")" << endl;
        cout << "--------------------------------------" << endl;
        cout << "  0.放弃修改" << endl;
        cout << "  1.存盘退出" << endl;
        cout << "--------------------------------------" << endl;
        cout << "请选择[a..y, 0..1] ";
#if defined(_MSC_VER) || defined(__MINGW32__) 
        choice = _getch();
#elif defined(__linux__)
        choice = getchar();
#endif
#if defined(_MSC_VER) || defined(__MINGW32__) 
        cout << choice << endl;
#endif
        cout << endl;
        short num_short = 0;
        int num_int = 0;
        long long num_long_long = 0LL;
        switch (choice) 
        {
            case 'a':
                cout << "玩家昵称，当前值=" << data.nickname << "，请输入: ";
                cin.clear();
#if defined(__linux__) 
                cin.ignore(65536, '\n');
#endif
                cin.getline(data.nickname, 16);
                if (cin.fail()) 
                {
                    cin.clear();
                    cin.ignore(65536, '\n'); 
                }
                data.nickname[15] = '\0';
                break;
            case 'b':
                judge_and_change(data, data.hp, attribute[1], num_short, 10000);
                break;
            case 'c':
                judge_and_change(data, data.strength, attribute[2], num_short, 10000);
                break;
            case 'd':
                judge_and_change(data, data.constitution, attribute[3], num_short, 8192);
                break;
            case 'e':
                judge_and_change(data, data.agility, attribute[4], num_short, 1024);
                break;
            case 'f':
                judge_and_change(data, data.money, attribute[5], num_int, 100000000);
                break;
            case 'g':
                judge_and_change(data, data.reputation, attribute[6], num_int, 1000000);
                break;
            case 'h':
                judge_and_change(data, data.charm, attribute[7], num_int, 1000000);
                break;
            case 'i':
                judge_and_change(data, data.playTime, attribute[8], num_long_long);
                break;
            case 'j':
                judge_and_change(data, data.moveSpeed, attribute[9], num_int);
                break;
            case 'k':
                judge_and_change(data, data.attackSpeed, attribute[10], num_int);
                break;
            case 'l':
                judge_and_change(data, data.attackRange, attribute[11], num_int);
                break;
            case 'm':
                judge_and_change(data, data.attackPower, attribute[12], num_short, 2000);
                break;
            case 'n':
                judge_and_change(data, data.defense, attribute[13], num_short, 2000);
                break;
            case 'o':
                judge_and_change(data, data.dexterity, attribute[14], num_int);
                break;
            case 'p':
                judge_and_change(data, data.intelligence, attribute[15], num_int);
                break;
            case 'q':
                judge_and_change(data, data.experience, attribute[16], num_int);
                break;
            case 'r':
                judge_and_change(data, data.level, attribute[17], num_int);
                break;
            case 's':
                judge_and_change(data, data.mana, attribute[18], num_short, 10000);
                break;
            case 't':
                judge_and_change(data, data.manaCost, attribute[19], num_int);
                break;
            case 'u':
                judge_and_change(data, data.magicDamage, attribute[20], num_int);
                break;
            case 'v':
                judge_and_change(data, data.hitRate, attribute[21], num_int);
                break;
            case 'w':
                judge_and_change(data, data.magicDefense, attribute[22], num_int);
                break;
            case 'x':
                judge_and_change(data, data.criticalRate, attribute[23], num_int);
                break;
            case 'y':
                judge_and_change(data, data.stamina, attribute[24], num_int);
                break;
            case '0':
                gfile.close();
                return 0;
            case '1':
                char temp0[sizeof(GameData)];
                memcpy(temp0, &data, sizeof(GameData));
                gfile.seekp(0);
                gfile.write(temp0, sizeof(GameData));
                if (!gfile) 
                {
                    cerr << "文件写入失败" << endl;
                    return -1;
                }
                gfile.close();
                return 0;
            default:
                continue;
        }
    } while (true);

    return 0;
}


/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数允许带参数，不允许进行文件读写
***************************************************************************/
int main(int argc, char** argv) 
{
    if (argc < 2)
    {
        cerr << "usage : 15-b7-1 --modify | --read" << endl;
        return -1;
    }

    if (strcmp(argv[1], "--read") == 0) 
        return read();
    else if (strcmp(argv[1], "--modify") == 0) 
        return modify();
    else {
        cerr << "usage : 15-b7 --modify | --read" << endl;
        return -1;
    }
    return 0;
}

