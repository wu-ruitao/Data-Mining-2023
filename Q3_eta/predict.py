import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
def predict(model):
    # 设定显示的最大行数，例如设置为None以显示所有行
    pd.set_option('display.max_rows', None)

    # 设定显示的最大列数，例如设置为None以显示所有列
    pd.set_option('display.max_columns', None)

    # 设定显示的宽度，以便显示每行的全部数据
    pd.set_option('display.width', None)

    # 设定最大列宽，以便显示每个列的全部数据，例如设置为100
    pd.set_option('display.max_colwidth', 100)
    # 加载数据
    data = pd.read_csv('traj_to_predict.csv')

    # 将时间戳转换为pandas中的datetime对象
    data['time'] = pd.to_datetime(data['time'])

    # 从时间戳中提取特征
    #print(data['time'])
    data['hour'] = data['time'].dt.hour
   # print(data['hour'])
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
    #fea =data.drop([ 'id', 'time', 'entity_id','coordinates_last',
    #                                'speeds','current_dis', 'holidays', 'hour', 'day_of_week', 'is_weekend', 'latitude', 'longitude'], axis=1)
    a = data['traj_id']
    features = data.drop(['id', 'traj_id', 'time', 'entity_id','coordinates_last','latitude', 'longitude'
                          ], axis=1)
    # 使用模型进行预测
    # 使用模型进行预测
    predictions = model.predict(features)
    features['traj_id'] = a
    # 输出预测结果
    print(predictions)
    # 如果你需要将预测结果作为一个列添加到new_data DataFrame中
    features['predicted_value'] = predictions
    # 读取 traj_eta.csv 文件
    traj_eta_df = pd.read_csv('eta_task.csv')

    # 确保 'time' 列是 datetime 类型
    traj_eta_df['time'] = pd.to_datetime(traj_eta_df['time'])

    # 假设 'features' DataFrame 已经存在并且包含 'traj_id' 和 'predicted_value' 列
    # 确保 'features' 按 'traj_id' 排序
    features.sort_values(by=['traj_id'], inplace=True)

    # 确保 'traj_eta_df' 按 'traj_id' 和 'time' 排序
    traj_eta_df.sort_values(by=['traj_id', 'time'], inplace=True)

    # 为每个 'traj_id' 分组的第一项的时间加上 'predicted_value' 分钟数
    # 假设 'features' DataFrame 中每个 'traj_id' 只有一个 'predicted_value'
    # 我们将使用 map 函数将 'predicted_value' 从 'features' 映射到 'traj_eta_df'

    # 创建一个以 'traj_id' 为键，以 'predicted_value' 为值的字典
    predicted_values_dict = pd.Series(features.predicted_value.values, index=features.traj_id).to_dict()

    # 为 'traj_eta_df' 创建一个 'predicted_value' 列，根据 'traj_id' 来映射值
    traj_eta_df['predicted_value'] = traj_eta_df['traj_id'].map(predicted_values_dict)

    # 计算新的时间戳，只针对每个 'traj_id' 组的第二项
    # 假设每个 'traj_id' 至少有两项
    first_times = traj_eta_df.groupby('traj_id')['time'].transform('first')
    first_predicted_values = traj_eta_df.groupby('traj_id')['predicted_value'].transform('first')
    traj_eta_df['new_time'] = first_times + pd.to_timedelta(first_predicted_values, unit='min')

    # 更新第二项的时间
    # 我们可以使用 cumcount 为每个分组内的行计数
    traj_eta_df['row_number'] = traj_eta_df.groupby('traj_id').cumcount() + 1

    # 只更新分组内的第二项
    traj_eta_df.loc[traj_eta_df['row_number'] == 2, 'time'] = traj_eta_df.loc[
        traj_eta_df['row_number'] == 2, 'new_time']

    # 如果你不需要 'predicted_value', 'new_time' 和 'row_number' 列，可以在此删除
    traj_eta_df.drop(['predicted_value', 'new_time', 'row_number'], axis=1, inplace=True)

    # 将更新后的 DataFrame 保存回文件
    traj_eta_df.to_csv('updated_traj_eta.csv', index=False)
    features.to_csv('predictions.csv', index=False)
