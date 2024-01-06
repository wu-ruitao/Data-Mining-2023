import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import hdbscan
import traj_dist.distance as tdist

plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决汉字显示为□指定默认字体为黑体。
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时 负号'-' 显示为□和报错的问题。
np.set_printoptions(threshold=np.inf)  # 避免打印 np.array 时出现省略号


def gen_data():
    '''
    使用原始的 traj.csv 生成 tdist 库可以直接使用的数据格式 traj.npz
    '''
    df = pd.read_csv('./data_raw/traj.csv')
    traj_list = {}
    group_df = df.groupby(by='traj_id')
    for group in tqdm(list(group_df)):
        index, row = group[0], group[1]
        res = list(map(eval, list(row['coordinates'])))
        traj_list[f'traj_{index}'] = np.array(res)
    np.savez("./data_cluster/traj.npz", **traj_list)


def calculate_and_save_dist():
    '''
    使用 tdist 库计算轨迹之间的距离并保存为 cdist.npy，这是一个对称矩阵
    '''
    npzfile = np.load("./data_cluster/traj.npz")
    traj_list = []
    for key in tqdm(npzfile):
        traj_list.append(npzfile[key])
    print(len(traj_list))

    # # Pairwise distance
    # pdist = tdist.pdist(traj_list, metric="sspd")
    # print(pdist)

    # Distance between two list of trajectories
    cdist = tdist.cdist(traj_list, traj_list, metric="sspd")
    print(type(cdist))
    np.save('./data_cluster/cdist.npy', cdist, allow_pickle=True)


def clust():
    '''
    使用 hdbscan 聚类算法进行聚类，保存聚类结果（标签）
    '''
    dist_matrix = np.load('./data_cluster/cdist.npy')
    clusterer = hdbscan.HDBSCAN(metric='precomputed', min_cluster_size=10, min_samples=1)
    clusterer.fit_predict(dist_matrix)
    print(clusterer.labels_.max())  # 输出最大聚类标签
    np.save('./data_cluster/clusterer.npy', clusterer.labels_, allow_pickle=True)


def draw():
    '''
    根据聚类结果（标签）绘制聚类类别频数统计图
    '''
    clusterer_labels = np.load('./data_cluster/clusterer.npy')
    filtered_array = clusterer_labels[clusterer_labels != -1]
    values, counts = np.unique(filtered_array, return_counts=True)
    plt.figure(figsize=(10, 6))
    plt.bar(values, counts, color='skyblue')
    plt.xlabel('类别')
    plt.ylabel('频数')
    plt.title('聚类类别频数')
    plt.grid()
    # plt.xticks(values, rotation=45)
    plt.xticks([])
    plt.savefig('./data_cluster/label_result.png', dpi=200)
    plt.show()


if __name__ == '__main__':
    # gen_data()
    # calculate_and_save_dist()
    # clust()
    draw()
