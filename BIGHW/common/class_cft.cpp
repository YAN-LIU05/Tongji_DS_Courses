/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <sstream>
/* 添加自己需要的头文件，注意限制 */
#include "../include/class_cft.h"
using namespace std;

/* 由于一开始使用get进行读取，只有在处理homework.conf时，读取有效内容非空,不是组,也没有分隔符的项会出现问题 */

/* 给出各种自定义函数的实现（已给出的内容不全） */
char my_tolower(char ch) 
{
	if (ch >= 'A' && ch <= 'Z') 
		return ch + ('a' - 'A');
	return ch;
}

int my_strcasecmp(const char* s1, const char* s2) 
{
	while (*s1 && *s2) 
	{
		char c1 = my_tolower(static_cast<unsigned char>(*s1));
		char c2 = my_tolower(static_cast<unsigned char>(*s2));
		if (c1 != c2) 
			return c1 - c2;
		++s1;
		++s2;
	}
	return my_tolower(static_cast<unsigned char>(*s1)) -
		my_tolower(static_cast<unsigned char>(*s2));
}

int find_group(const vector<string>& source, const char* const name, const bool group_is_case_sensitive)
{
	if (name == nullptr)
		return -1;

	if (name == "")
		return 0;
	for (size_t i = 0; i < source.size() - 1; i++)
	{


		if (source[i].size() != strlen(name))
			continue;
		//if (i == source.size() - 1)
		//	break;
		if (!group_is_case_sensitive)
		{
			// 不区分大小写的比较
			bool match = true;
			for (size_t j = 0; j < source[i].size(); ++j)
			{
				if (j >= strlen(name) || my_tolower(source[i][j]) != my_tolower(name[j]))
				{
					match = false;
					break;
				}
			}
			if (match && strlen(name) == source[i].size())
			{
				//if (i == source.size() - 1)
				//	return static_cast<int>(i - 1);
				return static_cast<int>(i);
			}
		}
		else
		{
			// 区分大小写的比较
			if (source[i] == name)
			{
				//if (i == source.size() - 1)
				//	return static_cast<int>(i - 1);
				return static_cast<int>(i);
			}
		}
	}


	return 0; // 未找到匹配的组
}

int find_group(const vector<string>& source, const string& name, const bool group_is_case_sensitive)
{
	if (name == "")
		return 0;
	int group_index = -1;
	for (size_t i = 0; i < source.size() - 1; ++i)
	{
		if (i == source.size() - 1)
			break;
		if (source[i].size() != name.size())
			continue;
		if (!group_is_case_sensitive)
		{
			group_index = 1;
			for (size_t j = 0; j < source[i].size(); ++j)  // 不区分大小写，手写实现
			{
				if (my_tolower(source[i][j]) != my_tolower(name[j]))
				{
					group_index = -1;
					break;
				}
			}
			if (group_index != -1)
			{
				group_index = (int)(i);
				break;
			}
		}
		else
		{
			if (source[i] == name) // 如果区分大小写，直接使用 == 运算符进行比较
			{
				group_index = (int)(i); // 找到匹配项，记录索引位置
				break;
			}
		}
	}
	if (group_index == -1)
		return -1;
	else
		return group_index;
}

int find_item(const vector<item>& source, const char* const name, const bool item_is_case_sensitive)
{
	int item_index = -1;
	if (name == NULL)
		return -1;
	for (size_t i = 0; i < source.size(); ++i)
	{
		if (source[i].name.size() != strlen(name))
			continue;
		if (!item_is_case_sensitive)
		{
			item_index = 1;
			for (size_t j = 0; j < source[i].name.size(); ++j)  // 不区分大小写，手写实现
			{
				if (my_tolower(source[i].name[j]) != my_tolower(name[j]))
				{
					item_index = -1;
					break;
				}
			}
			if (item_index != -1)
			{
				item_index = (int)(i);
				break;
			}
		}
		else
		{
			if (source[i].name == name) // 如果区分大小写，直接使用 == 运算符进行比较
			{
				item_index = (int)(i); // 找到匹配项，记录索引位置
				break;
			}
		}
	}
	if (item_index == -1)
		return -1;
	else
		return item_index;
}

int find_item(const vector<item>& source, const string& name, const bool item_is_case_sensitive)
{
	int item_index = -1;
	for (size_t i = 0; i < source.size(); ++i)
	{
		if (source[i].name.size() != name.size())
			continue;
		if (!item_is_case_sensitive)
		{
			item_index = 1;
			for (size_t j = 0; j < source[i].name.size(); ++j)  // 不区分大小写，手写实现
			{
				if (my_tolower(source[i].name[j]) != my_tolower(name[j]))
				{
					item_index = -1;
					break;
				}
			}
			if (item_index != -1)
			{
				item_index = (int)(i);
				break;
			}
		}
		else
		{
			if (source[i].name == name) // 如果区分大小写，直接使用 == 运算符进行比较
			{
				item_index = (int)(i); // 找到匹配项，记录索引位置
				break;
			}
		}
	}
	if (item_index == -1)
		return -1;
	else
		return item_index;
}

int read_cfgfile(config_file_tools& cfg)
{
	if (!cfg.is_read_succeeded())
		return 0;

	cfg.in.clear();
	cfg.in.seekg(0, ios::beg);  // 文件指针移至开头
	int beg_index = 0, end_index = 0;
	int line_num = 0, last_group_num = 0, new_group_num = 0;
	vector<char> line_content;
	char ch;
	string current_value;  // 存储跨行的值
	bool value_pending = false;  // 标记是否在等待新行作为值的一部分

	while (!cfg.in.eof())
	{
		// 读取一行并去掉行尾的注释和空白
		while ((ch = cfg.in.get()) != '\r' && ch != '\n' && (!cfg.in.eof()))
		{
			if (ch == ';' || ch == '#' || ch == '<') // 注释处理
			{
				while ((ch = cfg.in.get()) != '\r' && ch != '\n' && (!cfg.in.eof()))
					;

				break;
			}
			if (ch == '/') {
				char next_ch = cfg.in.peek();  // 查看下一个字符
				if (next_ch == '/') {
					// 是双斜杠注释，跳过整行
					while ((ch = cfg.in.get()) != '\r' && ch != '\n' && (!cfg.in.eof()));
					if (ch == '\r') {
						ch = cfg.in.get();  // Windows换行符处理
					}
					break;  // 跳出当前行循环
				}
			}
			line_content.push_back(ch);
		}
		++line_num;



		// 去除空格/tab
		if (!line_content.empty()) {
			while (!line_content.empty() && (line_content.front() == ' ' || line_content.front() == '\t'))
				line_content.erase(line_content.begin());
			while (!line_content.empty() && (line_content.back() == ' ' || line_content.back() == '\t'))
				line_content.pop_back();
		}

		// 如果有未处理的值，检查是否需要继续拼接下一行
		if (value_pending && !line_content.empty()) {
			current_value += " " + string(line_content.begin(), line_content.end());
			line_content.clear();
			continue;
		}

		// 如果是组名 [group]，则处理组名
		if (!line_content.empty() && line_content.front() == '[' && line_content.back() == ']')
		{
			beg_index = 1;
			end_index = (int)line_content.size() - 2;
			while (line_content[beg_index] == ' ' || line_content[beg_index] == '\t')
				++beg_index;
			while (line_content[end_index] == ' ' || line_content[end_index] == '\t')
				--end_index;

			string temp(line_content.data() + beg_index, end_index - beg_index + 1);
			temp.push_back(']');
			temp.insert(temp.begin(), '[');
			cfg.all_group.push_back(temp);  // 保存组名
		}
		else
		{
			// 根据分隔符处理项名和值
			int equal_pos = -1;
			if (cfg.item_separate_character_type == BREAK_CTYPE::Equal) {
				// 如果是Equal模式，查找 '='
				for (size_t i = 0; i < line_content.size(); ++i)
				{
					if (line_content[i] == '=')
					{
						equal_pos = (int)i;
						break;
					}
				}
			}
			else {
				// 如果是Space模式，查找第一个空格或Tab
				for (size_t i = 0; i < line_content.size(); ++i)
				{
					if (line_content[i] == ' ' || line_content[i] == '\t')
					{
						equal_pos = (int)i;
						break;
					}
				}
			}
			item temp_item;
			if (equal_pos == -1) {
				// 检查是否为组名（如 [group]）
				if (!line_content.empty() && line_content.front() == '[' && line_content.back() == ']') {
					string temp(line_content.data() + beg_index, end_index - beg_index + 1);
					temp.push_back(']');
					temp.insert(temp.begin(), '[');
					cfg.all_group.push_back(temp);  // 保存组名
				}


				continue;
			}

			// 处理项名
			beg_index = 0;
			end_index = equal_pos - 1;
			while (line_content[beg_index] == ' ' || line_content[beg_index] == '\t')
				++beg_index;
			while (line_content[end_index] == ' ' || line_content[end_index] == '\t')
				--end_index;

			//item temp_item;
			string item_name(line_content.begin() + beg_index, line_content.begin() + end_index + 1);
			if (item_name.find('[') != string::npos || item_name.find(']') != string::npos) {
				// 跳过当前行处理
				continue;
			}
			temp_item.name = item_name;

			// 处理项的值
			beg_index = equal_pos + 1;
			end_index = (int)line_content.size() - 1;
			if (beg_index > end_index)
				temp_item.value = "";  // 处理空值
			else
			{
				while (line_content[beg_index] == ' ' || line_content[beg_index] == '\t')
					++beg_index;
				while (line_content[end_index] == ' ' || line_content[end_index] == '\t')
					--end_index;

				int length = end_index - beg_index + 1;
				string value(line_content.begin() + beg_index, line_content.begin() + end_index + 1);
				temp_item.value = value;
			}


			if (cfg.item_separate_character_type == BREAK_CTYPE::Equal)
				temp_item.expression = temp_item.name + " = " + temp_item.value;
			else
				temp_item.expression = temp_item.name + " " + temp_item.value;
			// 保存项
			if (cfg.all_group.empty())
				cfg.all_group.push_back("");  // 特殊处理没有组的情况


			new_group_num = (int)cfg.all_group.size();
			while (last_group_num < new_group_num)
			{
				cfg.all_item.push_back(vector<item>());
				++last_group_num;
			}
			cfg.all_item[new_group_num - 1].push_back(temp_item);  // 添加到当前组

		}

		// 清理数据为下一行做准备
		line_content.clear();
		beg_index = end_index = 0;
	}
	return 1;
}


/***************************************************************************
  函数名称： 
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
config_file_tools::config_file_tools(const char* const _cfgname, const enum BREAK_CTYPE _ctype)
{
	this->cfgname = _cfgname;
	this->item_separate_character_type = _ctype;
	this->_is_open = false;  // 默认值
	ifstream fin(_cfgname);
	// 路径分隔符转换
	for (size_t i = 0; i < this->cfgname.size(); ++i)
	{
		if (this->cfgname[i] == '\\')
			this->cfgname[i] = '/';  // 将 '\\' 替换为 '/'
	}
	string line;
	int line_cnt = 1;
	while (getline(fin, line))
	{
		line_cnt++;
		size_t line_len = line.length() + 2;
	}
	cfg_list.push_back(line);
	// 打开配置文件
	this->in.open(this->cfgname, ios::in | ios::binary);
	this->all_group.clear();  // 清空所有组
	this->all_item.clear();   // 清空所有项

	// 读取配置文件内容
	if (!read_cfgfile(*this)) 
		this->_is_open = false;
	else 
		this->_is_open = true;
	fin.close();
}


/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
config_file_tools::config_file_tools(const string& _cfgname, const enum BREAK_CTYPE _ctype)
{
	this->cfgname = _cfgname;
	this->item_separate_character_type = _ctype;
	this->_is_open = false;  // 默认值
	ifstream fin(_cfgname);
	// 路径分隔符转换
	for (size_t i = 0; i < this->cfgname.size(); ++i)
	{
		if (this->cfgname[i] == '\\')
			this->cfgname[i] = '/';  // 将 '\\' 替换为 '/'
	}
	string line;
	int line_cnt = 1;
	while (getline(fin, line))
	{
		line_cnt++;
		size_t line_len = line.length() + 2;
	}
	cfg_list.push_back(line);
	// 打开配置文件
	this->in.open(this->cfgname, ios::in | ios::binary);
	this->all_group.clear();  // 清空所有组
	this->all_item.clear();   // 清空所有项

	// 读取配置文件内容
	if (!read_cfgfile(*this)) 
		this->_is_open = false;
	else 
		this->_is_open = true;
	fin.close();
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
config_file_tools::~config_file_tools()
{
	all_group.clear();
	all_item.clear();
	in.close();
}


/***************************************************************************
  函数名称：
  功    能：判断读配置文件是否成功
  输入参数：
  返 回 值：true - 成功，已读入所有的组/项
		   false - 失败，文件某行超长/文件全部是注释语句
  说    明：
***************************************************************************/
bool config_file_tools::is_read_succeeded() const
{
	if (!in.is_open())
		return false;
	else
		return true;
}

/***************************************************************************
  函数名称：
  功    能：返回配置文件中的所有组
  输入参数：vector <string>& ret : vector 中每项为一个组名
  返 回 值：读到的组的数量（简单配置文件的组数量为1，组名为"）
  说    明：
***************************************************************************/
int config_file_tools::get_all_group(vector <string>& ret)
{
	ret.clear();
	for (size_t i = 0; i < all_group.size(); i++)
		ret.push_back(all_group[i]);
	return static_cast<int>(ret.size());
}

/***************************************************************************
  函数名称：
  功    能：查找指定组的所有项并返回项的原始内容
  输入参数：const char* const group_name：组名
		   vector <string>& ret：vector 中每项为一个项的原始内容
		   const bool is_case_sensitive = false : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：项的数量，0表示空
  说    明：
***************************************************************************/
int config_file_tools::get_all_item(const char* const group_name, vector<string>& ret, const bool is_case_sensitive)
{
	ret.clear();  // 清空返回的向量
	// 查找组的索引
	int group_index = find_group(all_group, group_name, is_case_sensitive);
	if (group_index == -1) 
	{
		if (all_group.empty())
		{
			all_group.push_back("");
			group_index = 0;
		}
		else 
			return 0;
	}

	
	// 如果找到指定组，返回该组中的所有项

	for (size_t i = 0; i < all_item[group_index].size(); i++) 
		ret.push_back(all_item[group_index][i].expression);  // 将项的表达式加入返回列表

	return (int)ret.size();  // 返回找到的项数
}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int config_file_tools::get_all_item(const string& group_name, vector <string>& ret, const bool is_case_sensitive)
{
	ret.clear();
	int group_index = find_group(all_group, group_name, !is_case_sensitive);
	if (group_index == -1)
		return 0;
	else
		for (size_t i = 0; i < all_item[group_index].size(); i++)
			ret.push_back(all_item[group_index][i].expression);
	return (int)ret.size();
}

/***************************************************************************
  函数名称：
  功    能：取某项的原始内容（=后的所有字符，string方式）
  输入参数：const char* const group_name
		   const char* const item_name
		   string &ret
		   const bool group_is_case_sensitive = false : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
		   const bool item_is_case_sensitive = false  : 项名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：
  说    明：
***************************************************************************/
int config_file_tools::item_get_raw(const char* const group_name, const char* const item_name, string& ret, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	if (group_name == nullptr || item_name == nullptr)
		return 0;
	int group_index = find_group(all_group, group_name, group_is_case_sensitive);
	if (group_index == all_group.size())
		return 0;
	int item_index = find_item(all_item[group_index], item_name, item_is_case_sensitive);
	if (item_index == all_item[group_index].size())
		return 0;
	ret = all_item[group_index][item_index].value;
	return 1;
}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int config_file_tools::item_get_raw(const string& group_name, const string& item_name, string& ret, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	/* 本函数已实现 */
	return this->item_get_raw(group_name.c_str(), item_name.c_str(), ret, group_is_case_sensitive, item_is_case_sensitive);
}

/***************************************************************************
  函数名称：
  功    能：取某项的内容，返回类型为char型
  输入参数：const char* const group_name               ：组名
		   const char* const item_name                ：项名
		   const bool group_is_case_sensitive = false : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
		   const bool item_is_case_sensitive = false  : 项名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：1 - 该项的项名存在
		   0 - 该项的项名不存在
  说    明：
***************************************************************************/
int config_file_tools::item_get_null(const char* const group_name, const char* const item_name, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	if (group_name == nullptr || item_name == nullptr)
		return 0;
	int group_index = find_group(all_group, group_name, group_is_case_sensitive);
	if (group_index == all_group.size())
		return 0;
	int item_index = find_item(all_item[group_index], item_name, item_is_case_sensitive);
	if (item_index == all_item[group_index].size())
		return 0;
	return 1;
}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：因为工具函数一般在程序初始化阶段被调用，不会在程序执行中被高频次调用，
		   因此这里直接套壳，会略微影响效率，但不影响整体性能（对高频次调用，此方法不适合）
***************************************************************************/
int config_file_tools::item_get_null(const string& group_name, const string& item_name, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	/* 本函数已实现 */
	return this->item_get_null(group_name.c_str(), item_name.c_str(), group_is_case_sensitive, item_is_case_sensitive);
}

/***************************************************************************
  函数名称：
  功    能：取某项的内容，返回类型为char型
  输入参数：const char* const group_name               ：组名
		   const char* const item_name                ：项名
		   char& value                                ：读到的char的值（返回1时可信，返回0则不可信）
		   const char* const choice_set = nullptr     ：合法的char的集合（例如："YyNn"表示合法输入为Y/N且不分大小写，该参数有默认值nullptr，表示全部字符，即不检查）
		   const char def_value = DEFAULT_CHAR_VALUE  ：读不到/读到非法的情况下的默认值，该参数有默认值DEFAULT_CHAR_VALUE，分两种情况
															当值是   DEFAULT_CHAR_VALUE 时，返回0（值不可信）
															当值不是 DEFAULT_CHAR_VALUE 时，令value=def_value并返回1
		   const bool group_is_case_sensitive = false : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
		   const bool item_is_case_sensitive = false  : 项名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：1 - 取到正确值
			   未取到值/未取到正确值，设置了缺省值（包括设为缺省值）
		   0 - 未取到（只有为未指定默认值的情况下才会返回0）
  说    明：
***************************************************************************/
int config_file_tools::item_get_char(const char* const group_name, const char* const item_name, char& value,
	const char* const choice_set, const char def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	value = def_value; // 初始化为默认值

	// 查找组索引
	int group_index = -1;
	for (size_t i = 0; i < all_group.size(); ++i)
	{
		bool match = group_is_case_sensitive ? (all_group[i] == group_name) : (my_strcasecmp(all_group[i].c_str(), group_name) == 0);
		if (match) 
		{
			group_index = static_cast<int>(i);
			break;
		}
	}

	if (group_index == -1)  // 未找到组
		return def_value == DEFAULT_CHAR_VALUE ? 0 : 1;

	// 查找项索引
	int item_index = -1;
	for (size_t i = 0; i < all_item[group_index].size(); ++i) 
	{
		bool match = item_is_case_sensitive ? (all_item[group_index][i].name == item_name) : (my_strcasecmp(all_item[group_index][i].name.c_str(), item_name) == 0);
		if (match) 
		{
			item_index = static_cast<int>(i);
			break;
		}
	}

	if (item_index == -1)  // 未找到项
		return def_value == DEFAULT_CHAR_VALUE ? 0 : 1;

	// 获取项值
	const string& item_value = all_item[group_index][item_index].value;
	if (item_value.empty() || item_value.size() != 1) // 值为空或不是单字符
		return def_value == DEFAULT_CHAR_VALUE ? 0 : 1;

	char parsed_value = item_value[0];

	// 检查是否在合法集合中
	if (choice_set != nullptr && strchr(choice_set, parsed_value) == nullptr) 
		return def_value == DEFAULT_CHAR_VALUE ? 0 : 1;

	// 赋值并返回
	value = parsed_value;
	return 1; // 返回1表示成功读取合法值
}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：因为工具函数一般在程序初始化阶段被调用，不会在程序执行中被高频次调用，
		   因此这里直接套壳，会略微影响效率，但不影响整体性能（对高频次调用，此方法不适合）
***************************************************************************/
int config_file_tools::item_get_char(const string& group_name, const string& item_name, char& value,
	const char* const choice_set, const char def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	/* 本函数已实现 */
	return this->item_get_char(group_name.c_str(), item_name.c_str(), value, choice_set, def_value, group_is_case_sensitive, item_is_case_sensitive);
}

/***************************************************************************
  函数名称：
  功    能：取某项的内容，返回类型为int型
  输入参数：const char* const group_name               ：组名
		   const char* const item_name                ：项名
		   int& value                                 ：读到的int的值（返回1时可信，返回0则不可信）
		   const int min_value = INT_MIN              : 期望数据范围的下限，默认为INT_MIN
		   const int max_value = INT_MAX              : 期望数据范围的上限，默认为INT_MAX
		   const int def_value = DEFAULT_INT_VALUE    ：读不到/读到非法的情况下的默认值，该参数有默认值 DEFAULT_INT_VALUE，分两种情况
															当值是   DEFAULT_INT_VALUE 时，返回0（值不可信）
															当值不是 DEFAULT_INT_VALUE 时，令value=def_value并返回1
		   const bool group_is_case_sensitive = false : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
		   const bool item_is_case_sensitive = false  : 项名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：
  说    明：
***************************************************************************/
int config_file_tools::item_get_int(const char* const group_name, const char* const item_name, int& value,
	const int min_value, const int max_value, const int def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	// 如果 def_value 是默认值，返回的值不可信
	if (def_value == DEFAULT_INT_VALUE) 
		value = def_value;

	// 查找组索引
	int group_index = find_group(all_group, group_name, group_is_case_sensitive);
	if (group_index == -1)  // 未找到组
		return def_value == DEFAULT_INT_VALUE ? 0 : 1;

	// 查找项索引
	int item_index = find_item(all_item[group_index], item_name, item_is_case_sensitive);
	if (item_index == -1) 
		return 0;  // 未找到项，返回 0 表示值不可信

	// 获取项的值并尝试将其解析为整数
	const string& item_value = all_item[group_index][item_index].value;
	char* endptr;
	long parsed_value = strtol(item_value.c_str(), &endptr, 10);

	// 检查解析是否成功
	if (*endptr != '\0' || parsed_value < min_value || parsed_value > max_value) 
	{
		// 解析失败或值超出范围
		if (def_value != DEFAULT_INT_VALUE) 
			value = def_value;  // 设置为默认值
		return 0;  // 返回 0 表示值不可信
	}

	// 解析成功且在范围内，将值赋给 value
	value = static_cast<int>(parsed_value);
	return 1;
}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：因为工具函数一般在程序初始化阶段被调用，不会在程序执行中被高频次调用，
		   因此这里直接套壳，会略微影响效率，但不影响整体性能（对高频次调用，此方法不适合）
***************************************************************************/
int config_file_tools::item_get_int(const string& group_name, const string& item_name, int& value,
	const int min_value, const int max_value, const int def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	/* 本函数已实现 */
	return this->item_get_int(group_name.c_str(), item_name.c_str(), value, min_value, max_value, def_value, group_is_case_sensitive, item_is_case_sensitive);
}

/***************************************************************************
  函数名称：
  功    能：取某项的内容，返回类型为double型
  输入参数：const char* const group_name                  ：组名
		   const char* const item_name                   ：项名
		   double& value                                 ：读到的int的值（返回1时可信，返回0则不可信）
		   const double min_value = __DBL_MIN__          : 期望数据范围的下限，默认为INT_MIN
		   const double max_value = __DBL_MAX__          : 期望数据范围的上限，默认为INT_MAX
		   const double def_value = DEFAULT_DOUBLE_VALUE ：读不到/读到非法的情况下的默认值，该参数有默认值DEFAULT_DOUBLE_VALUE，分两种情况
																当值是   DEFAULT_DOUBLE_VALUE 时，返回0（值不可信）
																当值不是 DEFAULT_DOUBLE_VALUE 时，令value=def_value并返回1
		   const bool group_is_case_sensitive = false     : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
		   const bool item_is_case_sensitive = false      : 项名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：
  说    明：
***************************************************************************/
int config_file_tools::item_get_double(const char* const group_name, const char* const item_name, double& value,
	const double min_value, const double max_value, const double def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	if (def_value == DEFAULT_DOUBLE_VALUE) 
		value = def_value;
	// 查找组索引
	int group_index = find_group(all_group, group_name, group_is_case_sensitive);
	if (group_index == -1)  // 未找到组
		return def_value == DEFAULT_DOUBLE_VALUE ? 0 : 1;

	// 查找项索引
	int item_index = find_item(all_item[group_index], item_name, item_is_case_sensitive);
	if (item_index == -1)
		return -1;

	// 获取项的值
	const string& item_value = all_item[group_index][item_index].value;
	if (item_value.empty())
		return 0;

	// 验证是否为有效浮点数
	const char* str = item_value.c_str();
	char* endptr = nullptr;
	double temp_value = strtod(str, &endptr);

	// 检查解析是否成功
	if (*endptr != '\0' || str == endptr) // 检查是否解析到字符串末尾
		return 0;

	// 检查范围是否合法
	if (temp_value < min_value || temp_value > max_value)
		return 0;

	value = temp_value;
	return 1;

}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：因为工具函数一般在程序初始化阶段被调用，不会在程序执行中被高频次调用，
		   因此这里直接套壳，会略微影响效率，但不影响整体性能（对高频次调用，此方法不适合）
***************************************************************************/
int config_file_tools::item_get_double(const string& group_name, const string& item_name, double& value,
	const double min_value, const double max_value, const double def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	/* 本函数已实现 */
	return this->item_get_double(group_name.c_str(), item_name.c_str(), value, min_value, max_value, def_value, group_is_case_sensitive, item_is_case_sensitive);
}

/***************************************************************************
  函数名称：
  功    能：取某项的内容，返回类型为char * / char []型
  输入参数：const char* const group_name                  ：组名
		   const char* const item_name                   ：项名
		   char *const value                             ：读到的C方式的字符串（返回1时可信，返回0则不可信）
		   const int str_maxlen                          ：指定要读的最大长度（含尾零）
																如果<1则返回空串(不是DEFAULT_CSTRING_VALUE，虽然现在两者相同，但要考虑default值可能会改)
																如果>MAX_STRLEN 则上限为MAX_STRLEN
		   const char* const def_str                     ：读不到情况下的默认值，该参数有默认值DEFAULT_CSTRING_VALUE，分两种情况
																当值是   DEFAULT_CSTRING_VALUE 时，返回0（值不可信）
																当值不是 DEFAULT_CSTRING_VALUE 时，令value=def_value并返回1（注意，不是直接=）
		   const bool group_is_case_sensitive = false : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
		   const bool item_is_case_sensitive = false  : 项名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：
  说    明：1、为简化，未对\"等做转义处理，均按普通字符
		   2、含尾零的最大长度为str_maxlen，调用时要保证有足够空间
		   3、如果 str_maxlen 超过了系统预设的上限 MAX_STRLEN，则按 MAX_STRLEN 取
***************************************************************************/
int config_file_tools::item_get_cstring(const char* const group_name, const char* const item_name, char* const value,
	const int str_maxlen, const char* const def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	string ret = "";
	int temp_max_len = str_maxlen;
	if (str_maxlen > MAX_STRLEN)
		temp_max_len = MAX_STRLEN;
	else if (str_maxlen < 1) 
	{
		value[0] = '\0';//返回空串
		return 0;
	}
	int have_value = item_get_raw(group_name, item_name, ret, group_is_case_sensitive, item_is_case_sensitive);//获取原始值
	if (have_value) 
	{
		size_t ret_len = ret.length();
		char* p = new char[ret_len + 1];//分配空间
		if (p == nullptr) 
		{
			cout << "内存分配失败" << endl;
			return 0;
		}
		istringstream is(ret.c_str());
		is >> p;
		is.clear();
		if (is.fail()) 
		{
			delete[]p;//释放空间
			if (def_value != DEFAULT_CSTRING_VALUE) 
			{
				strcpy(value, def_value);
				return 1;
			}
			else
				return 0;
		}
		else {
			int len = strlen(p);
			if (len >= temp_max_len) 
				len = temp_max_len - 1; // 限制长度
			strncpy(value, p, len);
			value[len] = '\0'; // 确保 value 是以 '\0' 结尾
			delete[]p;//释放空间
			return 1;
		}
	}
	else
	{
		if (def_value != DEFAULT_CSTRING_VALUE) 
		{
			strcpy(value, def_value);
			return 1;
		}
		else
			return 0;
	}
	return 0;
}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：因为工具函数一般在程序初始化阶段被调用，不会在程序执行中被高频次调用，
		   因此这里直接套壳，会略微影响效率，但不影响整体性能（对高频次调用，此方法不适合）
***************************************************************************/
int config_file_tools::item_get_cstring(const string& group_name, const string& item_name, char* const value,
	const int str_maxlen, const char* const def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)

{
	/* 本函数已实现 */
	return item_get_cstring(group_name.c_str(), item_name.c_str(), value, str_maxlen, def_value, group_is_case_sensitive, item_is_case_sensitive);
}

/***************************************************************************
  函数名称：
  功    能：取某项的内容，返回类型为 string 型
  输入参数：const char* const group_name               ：组名
		   const char* const item_name                ：项名
		   string &value                              ：读到的string方式的字符串（返回1时可信，返回0则不可信）
		   const string &def_value                    ：读不到情况下的默认值，该参数有默认值DEFAULT_STRING_VALUE，分两种情况
															当值是   DEFAULT_STRING_VALUE 时，返回0（值不可信）
															当值不是 DEFAULT_STRING_VALUE 时，令value=def_value并返回1
		   const bool group_is_case_sensitive = false : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
		   const bool item_is_case_sensitive = false  : 项名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：
  说    明：为简化，未对\"等做转义处理，均按普通字符
***************************************************************************/
int config_file_tools::item_get_string(const char* const group_name, const char* const item_name, string& value,
	const string& def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	value = def_value;

	int group_index = find_group(all_group, group_name, group_is_case_sensitive);
	if (group_index == -1)  // 未找到组
		return def_value == DEFAULT_STRING_VALUE ? 0 : 1;

	int item_index = find_item(all_item[group_index], item_name, item_is_case_sensitive);
	if (item_index == -1) 
		return 0;

	if (!all_item[group_index][item_index].value.empty())
	{
		value = all_item[group_index][item_index].value;
		return 1;
	}

	return 0;
}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：因为工具函数一般在程序初始化阶段被调用，不会在程序执行中被高频次调用，
		   因此这里直接套壳，会略微影响效率，但不影响整体性能（对高频次调用，此方法不适合）
***************************************************************************/
int config_file_tools::item_get_string(const string& group_name, const string& item_name, string& value,
	const string& def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	/* 本函数已实现 */
	return this->item_get_string(group_name.c_str(), item_name.c_str(), value, def_value, group_is_case_sensitive, item_is_case_sensitive);
}

/***************************************************************************
  函数名称：
  功    能：取某项的内容，返回类型为 IPv4 地址的32bit整型（主机序）
  输入参数：const char* const group_name               ：组名
		   const char* const item_name                ：项名
		   unsigned int &value                        ：读到的IP地址，32位整型方式（返回1时可信，返回0则不可信）
		   const unsigned int &def_value              ：读不到情况下的默认值，该参数有默认值DEFAULT_IPADDR_VALUE，分两种情况
															当值是   DEFAULT_IPADDR_VALUE 时，返回0（值不可信）
															当值不是 DEFAULT_IPADDR_VALUE 时，令value=def_value并返回1
		   const bool group_is_case_sensitive = false : 组名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
		   const bool item_is_case_sensitive = false  : 项名是否大小写敏感，true-大小写敏感 / 默认false-大小写不敏感
  返 回 值：
  说    明：
***************************************************************************/
int config_file_tools::item_get_ipaddr(const char* const group_name, const char* const item_name, unsigned int& value,
	const unsigned int& def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	// 初始化返回值为默认值
	value = def_value;

	// 查找组索引
	int group_index = find_group(all_group, group_name, group_is_case_sensitive);
	if (group_index == -1) 
		// 如果没有找到组，返回0（表示失败）或1（表示使用默认值成功）
		return def_value == DEFAULT_IPADDR_VALUE ? 0 : 1;

	// 查找项索引
	int item_index = find_item(all_item[group_index], item_name, item_is_case_sensitive);
	if (item_index == -1) 
		// 如果没有找到项，返回0（表示失败）或1（表示使用默认值成功）
		return def_value == DEFAULT_IPADDR_VALUE ? 0 : 1;

	// 获取项的值
	const string& item_value = all_item[group_index][item_index].value;
	if (item_value.empty()) 
		// 如果值为空，返回0或1（使用默认值）
		return def_value == DEFAULT_IPADDR_VALUE ? 0 : 1;

	// 解析点分十进制格式的 IP 地址
	unsigned int ip_value = 0;
	vector<string> octets;
	stringstream ss(item_value);
	string octet;
	int part;

	while (getline(ss, octet, '.')) 
	{
		if (octet.empty()) 
			// 处理非法输入，如有多个连续的点
			return def_value == DEFAULT_IPADDR_VALUE ? 0 : 1;

		// 使用 istringstream 进行转换并检查是否成功
		istringstream part_stream(octet);
		part_stream >> part;

		if (part_stream.fail() || part < 0 || part > 255) 
			// 转换失败或数值超出范围
			return def_value == DEFAULT_IPADDR_VALUE ? 0 : 1;

		ip_value = (ip_value << 8) | part;
	}

	// 检查是否解析到四个部分
	if (ss.fail() && !ss.eof()) 
		// 解析失败或没有到达输入末尾
		return def_value == DEFAULT_IPADDR_VALUE ? 0 : 1;

	if (ss.eof() && ip_value < 0x100000000 && item_value.size() != 0) 
	{
		// 如果到达输入末尾并解析到四个部分
		value = ip_value;
		return 1;
	}

	return def_value == DEFAULT_IPADDR_VALUE ? 0 : 1;
}

/***************************************************************************
  函数名称：
  功    能：组名/项目为string方式，其余同上
  输入参数：
  返 回 值：
  说    明：因为工具函数一般在程序初始化阶段被调用，不会在程序执行中被高频次调用，
		   因此这里直接套壳，会略微影响效率，但不影响整体性能（对高频次调用，此方法不适合）
***************************************************************************/
int config_file_tools::item_get_ipaddr(const string& group_name, const string& item_name, unsigned int& value,
	const unsigned int& def_value, const bool group_is_case_sensitive, const bool item_is_case_sensitive)
{
	/* 本函数已实现 */
	return this->item_get_ipaddr(group_name.c_str(), item_name.c_str(), value, def_value, group_is_case_sensitive, item_is_case_sensitive);
}
