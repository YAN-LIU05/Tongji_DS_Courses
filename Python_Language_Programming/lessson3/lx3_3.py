import json

def read_json_file(filename):
    # 读取JSON文件并返回解析后的数据
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def search_students_by_keyword(students_data, keyword):
    # 搜索包含关键字的所有学生记录
    results = []
    for student in students_data:
        # 检查关键字是否出现在学生记录的任何字段中
        if keyword in str(student).lower():
            results.append(student)
    return results

# 读取JSON文件
students_data = read_json_file('course.txt')

# 获取用户输入的关键字
keyword_input = input("请输入关键字：")

# 搜索包含关键字的学生记录
matched_students = search_students_by_keyword(students_data, keyword_input)

# 输出结果
if matched_students:
    print('共找到'+str(len(matched_students))+'条数据：')
    for student in matched_students:
        print(student)
else:
    print(f"没找到相关数据")