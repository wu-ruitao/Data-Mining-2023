import pandas as pd
from coordTransform_utils import *
from tqdm import tqdm
import csv
import ast
import json
import math
import numpy as np


def traj_csv_to_js():
    '''
    原始 traj.csv 文件转换为用于绘制地图的 js 文件
    '''
    data = pd.read_csv("./data_raw/traj.csv")
    with open('./data_processed/traj.js', 'w+') as f:
        f.write('var traj = [')
        for c in tqdm(data['coordinates']):
            f.write('{"lnglat":')
            f.write(c)
            f.write(',"style":0} ,')
        f.write(']')


def road_csv_to_js(gcj=True):
    '''
    road.csv 文件转换为用于绘制地图的 js 文件，若 gcj=True 则使用 GCJ 坐标，若 gcj=False 则使用 WGS 坐标
    '''
    if gcj:
        data = pd.read_csv("./data_processed/road_gcj.csv")
        with open('./data_processed/road_gcj.js', 'w+') as f:
            f.write('var road = [')
            for c in tqdm(data['coordinates']):
                f.write(c)
                f.write(', ')
            f.write(']')
    else:
        data = pd.read_csv("./data_raw/road.csv")
        with open('./data_processed/road_wgs.js', 'w+') as f:
            f.write('var road = [')
            for c in tqdm(data['coordinates']):
                f.write(c)
                f.write(', ')
            f.write(']')


def road_csv_wgs2gcj():
    '''
    原始 road.csv 文件坐标系转换，输出为 road_gcj.csv
    '''
    data = pd.read_csv('./data_raw/road.csv')
    for i in tqdm(range(len(data))):
        coord_list = eval(data.loc[i, 'coordinates'])
        res_list = []
        for c in coord_list:
            lng, lat = c
            res_list.append(wgs84_to_gcj02(lng, lat))
        data.loc[i, 'coordinates'] = str(res_list)
    data.to_csv('./data_processed/road_gcj.csv', index=False)


def road_csv_round():
    '''
    road_gcj.csv 中的 GPS 坐标保留 7 位小数，输出为 road_round.csv
    实际实验表明，不需要进行保留，否则匹配结果会出错！
    '''
    data = pd.read_csv('./data_processed/road_gcj.csv')
    for i in tqdm(range(len(data))):
        coord_list = eval(data.loc[i, 'coordinates'])
        res_list = []
        for c in coord_list:
            lng, lat = c
            res_list.append([round(lng, 7), round(lat, 7)])
        data.loc[i, 'coordinates'] = str(res_list)
    data.to_csv('./data_processed/road_round.csv', index=False)


def gen_input_traj_csv():
    with open('./data_raw/traj.csv', 'r') as input_file:
        reader = csv.DictReader(input_file)
        output_data = []
        for row in tqdm(reader):
            id_value = row['traj_id']
            coordinates = ast.literal_eval(row['coordinates'])
            coordinates = [f"{float(coord):f}" for coord in coordinates]
            new_value = f"{id_value};{';'.join(coordinates)}"
            output_data.append(new_value)
    with open('./data_input/traj.csv', 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["id;x;y"])
        for item in output_data:
            writer.writerow([item])


def gen_node_csv():
    # 读取原始csv文件
    df = pd.read_csv('./data_processed/road_gcj_drop_duplicates.csv')

    # 将coordinates列的字符串转化为真正的列表
    df['coordinates'] = df['coordinates'].apply(json.loads)

    # 提取coordinates列表中的所有元素，并创建新的DataFrame
    rows = []
    seen = set()  # 用于存储已经添加过的坐标
    for i, row in df.iterrows():
        for coord in row['coordinates']:
            # 将坐标转换为字符串，然后检查是否已经存在
            coord_str = json.dumps(coord)
            if coord_str not in seen:
                seen.add(coord_str)
                rows.append({'geo_id': len(rows), 'type': 'Point', 'coordinates': coord, 'highway': row['highway']})

    new_df = pd.DataFrame(rows)

    # 将新的DataFrame保存为csv文件
    new_df.to_csv('./data_processed/node.csv', index=False)


def gen_node_json():
    string2Id = {}
    with open('./data_processed/node.csv', 'r') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            if count == 0:
                count = 1
                continue
            string2Id[row[2]] = row[0]

    with open("./data_processed/string2Id.json", "w") as r:
        json.dump(string2Id, r)


def gen_input_edges_csv():
    gen_node_csv()
    gen_node_json()
    with open("./data_processed/string2Id.json", "r") as r:
        string2Id = json.load(r)

    with open("./data_input/edges.csv", "w", newline="") as edge:
        writer = csv.writer(edge)
        header = ["WKT", "_uid_", "id", "source", "target", "cost", "x1", "y1", "x2", "y2"]
        writer.writerow(header)
        with open("./data_processed/road_gcj_drop_duplicates.csv", "r") as f:
            reader = csv.reader(f)
            count = -1
            for row in tqdm(reader):
                if count == -1:
                    count += 1
                    continue

                node_list = row[1][1:-1].split(", [")
                start = node_list[0]
                for end in node_list[1:]:
                    road_id = str(count)
                    end = '[' + end
                    source = string2Id[start]
                    target = string2Id[end]
                    x1, y1 = start[1:-1].split(", ")
                    x2, y2 = end[1:-1].split(", ")
                    WKT = "LINESTRING (" + x1 + " " + y1 + ", " + x2 + " " + y2 + ")"
                    data = [WKT, road_id, road_id, source, target, "1", x1, y1, x2, y2]
                    count += 1
                    writer.writerow(data)
                    start = end


def fmm_draw_traj():
    '''
    将 fmm 输入的 traj.csv 文件转化为用于绘制地图的 traj.js
    '''
    data = pd.read_csv("./data_input/traj.csv", sep=';')
    with open('./map_draw/traj.js', 'w+') as f:
        f.write('var traj = [')
        for row in tqdm(range(len(data))):
            f.write('{"lnglat": ')
            f.write('[' + str(data.iloc[row]['x']) + ', ' + str(data.iloc[row]['y']) + ']')
            if row == 0 or row == len(data) - 1 or data.iloc[row]['id'] != data.iloc[
                    row - 1]['id'] or data.iloc[row]['id'] != data.iloc[row + 1]['id']:
                f.write(',"style":0, ')
            else:
                f.write(',"style":1, ')
            f.write('"name": "' + str(int(data.iloc[row]['id'])) + '"')
            f.write('} ,')
        f.write(']')


def fmm_draw_path(trans=False):
    '''
    绘制 fmm 输出的 mr.csv 文件中的 cpath
    trans: 若为 True 则执行 wgs84_to_gcj02
    '''
    mr = pd.read_csv('./data_output/mr.csv', sep=';')
    road = pd.read_csv('./data_input/edges.csv')
    with open('./map_draw/path.js', 'w') as f:
        f.write('var path = [')
        for mr_row in tqdm(mr['cpath']):
            # f.write('[')    # 每条完整路径的开始
            try:
                cpath = list(eval(mr_row))
            except TypeError as e:
                # 若 mr_row 为 int，说明该路径只有一段路；若 mr_row 为 nan，说明该路径没有匹配的路
                if mr_row != mr_row:  # nan
                    continue
                else:
                    cpath = [eval(mr_row)]
            for id in cpath:
                f.write('[')
                if trans:
                    f.write(str(wgs84_to_gcj02(road.iloc[int(id)]['x1'], road.iloc[int(id)]['y1'])) + ', ')
                    f.write(str(wgs84_to_gcj02(road.iloc[int(id)]['x2'], road.iloc[int(id)]['y2'])))
                else:
                    f.write('[' + str(road.iloc[int(id)]['x1']) + ',' + str(road.iloc[int(id)]['y1']) + '], ')
                    f.write('[' + str(road.iloc[int(id)]['x2']) + ',' + str(road.iloc[int(id)]['y2']) + ']')
                f.write('], ')
            # f.write('], ')
        f.write(']')  # 每条完整路径的结束


def road_csv_drop_duplicates():
    '''
    删除 edges.csv 中坐标相同但其他属性不同的路
    '''
    # 读取CSV文件
    file_path = './data_processed/road_gcj.csv'
    df = pd.read_csv(file_path)
    # 按照'length'升序排列
    # df.sort_values(by='length', inplace=True)
    # 根据'length'和'coordinates'列删除重复行，只保留第一次出现的行
    df.drop_duplicates(subset=['length', 'coordinates'], keep='first', inplace=True)
    # 将结果保存到新的CSV文件
    output_file_path = './data_processed/road_gcj_drop_duplicates.csv'
    df.to_csv(output_file_path, index=False)


def calculate_cost():
    '''
    计算 edges.csv 中 cost 列的值，目前认为 cost=路段起始点之间的大圆距离（单位：米）
    '''

    def haversine(lat1, lon1, lat2, lon2):
        # 将经纬度转换为弧度
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        # 计算差值
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        # Haversine公式计算距离
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # 地球半径（单位：千米）
        radius = 6371000.0
        # 计算距离
        distance = radius * c
        return distance

    # 读取CSV文件
    df = pd.read_csv('./data_input/edges.csv')
    # 遍历每一行，计算距离并写入 'cost' 列
    for index, row in df.iterrows():
        distance = haversine(row['y1'], row['x1'], row['y2'], row['x2'])
        df.at[index, 'cost'] = distance
    # 将结果写回CSV文件
    df.to_csv('./data_input/edges.csv', index=False)


if __name__ == '__main__':

    # gen_input_traj_csv()
    # gen_input_edges_csv()
    fmm_draw_traj()
    # fmm_draw_path(False)
    # road_csv_drop_duplicates()

    # calculate_cost()
    # road_csv_to_js(gcj=False)
