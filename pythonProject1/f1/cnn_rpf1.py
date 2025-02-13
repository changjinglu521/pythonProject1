from tensorflow.python.keras.preprocessing.text import Tokenizer
import numpy as np
import pandas as pd
from itertools import chain
import tensorflow as tf
from tensorflow.keras import layers
import matplotlib.pyplot as plt
from tensorflow.python.keras import backend as K

path1 = "/home/xiong/PycharmProjects/pythonProject1/data/train.csv"
path2 = "/home/xiong/PycharmProjects/pythonProject1/data/dev.csv"
path3 = "/home/xiong/PycharmProjects/pythonProject1/data/test.csv"


train_label = pd.read_csv(path1,delimiter='\t',header=0,usecols=[1])
train = pd.read_csv(path1,delimiter='\t',header=0,usecols=[0])
train_array = np.array(train)
label_array = np.array(train_label)
train_list = train_array.tolist()
train_label_list = label_array.tolist()
train_x = list(chain.from_iterable(train_label_list))
train_y = list(chain.from_iterable(train_list))
for i in range(len(train_y)):
    if train_y[i] == -1:
        train_y[i]=0

test_label = pd.read_csv(path2,delimiter='\t',header=0,usecols=[1])
test = pd.read_csv(path2,delimiter='\t',header=0,usecols=[0])
test_array = np.array(test)
test_label_array = np.array(test_label)
test_list = test_array.tolist()
test_label_list = test_label_array.tolist()
test_x = list(chain.from_iterable(test_label_list))
test_y = list(chain.from_iterable(test_list))
for i in range(len(test_y)):
    if test_y[i] == -1:
        test_y[i]=0

t_label = pd.read_csv(path3,delimiter='\t',header=0,usecols=[1])
t_text = pd.read_csv(path3,delimiter='\t',header=0,usecols=[0])
t_text_array = np.array(t_text)
t_label_array = np.array(t_label)
t_text_list = t_text_array.tolist()
t_label_list = t_label_array.tolist()
t_x = list(chain.from_iterable(t_label_list))
t_y = list(chain.from_iterable(t_text_list))
for i in range(len(t_y)):
    if t_y[i] == -1:
        t_y[i]=0


def f1(y_true, y_pred):
    def recall(y_true, y_pred):
        """Recall metric.

        Only computes a batch-wise average of recall.

        Computes the recall, a metric for multi-label classification of
        how many relevant items are selected.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision(y_true, y_pred):
        """Precision metric.

        Only computes a batch-wise average of precision.

        Computes the precision, a metric for multi-label classification of
        how many selected items are relevant.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision
    precision = precision(y_true, y_pred)
    recall = recall(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

tokenizer = Tokenizer(num_words=None)
tokenizer.fit_on_texts(train_x)
train_x = tokenizer.texts_to_sequences(train_x)
tokenizer.fit_on_texts(test_x)
test_x = tokenizer.texts_to_sequences(test_x)
tokenizer.fit_on_texts(t_x)
t_x = tokenizer.texts_to_sequences(t_x)


vocab_size=10000        #词库大小
seq_length=300          #句子最大长度
vocab_dim=100          #词的emedding维度
num_classes=2          #分类类别

train_x = tf.keras.preprocessing.sequence.pad_sequences(train_x, value=0, padding='post',maxlen=seq_length)
test_x = tf.keras.preprocessing.sequence.pad_sequences(test_x,value=0, padding='post', maxlen=seq_length)
t_x = tf.keras.preprocessing.sequence.pad_sequences(t_x,value=0, padding='post', maxlen=seq_length)


model = tf.keras.Sequential()#线性叠加层
model.add(layers.Embedding(vocab_size, vocab_dim))
model.add(layers.Conv1D(filters=256,kernel_size=2,kernel_initializer='he_normal',
                        strides=1,padding='VALID',activation='relu',name='conv'))#一维卷积层
model.add(layers.GlobalMaxPooling1D())#池化层
model.add(layers.Dropout(rate=0.5,name='dropout'))#为了防止过拟合
model.add(layers.Dense(num_classes,activation='softmax'))#全连接网络层
print(model.summary())

model.compile(loss='sparse_categorical_crossentropy',optimizer=tf.keras.optimizers.Adam(),metrics=['acc',f1])
history=model.fit(train_x,train_y,epochs=50,batch_size=64,verbose=1,validation_data=(test_x,test_y))
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.legend(['training', 'valiation'], loc='upper left')
plt.show()


score = model.evaluate(t_x, t_y)
print('Test loss:', score[0])
print('Accuracy:', score[1])
print('f1:', score[2])