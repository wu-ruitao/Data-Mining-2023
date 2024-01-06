import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
# 设定显示的最大行数，例如设置为None以显示所有行
pd.set_option('display.max_rows', None)

# 设定显示的最大列数，例如设置为None以显示所有列
pd.set_option('display.max_columns', None)

# 设定显示的宽度，以便显示每行的全部数据
pd.set_option('display.width', None)

# 设定最大列宽，以便显示每个列的全部数据，例如设置为100
pd.set_option('display.max_colwidth', 100)
# 加载数据
data = pd.read_csv('traj_to_train.csv')

# 将时间戳转换为pandas中的datetime对象
data['time'] = pd.to_datetime(data['time'])

# 从时间戳中提取特征
#print(data['time'])
data['hour'] = data['time'].dt.hour
#print(data['hour'])
data['day_of_week'] = data['time'].dt.dayofweek
data['is_weekend'] = data['day_of_week'].isin([5,6]).astype(int)

#print(data['day_of_week'])
#print(data['is_weekend'])
# 对节假日的列进行编码
label_encoder = LabelEncoder()
data['holidays'] = label_encoder.fit_transform(data['holidays'])
# 先将coordinates列的前后方括号去除
data['coordinates'] = data['coordinates'].str.strip('[]')

# 然后再分割为两个独立的列：latitude 和 longitude
coordinates_split = data['coordinates'].str.split(',', expand=True)
data['latitude'] = pd.to_numeric(coordinates_split[0].str.strip())
data['longitude'] = pd.to_numeric(coordinates_split[1].str.strip())
data.drop('coordinates', axis=1, inplace=True)
datanew = {}



# 假设我们的目标变量（标签）是 'current_distance'，则需要将其从数据集中移除
labels = data['duration_minutes']
features = data.drop(['id', 'traj_id', 'time', 'entity_id', 'duration_minutes','coordinates_last',
                                                                                                  'latitude', 'longitude',
                      ], axis=1)

# 分割数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
print(X_train.shape)  # 这应该输出类似于 (n_samples, n_features) 的结果
print(y_train.shape)  # 这应该输出 (n_samples,) 确认它是一个1D数组
from train import train_xgboost
train_xgboost(X_train, y_train, X_test, y_test)