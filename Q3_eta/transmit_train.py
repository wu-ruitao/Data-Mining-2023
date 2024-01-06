import pandas as pd

# 读取CSV文件
df = pd.read_csv('traj.csv', parse_dates=['time'])
print(type(df['coordinates'][0]))
# 按照'traj_id'和'time'排序
df_sorted = df.sort_values(by=['traj_id', 'time'])

# 使用 transform 方法获得每个 traj_id 的最早和最晚时间
df_sorted['min_time'] = df_sorted.groupby('traj_id')['time'].transform('min')
df_sorted['max_time'] = df_sorted.groupby('traj_id')['time'].transform('max')

# 计算每个 traj_id 的持续时间（以分钟为单位）
df_sorted['duration_minutes'] = (df_sorted['max_time'] - df_sorted['min_time']).dt.total_seconds() / 60

# 去除重复的 traj_id 条目，只保留第一条记录
traj_duration = df_sorted.drop_duplicates(subset='traj_id')

# 现在 traj_duration 包含每个 traj_id 的第一条记录以及相应的持续时间
# 可以选择删除 min_time 和 max_time 列，如果它们不再需要的话
traj_duration = traj_duration.drop(['min_time', 'max_time'], axis=1)

# 获取每个 traj_id 最晚时间的索引
idx = df_sorted.groupby('traj_id')['time'].idxmin()

# 利用上面找到的索引获取最晚时间的current_dis和coordinates值
df_latest = df_sorted.loc[idx, ['traj_id', 'current_dis', 'coordinates']]
df_latest['coordinates_last'] = df_latest['coordinates']
#df_latest.drop('coordinates', axis=1)
# 将df_latest的索引设置为traj_id，以便能够按traj_id对齐并更新traj_duration
df_latest.set_index('traj_id', inplace=True)

# 更新traj_duration的current_dis和coordinates列
traj_duration.set_index('traj_id', inplace=True)
traj_duration['current_dis'] = df_latest['current_dis']
traj_duration['coordinates_last'] = df_latest['coordinates_last']
# 重置索引以便保存到CSV
traj_duration.reset_index(inplace=True)
import pandas as pd
#print(type(eval(traj_duration['coordinates'][0])))
# 假设df是你的dataframe，并且coordinates列是字符串形式的 '[x, y]'
# 首先，确保coordinates是字符串类型
traj_duration['coordinates'] = traj_duration['coordinates'].astype(str)

# 使用str.strip去掉两边的括号，然后使用str.split分割字符串
traj_duration[['x_first', 'y_first']] = traj_duration['coordinates'].str.strip('[]').str.split(',', expand=True)

# 将分割后的字符串转换为数值类型(float或int根据你的数据而定)
traj_duration['x_first'] = traj_duration['x_first'].astype(float)
traj_duration['y_first'] = traj_duration['y_first'].astype(float)

# 现在df中有两个新列x和y，分别对应coordinates中的值

traj_duration['coordinates_last'] = traj_duration['coordinates_last'].astype(str)

# 使用str.strip去掉两边的括号，然后使用str.split分割字符串
traj_duration[['x_last', 'y_last']] = traj_duration['coordinates_last'].str.strip('[]').str.split(',', expand=True)

# 将分割后的字符串转换为数值类型(float或int根据你的数据而定)
traj_duration['x_last'] = traj_duration['x_last'].astype(float)
traj_duration['y_last'] = traj_duration['y_last'].astype(float)

# 保存到新的CSV文件
traj_duration.to_csv('traj_to_train.csv', index=False)