/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#if defined(_MSC_VER) || defined(__MINGW32__) 
#include <conio.h>
#endif
//根据需要可加入其它头文件


// 定义一个 64 字节的结构体，成员可自行设计
#pragma pack(push, 1)
typedef struct {
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
} GameData;
#pragma pack(pop)

/* 此处允许新增函数，数量不限
   1、所有新增的函数，均不允许定义新的 FILE* 并进行打开/读/写/关闭等操作
   2、上述限制同样适用于main函数
*/

// 判断并修改 char 类型数值
void judge_and_change_char(GameData* data, char* value, const char attribute[15], int num, char max_border, char min_border) {
    while (1) {
        printf("%s，当前值=%d，范围[%d..%d]，请输入: ", attribute, (int)*value, (int)min_border, (int)max_border);
        if (scanf("%d", &num) != 1) {
            while (getchar() != '\n');  // 清空输入缓冲区
            continue;
        }
        if (num > max_border || num < min_border) {
            printf("非法的%s值：%d\n", attribute, num);
            continue;
        }
        else {
            *value = (char)num;
            break;
        }
    }
}

// 判断并修改 short 类型数值
void judge_and_change_short(GameData* data, short* value, const char attribute[15], short num, short max_border, short min_border) {
    while (1) {
        printf("%s，当前值=%d，范围[%d..%d]，请输入: ", attribute, *value, min_border, max_border);
        if (scanf("%hd", &num) != 1) {
            while (getchar() != '\n');  // 清空输入缓冲区
            continue;
        }
        if (num > max_border || num < min_border) {
            printf("非法的%s值：%d\n", attribute, num);
            continue;
        }
        else {
            *value = num;
            break;
        }
    }
}

// 判断并修改 int 类型数值
void judge_and_change_int(GameData* data, int* value, const char attribute[15], int num, int max_border, int min_border) {
    while (1) {
        printf("%s，当前值=%d，范围[%d..%d]，请输入: ", attribute, *value, min_border, max_border);
        if (scanf("%d", &num) != 1) {
            while (getchar() != '\n');  // 清空输入缓冲区
            continue;
        }
        if (num > max_border || num < min_border) {
            printf("非法的%s值：%d\n", attribute, num);
            continue;
        }
        else {
            *value = num;
            break;
        }
    }
}

// 判断并修改 long long 类型数值
void judge_and_change_long_long(GameData* data, long long* value, const char attribute[15], long long num, long long max_border, long long min_border) {
    while (1) {
        printf("%s，当前值=%lld，范围[%lld..%lld]，请输入: ", attribute, *value, min_border, max_border);
        if (scanf("%lld", &num) != 1) {
            while (getchar() != '\n');  // 清空输入缓冲区
            continue;
        }
        if (num > max_border || num < min_border) {
            printf("非法的%s值：%lld\n", attribute, num);
            continue;
        }
        else {
            *value = num;
            break;
        }
    }
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：整个函数，只允许出现一次fopen、一次fread（因为包含错误处理，允许多次fclose）
***************************************************************************/
int read()
{
    const char attributes[][22] = {
    "玩家昵称：", "生命值：", "力量值：", "体质值：", "灵巧值：", "金钱值：",
    "名声值：", "魅力值：", "游戏累计时间(us)值：", "移动速度值：", "攻击速度值：",
    "攻击范围值：", "攻击力值：", "防御力值：", "敏捷度值：", "智力值：",
    "经验值：", "等级值：", "魔法值：", "消耗魔法值：", "魔法伤害力值：",
    "魔法命中率值：", "魔法防御力值：", "暴击率值：", "耐力值："
    };
    FILE* fp = fopen("game.dat", "rb");
    if (!fp) 
    {
        fprintf(stderr, "无法打开文件 game.dat\n");
        return -1;
    }

    GameData data;
    if (fread(&data, 1, sizeof(GameData), fp) != sizeof(GameData)) 
    {
        fprintf(stderr, "读取文件失败\n");
        fclose(fp);
        return -1;
    }
    

    int length = strlen("游戏累计时间(us)值：");
    printf("%*s%s\n", length, attributes[0], data.nickname);
    printf("%*s%d\n", length, attributes[1], data.hp);
    printf("%*s%d\n", length, attributes[2], data.strength);
    printf("%*s%d\n", length, attributes[3], data.constitution);
    printf("%*s%d\n", length, attributes[4], data.agility);
    printf("%*s%d\n", length, attributes[5], data.money);
    printf("%*s%d\n", length, attributes[6], data.reputation);
    printf("%*s%d\n", length, attributes[7], data.charm);
    printf("%*s%lld\n", length, attributes[8], data.playTime);
    printf("%*s%d\n", length, attributes[9], (int)data.moveSpeed);
    printf("%*s%d\n", length, attributes[10], (int)data.attackSpeed);
    printf("%*s%d\n", length, attributes[11], (int)data.attackRange);
    printf("%*s%d\n", length, attributes[12], data.attackPower);
    printf("%*s%d\n", length, attributes[13], data.defense);
    printf("%*s%d\n", length, attributes[14], (int)data.dexterity);
    printf("%*s%d\n", length, attributes[15], (int)data.intelligence);
    printf("%*s%d\n", length, attributes[16], (int)data.experience);
    printf("%*s%d\n", length, attributes[17], (int)data.level);
    printf("%*s%d\n", length, attributes[18], data.mana);
    printf("%*s%d\n", length, attributes[19], (int)data.manaCost);
    printf("%*s%d\n", length, attributes[20], (int)data.magicDamage);
    printf("%*s%d\n", length, attributes[21], (int)data.hitRate);
    printf("%*s%d\n", length, attributes[22], (int)data.magicDefense);
    printf("%*s%d\n", length, attributes[23], (int)data.criticalRate);
    printf("%*s%d\n", length, attributes[24], (int)data.stamina);

    fclose(fp);
    return 0;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：整个函数，只允许出现一次open、一次read、一次write（因为包含错误处理，允许多次fclose）
***************************************************************************/
int modify()
{
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
        "魔法命中率", "魔法防御力", "暴击率", "耐力"
    };

    FILE* gfile = fopen("game.dat", "rb+");
    if (!gfile) {
        perror("无法打开文件 game.dat");
        return -1;
    }

    GameData data;
    if (fread(&data, sizeof(GameData), 1, gfile) != 1) {
        perror("读取文件失败");
        fclose(gfile);
        return -1;
    }

    char choice;
    do {
        printf("--------------------------------------\n");
        printf("  游戏存档文件修改工具\n");
        printf("--------------------------------------\n");
        printf("  %s(%s)\n", attributes[0], data.nickname);
        printf("  %s(%d)\n", attributes[1], data.hp);
        printf("  %s(%d)\n", attributes[2], data.strength);
        printf("  %s(%d)\n", attributes[3], data.constitution);
        printf("  %s(%d)\n", attributes[4], data.agility);
        printf("  %s(%d)\n", attributes[5], data.money);
        printf("  %s(%d)\n", attributes[6], data.reputation);
        printf("  %s(%d)\n", attributes[7], data.charm);
        printf("  %s(%lld)\n", attributes[8], data.playTime);
        printf("  %s(%d)\n", attributes[9], (int)data.moveSpeed);
        printf("  %s(%d)\n", attributes[10], (int)data.attackSpeed);
        printf("  %s(%d)\n", attributes[11], (int)data.attackRange);
        printf("  %s(%d)\n", attributes[12], data.attackPower);
        printf("  %s(%d)\n", attributes[13], data.defense);
        printf("  %s(%d)\n", attributes[14], (int)data.dexterity);
        printf("  %s(%d)\n", attributes[15], (int)data.intelligence);
        printf("  %s(%d)\n", attributes[16], (int)data.experience);
        printf("  %s(%d)\n", attributes[17], (int)data.level);
        printf("  %s(%d)\n", attributes[18], data.mana);
        printf("  %s(%d)\n", attributes[19], (int)data.manaCost);
        printf("  %s(%d)\n", attributes[20], (int)data.magicDamage);
        printf("  %s(%d)\n", attributes[21], (int)data.hitRate);
        printf("  %s(%d)\n", attributes[22], (int)data.magicDefense);
        printf("  %s(%d)\n", attributes[23], (int)data.criticalRate);
        printf("  %s(%d)\n", attributes[24], (int)data.stamina);
        printf("--------------------------------------\n");
        printf("  0.放弃修改\n");
        printf("  1.存盘退出\n");
        printf("--------------------------------------\n");
        printf("请选择[a..y, 0..1]: ");
#if defined(_MSC_VER) || defined(__MINGW32__) 
        choice = _getch();
#elif defined(__linux__)
        choice = getchar();
#endif
#if defined(_MSC_VER) || defined(__MINGW32__) 
        printf("%c\n", choice);
#endif
        printf("\n");
        short num_short = 0;
        int num_int = 0;
        long long num_long_long = 0LL;
        switch (choice) 
        {
            case 'a':
                printf("玩家昵称，当前值=%s，请输入: ", data.nickname);
#if defined(__linux__)
                while (getchar() != '\n' && getchar() != EOF);
#endif
                if (fgets(data.nickname, sizeof(data.nickname), stdin))
                    data.nickname[strcspn(data.nickname, "\n")] = '\0'; // 去掉换行符
                if (strcspn(data.nickname, "\n") == sizeof(data.nickname) - 1) {
                    char ch;
                    while ((ch = getchar()) != '\n' && ch != EOF);  // 读取并丢弃直到换行符
                }
                break;
            case 'b':
                judge_and_change_short(&data, &data.hp, attribute[1], num_short, 10000, 0);
                break;
            case 'c':
                judge_and_change_short(&data, &data.strength, attribute[2], num_short, 10000, 0);
                break;
            case 'd':
                judge_and_change_short(&data, &data.constitution, attribute[3], num_short, 8192, 0);
                break;
            case 'e':
                judge_and_change_short(&data, &data.agility, attribute[4], num_short, 1024, 0);
                break;
            case 'f':
                judge_and_change_int(&data, &data.money, attribute[5], num_int, 100000000, 0);
                break;
            case 'g':
                judge_and_change_int(&data, &data.reputation, attribute[6], num_int, 1000000, 0);
                break;
            case 'h':
                judge_and_change_int(&data, &data.charm, attribute[7], num_int, 1000000, 0);
                break;
            case 'i':
                judge_and_change_long_long(&data, &data.playTime, attribute[8], num_long_long, 10000000000000000LL, 0);
                break;
            case 'j':
                judge_and_change_char(&data, &data.moveSpeed, attribute[9], num_int, 127, 0);
                break;
            case 'k':
                judge_and_change_char(&data, &data.attackSpeed, attribute[10], num_int, 127, 0);
                break;
            case 'l':
                judge_and_change_char(&data, &data.attackRange, attribute[11], num_int, 127, 0);
                break;
            case 'm':
                judge_and_change_short(&data, &data.attackPower, attribute[12], num_short, 2000, 0);
                break;
            case 'n':
                judge_and_change_short(&data, &data.defense, attribute[13], num_short, 2000, 0);
                break;
            case 'o':
                judge_and_change_char(&data, &data.dexterity, attribute[14], num_int, 100, 0);
                break;
            case 'p':
                judge_and_change_char(&data, &data.intelligence, attribute[15], num_int, 100, 0);
                break;
            case 'q':
                judge_and_change_char(&data, &data.experience, attribute[16], num_int, 100, 0);
                break;
            case 'r':
                judge_and_change_char(&data, &data.level, attribute[17], num_int, 100, 0);
                break;
            case 's':
                judge_and_change_short(&data, &data.mana, attribute[18], num_short, 10000, 0);
                break;
            case 't':
                judge_and_change_char(&data, &data.manaCost, attribute[19], num_int, 100, 0);
                break;
            case 'u':
                judge_and_change_char(&data, &data.magicDamage, attribute[20], num_int, 100, 0);
                break;
            case 'v':
                judge_and_change_char(&data, &data.hitRate, attribute[21], num_int, 100, 0);
                break;
            case 'w':
                judge_and_change_char(&data, &data.magicDefense, attribute[22], num_int, 100, 0);
                break;
            case 'x':
                judge_and_change_char(&data, &data.criticalRate, attribute[23], num_int, 100, 0);
                break;
            case 'y':
                judge_and_change_char(&data, &data.stamina, attribute[24], num_int, 100, 0);
                break;
            case '0':
                fclose(gfile);
                return 0;
            case '1':
                fseek(gfile, 0, SEEK_SET);
                if (fwrite(&data, sizeof(GameData), 1, gfile) != 1) {
                    perror("文件写入失败");
                    fclose(gfile);
                    return -1;
                }
                fclose(gfile);
                return 0;
            default:
                continue;
        }
    } while (1);

    fclose(gfile);
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
    if (argc < 2) {
        fprintf(stderr, "usage : 15-b7-2 --modify | --read\n");
        return -1;
    }

    if (strcmp(argv[1], "--read") == 0) 
        read();
    else if (strcmp(argv[1], "--modify") == 0) 
        modify();
    else {
        fprintf(stderr, "usage: program --modify | --read\n");
        return -1;
    }

    return 0;
}