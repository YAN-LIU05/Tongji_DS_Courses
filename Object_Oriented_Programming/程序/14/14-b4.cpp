/* 2352018 大数据 刘彦 */
#include <iostream>
#include <iomanip>
#include <cstring>
using namespace std;

#define PING_NUM  3
#define MAX_LEN1  5
#define MAX_LEN2  9
#define MAX_LEN3  12
#define MAX_LEN4  6
#define MAX_SIZE  64000
#define MIN_SIZE  32
#define DEFAULT_SIZE  64
#define MAX_AMOUNT  1024
#define MIN_AMOUNT  1
#define DEFAULT_AMOUNT  4

class ping 
{
    public:
        const char* name;        // 参数名称
        const char* description; // 参数的描述
        int count;              // 附加参数的个数
        int origin;             // 默认值
        int value;              // 当前值
        int minimum;            // 允许的最小值
        int maximum;            // 允许的最大值

        // 构造函数，用于初始化成员变量
        ping(const char* n, const char* desc, int c, int o, int min, int max)
        {
            name = n;          // 设置参数名称
            description = desc; // 设置参数描述
            count = c;        // 设置附加参数个数
            origin = o;       // 设置默认值
            value = o;        // 当前值初始化为默认值
            minimum = min;    // 设置最小值
            maximum = max;    // 设置最大值
        }

        int int_bit_num(int value) const
        {
            if (value == 0) // 0 有 1 位
                return 1;
            int cnt = 0;
            while (value > 0)
            {
                cnt++;
                value /= 10; // 每次将值除以 10
            }
            return cnt; // 返回位数
        }

        static int my_max(int a, int b)
        {
            return (a > b) ? a : b; // 返回较大的值
        }

        static void calculate_max_lengths(const ping para_menu[], int max_length[], int temp_length[])
        {
            for (int j = 0; j < PING_NUM; j++)
            {
                temp_length[0] = my_max(int(strlen(para_menu[j].name)), temp_length[0]);
                temp_length[1] = my_max(para_menu[j].count, temp_length[1]);
                temp_length[2] = my_max(para_menu[j].int_bit_num(para_menu[j].minimum) +
                    para_menu[j].int_bit_num(para_menu[j].maximum) + 4,
                    temp_length[2]);
                temp_length[3] = my_max(para_menu[j].int_bit_num(para_menu[j].origin), temp_length[3]);
            }

            // 更新 max_length 数组
            for (int i = 0; i < 4; i++) {
                max_length[i] = my_max(max_length[i], temp_length[i] + 1);
            }
        }
};

// 验证 IP 段
bool check_ip_segment(const char* segment_start, int length)
{
    if (length == 0) return false; // 段为空，返回无效

    int segment_value = 0; // 当前段的数值

    // 将段转换为整数
    for (int j = 0; j < length; ++j)
    {
        if (segment_start[j] < '0' || segment_start[j] > '9')
        {
            return false; // 不是数字，标记为无效
        }
        segment_value = segment_value * 10 + (segment_start[j] - '0'); // 计算数值
    }

    // 检查段的有效性
    if (segment_value < 0 || segment_value > 255)
        return false; // 值超出范围
    if (length > 1 && segment_start[0] == '0')
        return false; // 前导零不合法

    return true; // 段有效
}

// 验证 ipv4 函数
bool check_ipv4(const char* ip_str)
{
    int segments[4] = { 0 }; // 用于存储每个段的长度
    int segment_count = 0;   // 段计数
    const char* segment_start = ip_str; // 当前段的起始位置

    // 遍历 IP 字符串，查找分隔符 '.'
    for (const char* p = ip_str; *p; ++p)
    {
        if (*p == '.')
        {
            if (segment_count >= 4)
                return false; // 段数超过 4，返回 false
            segments[segment_count++] = p - segment_start; // 记录段的长度
            segment_start = p + 1; // 更新下一个段的起始位置
        }
    }

    // 处理最后一个段
    int last_segment_length = strlen(segment_start);
    if (segment_count != 3 || last_segment_length == 0)
        return false; // 必须有 4 个段且最后一段不能为空

    // 验证每个段
    segment_start = ip_str; // 重置段的起始位置
    for (int i = 0; i < 4; ++i)
    {
        if (i < 3)
        {
            if (!check_ip_segment(segment_start, segments[i]))
                return false; // 如果段无效，返回 false
            segment_start += segments[i] + 1; // 更新下一个段的起始位置
        }
        else
        {
            // 检查最后一段的有效性
            if (!check_ip_segment(segment_start, last_segment_length))
                return false; // 如果最后一段无效，返回 false
        }
    }

    return true; // 所有段均有效
}


int usage(const char* const procname, const ping para_menu[]) 
{
    cout << "Usage: " << procname << " ";
    for (int i = 0; i < PING_NUM; i++) 
    {
        cout << "[" << para_menu[i].name;
        if (para_menu[i].description != nullptr)
            cout << " " << para_menu[i].description;
        cout << "] ";
    }
    cout << "IP地址" << endl;

    // 计算最大长度
    int max_length[4] = { MAX_LEN1, MAX_LEN2, MAX_LEN3, MAX_LEN4 };
    int temp_length[4] = { 0 };

    ping::calculate_max_lengths(para_menu, max_length, temp_length);

    // 打印分隔线
    cout << "       " << "=";
    for (int i = 0; i < 4; i++)
        cout << setiosflags(ios::left) << setw(max_length[i]) << setfill('=') << '=';
    cout << "=" << endl;

    // 打印标题
    cout << "        ";
    cout << setiosflags(ios::left) << setw(max_length[0]) << setfill(' ') << "参数";
    cout << setiosflags(ios::left) << setw(max_length[1]) << setfill(' ') << "附加参数";
    cout << setiosflags(ios::left) << setw(max_length[2]) << setfill(' ') << "范围";
    cout << setiosflags(ios::left) << setw(max_length[3]) << setfill(' ') << "默认值";
    cout << endl;

    // 打印分隔线
    cout << "       =";
    for (int i = 0; i < 4; i++)
        cout << setiosflags(ios::left) << setw(max_length[i]) << setfill('=') << '=';
    cout << "=" << endl;

    // 打印参数信息
    for (int i = 0; i < PING_NUM; i++) {
        int tem_len = max_length[2] - 3 - para_menu[i].int_bit_num(para_menu[i].minimum) - para_menu[i].int_bit_num(para_menu[i].maximum);
        cout << setw(8) << setfill(' ') << " ";
        cout << setiosflags(ios::left) << setw(max_length[0]) << setfill(' ') << para_menu[i].name;
        cout << setiosflags(ios::left) << setw(max_length[1]) << setfill(' ') << para_menu[i].count;
        cout << "[" << para_menu[i].minimum << ".." << para_menu[i].maximum << setw(tem_len) << setfill(' ') << "] ";
        cout << para_menu[i].origin << endl;
    }

    // 打印分隔线
    cout << "       " << "=";
    for (int i = 0; i < 4; i++)
        cout << setiosflags(ios::left) << setw(max_length[i]) << setfill('=') << '=';
    cout << "=" << endl;

    return 0;
}

int main(int argc, char* argv[])
{
    // 初始化参数菜单
    ping para_menu[PING_NUM] = 
    {
        ping("-l", "大小", 1, DEFAULT_SIZE, MIN_SIZE, MAX_SIZE),
        ping("-n", "数量", 1, DEFAULT_AMOUNT, MIN_AMOUNT, MAX_AMOUNT),
        ping("-t", "持续发送", 0, 0, 0, 1)
    };

    // 检查命令行参数数量
    if (argc < 2)
    {
        usage(argv[0], para_menu); // 显示使用说明
        return 0;
    }

    // 验证最后一个参数是否为合法的 IP 地址
    if (!check_ipv4(argv[argc - 1]))
    {
        cout << "IP地址错误" << endl; // 提示 IP 地址错误
        return 0;
    }

    // 处理命令行参数
    for (int i = 1; i < argc - 1; ++i)
    {
        if (argv[i][0] != '-') // 确保参数以 '-' 开头
        {
            cout << "参数" << argv[i] << "不是以-开头的合法参数" << endl;
            return 0; // 提示参数格式错误
        }
        int param_id = -1;
        for (int j = 0; j < PING_NUM; ++j)
        {
            if (strcmp(argv[i], para_menu[j].name) == 0)
            {
                param_id = j; // 找到参数 ID
                break;
            }
        }
        if (param_id == -1)
        {
            cout << "参数" << argv[i] << "不存在" << endl; // 提示参数不存在
            return 0;
        }

        // 处理带有附加参数的选项
        if (para_menu[param_id].count == 0)     //对"-t"进行的特判      
        {
            para_menu[param_id].value = 1;          
            continue;
        }
        if (para_menu[param_id].count > 0)
        {
            if (i + 1 >= argc || argv[i + 1][0] == '-')
            {
                cout << "参数" << argv[i] << "没有后续参数" << endl; // 提示缺少参数值
                return 0;
            }

            bool valid = true; // 标记参数值是否有效
            int param_value = 0; // 初始化参数值
            int sign = 1; // 初始化符号为正
            const char* param_arg = argv[i + 1]; // 获取参数值
            int length = strlen(param_arg); // 获取参数值的长度

            // 转换参数值为整数
            for (int j = 0; j < length; ++j)
            {
                if (j == 0 && param_arg[j] == '-')
                {
                    sign = -1; // 处理负号
                    continue;
                }
                if (param_arg[j] < '0' || param_arg[j] > '9')
                {
                    valid = false; // 非数字字符标记为无效
                    break;
                }
                param_value = param_value * 10 + (param_arg[j] - '0'); // 计算参数值
            }
            param_value *= sign; // 应用符号

            // 检查参数值的范围
            if (valid && param_value >= para_menu[param_id].minimum && param_value <= para_menu[param_id].maximum)
                para_menu[param_id].value = param_value; // 设置有效值
            else
                para_menu[param_id].value = para_menu[param_id].origin; // 使用默认值
            ++i; // 跳过已处理的参数
        }
    }

    // 输出参数检查结果
    cout << "参数检查通过" << endl;
    for (int i = 0; i < PING_NUM; ++i)
        cout << para_menu[i].name << " 参数：" << para_menu[i].value << endl; // 打印每个参数的值
    cout << "IP地址：" << argv[argc - 1] << endl; // 打印 IP 地址

    return 0;
}