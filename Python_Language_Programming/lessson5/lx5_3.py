import os
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras import Sequential

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 只是防止告警 'I tensorflow/core/platform/cpu_feature_guard.cc:140] Your CPU supports instructions that this'，没有真正解决这个问题

def load_data():
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    size = 10000  # 定义size变量
    x_train = x_train[0:size]  # 截取10000个样本
    y_train = y_train[0:size]  # 截取10000个样本
    x_train = x_train.reshape(size, 28 * 28)  # x_train本来是10000x28x28的数组，把它转换成10000x784的二维数组
    x_test = x_test.reshape(x_test.shape[0], 28 * 28)  # 和上面是同一个意思
    x_train = x_train.astype('float32')  # 将它的元素类型转换为float32,之前为uint8
    x_test = x_test.astype('float32')
    # y_train之前可以理解为10000x1的数组，每个单元素数组的值就是样本所表示的数字
    y_train = tf.keras.utils.to_categorical(y_train, 10)  # 把它转换成了10000x10的数组
    y_test = tf.keras.utils.to_categorical(y_test, 10)
    x_train = x_train / 255  # x_train之前的灰度值最大为255，最小为0，这里将它们进行特征归一化，变成了在0到1之间的小数
    x_test = x_test / 255
    return (x_train, y_train), (x_test, y_test)

def run():
    # 加载数据
    (x_train, y_train), (x_test, y_test) = load_data()
    # 定义模型
    model = Sequential()
    # 定义输入层，输入维度是784，神经元数量可以根据需要调整
    model.add(Dense(128, activation='relu', input_dim=784))
    # 定义隐藏层
    for i in range(2):
        model.add(Dense(128, activation='relu'))
    # 定义输出层，10个神经元对应10个类别，使用softmax激活函数
    model.add(Dense(10, activation='softmax'))

    # 编译模型
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    # 训练模型
    model.fit(x_train, y_train, batch_size=100, epochs=20, validation_split=0.1)

    # 评估模型
    train_eval = model.evaluate(x_train, y_train, batch_size=100)
    print('\nTrain Acc: %.2f%%' % (train_eval[1] * 100))
    test_eval = model.evaluate(x_test, y_test, batch_size=100)
    print('\nTest Acc: %.2f%%' % (test_eval[1] * 100))

if __name__ == '__main__':
    run()
