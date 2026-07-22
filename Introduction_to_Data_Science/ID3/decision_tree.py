import math
import pandas as pd
from collections import Counter


class DecisionTreeID3:
    def __init__(self):
        self.tree = None  # 存储生成的决策树

    def fit(self, data, features, target, max_depth=None, current_depth=0, min_samples_split=2, min_gain=0.01):
        self.tree = self.build_tree(data, features, target, max_depth, current_depth, min_samples_split, min_gain)

    def build_tree(self, data, features, target, max_depth, current_depth, min_samples_split, min_gain):
        # 终止条件
        if len(set(row[target] for row in data)) == 1:
            return data[0][target]
        if not features or (max_depth is not None and current_depth >= max_depth):
            return Counter(row[target] for row in data).most_common(1)[0][0]

        # 如果样本数少于最小分裂数，停止分裂
        if len(data) < min_samples_split:
            return Counter(row[target] for row in data).most_common(1)[0][0]

        # 选择最佳特征
        best_feature = self.select_best_feature(data, features, target)
        best_gain = self.calculate_info_gain(data, best_feature, target)

        # 如果信息增益小于阈值，停止分裂
        if best_gain < min_gain:
            return Counter(row[target] for row in data).most_common(1)[0][0]

        # 构建子树
        tree = {best_feature: {}}
        feature_values = set(row[best_feature] for row in data)

        for value in feature_values:
            subset = [row for row in data if row[best_feature] == value]
            subtree = self.build_tree(subset, [f for f in features if f != best_feature], target, max_depth, current_depth + 1, min_samples_split, min_gain)
            tree[best_feature][value] = subtree

        return tree

    def select_best_feature(self, data, features, target):
        base_entropy = self._entropy([row[target] for row in data])
        best_gain = 0
        best_feature = None

        for feature in features:
            info_gain = self.calculate_info_gain(data, feature, target)
            if info_gain > best_gain:
                best_gain = info_gain
                best_feature = feature

        return best_feature

    def calculate_info_gain(self, data, feature, target):
        base_entropy = self._entropy([row[target] for row in data])
        feature_values = [row[feature] for row in data]
        subsets = {value: [row[target] for row in data if row[feature] == value] for value in set(feature_values)}
        new_entropy = sum((len(subset) / len(data)) * self._entropy(subset) for subset in subsets.values())
        return base_entropy - new_entropy

    @staticmethod
    def _entropy(values):
        counts = Counter(values)
        total = len(values)
        return -sum((count / total) * math.log2(count / total) for count in counts.values() if count > 0)

    def predict(self, sample):
        return self._classify(sample, self.tree)

    def _classify(self, sample, tree):
        if not isinstance(tree, dict):
            return tree

        feature, branches = next(iter(tree.items()))
        feature_value = sample.get(feature)

        if feature_value not in branches:
            return None

        return self._classify(sample, branches[feature_value])

    def post_prune(self, tree, data, target):
        def prune(subtree, subset):
            if not isinstance(subtree, dict):
                return subtree

            feature = next(iter(subtree))
            branches = subtree[feature]

            for value, branch in branches.items():
                branch_data = [row for row in subset if row[feature] == value]
                branches[value] = prune(branch, branch_data)

            combined_label = Counter(row[target] for row in subset).most_common(1)[0][0]
            if all(not isinstance(branch, dict) for branch in branches.values()):
                leaf_predictions = [branches[row[feature]] for row in subset if row[feature] in branches]
                error_before = sum(1 for pred, actual in zip(leaf_predictions, [row[target] for row in subset]) if pred != actual)
                error_after = sum(1 for actual in [row[target] for row in subset] if actual != combined_label)

                if error_after <= error_before:
                    return combined_label

            return subtree

        return prune(tree, data)


# 从 Excel 文件中读取数据
def load_data_from_excel(file_path):
    data = pd.read_excel(file_path, engine='openpyxl').to_dict(orient='records')
    return data


# 打印决策树结构
def print_tree(tree, indent=""):
    if not isinstance(tree, dict):
        print(indent + "Leaf:", tree)
        return

    for feature, branches in tree.items():
        print(indent + f"Feature: {feature}")
        for value, subtree in branches.items():
            print(indent + f"  {value} ->")
            print_tree(subtree, indent + "    ")


def predict_with_names(tree, sample):
    name = sample.get('Name')  # 获取名字
    prediction = tree.predict(sample)  # 使用决策树预测结果
    print(f"{name} 的预测结果 : {prediction}")
    return prediction

if __name__ == "__main__":
    # 加载训练和验证数据
    training_data = load_data_from_excel('data.xlsx')
    validation_data = load_data_from_excel('validation_data.xlsx')
    sample_data = load_data_from_excel('samples.xlsx')

    # 定义特征和目标
    features = ['Age', 'Study Time', 'Attendance', 'Participation', 'Homework Hours', 'Previous Grades']
    target = 'Pass'

    # 创建并拟合决策树
    tree = DecisionTreeID3()
    tree.fit(training_data, features, target, min_samples_split=1, min_gain=0.05)

    # 打印生成的决策树结构
    print("生成的决策树结构:")
    print_tree(tree.tree)

    # 后剪枝
    tree.tree = tree.post_prune(tree.tree, validation_data, target)

    # 打印剪枝后的决策树结构
    print("\n剪枝后的决策树结构:")
    print_tree(tree.tree)


    print("\n样本数据预测结果:")
    # 对样本数据进行预测并打印结果
    for sample in sample_data:
        predict_with_names(tree, sample)
