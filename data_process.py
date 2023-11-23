import pandas as pd
from coordTransform_utils import *
from tqdm import tqdm
import csv
import ast


def traj_csv_to_js():
    '''
    原始 traj.csv 文件转换为用于绘制地图的 js 文件
    '''
    data = pd.read_csv("./data_raw/traj.csv")
    with open('./data_processd/traj.js','w+') as f:
        f.write('var traj = [')
        for c in tqdm(data['coordinates']):
            f.write('{"lnglat":')
            f.write(c)
            f.write(',"style":0} ,')
        f.write(']')


def road_csv_to_js():
    '''
    原始 road.csv 文件转换为用于绘制地图的 js 文件
    '''
    data = pd.read_csv("./data_raw/road.csv")
    with open('./data_processd/road.js','w+') as f:
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
        coord_list = eval(data.loc[i,'coordinates'])
        res_list = []
        for c in coord_list:
            lng, lat = c
            res_list.append(wgs84_to_gcj02(lng, lat))
        data.loc[i,'coordinates'] = str(res_list)
    data.to_csv('./data_processd/road_gcj.csv', index=False)


def road_csv_round():
    '''
    road_gcj.csv 中的 GPS 坐标保留 7 位小数，输出为 road_round.csv
    '''
    data = pd.read_csv('./data_processd/road_gcj.csv')
    for i in tqdm(range(len(data))):
        coord_list = eval(data.loc[i,'coordinates'])
        res_list = []
        for c in coord_list:
            lng, lat = c
            res_list.append([round(lng,7), round(lat,7)])
        data.loc[i,'coordinates'] = str(res_list)
    data.to_csv('./data_processd/road_round.csv', index=False)


def gen_input_traj_csv():
    with open('./data_raw/traj.csv', 'r') as input_file:
        reader = csv.DictReader(input_file)
        output_data = []
        for row in reader:
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
    import pandas as pd
    import json
    # 读取原始csv文件
    df = pd.read_csv('./data_raw/road.csv')

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
                rows.append({
                    'geo_id': len(rows),
                    'type': 'Point',
                    'coordinates': coord,
                    'highway': row['highway']
                })

    new_df = pd.DataFrame(rows)

    # 将新的DataFrame保存为csv文件
    new_df.to_csv('./data_processd/node.csv', index=False)



def gen_node_json():
    string2Id = {}
    with open('./data_processd/node.csv', 'r') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            if count == 0:
                count = 1
                continue
            string2Id[row[2]] = row[0]
    
    with open("./data_processd/string2Id.json", "w") as r:
        json.dump(string2Id, r)




def gen_input_edges_csv():
    gen_node_csv()
    gen_node_json()
    with open("./data_processd/string2Id.json", "r") as r:
        string2Id = json.load(r)

    with open("./data_input/edges.csv", "w", newline="") as edge:
        writer = csv.writer(edge)
        header = ["WKT", "_uid_", "id", "source", "target", "cost", "x1", "y1", "x2", "y2"]
        writer.writerow(header)
        with open("road.csv", "r") as f:
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
                    print(data)
                    writer.writerow(data)
                    start = end



def fmm_draw_traj():
    '''
    将 fmm 输入的 traj.csv 文件转化为用于绘制地图的 traj.js
    '''
    data = pd.read_csv("./data_input/traj.csv", sep=';')
    with open('./map_draw/traj.js','w+') as f:
        f.write('var traj = [')
        for row in tqdm(range(len(data))):
            f.write('{"lnglat": ')
            f.write('[' + str(data.iloc[row]['x']) + ', ' + str(data.iloc[row]['y']) + ']')
            if row == 0 or row == len(data)-1 or data.iloc[row]['id'] != data.iloc[row-1]['id'] or data.iloc[row]['id'] != data.iloc[row+1]['id']:
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
    with open('./map_draw/path.js','w') as f:
        f.write('var path = [')
        for mr_row in tqdm(mr['cpath']):
            # f.write('[')    # 每条完整路径的开始
            cpath = list(eval(mr_row))
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
        f.write(']')        # 每条完整路径的结束


def road_csv_drop_duplicates():
    '''
    删除 edges.csv 中坐标相同但其他属性不同的路
    '''
    # 读取CSV文件
    file_path = './data_processd/road_round.csv'  # 请替换成你的文件路径
    df = pd.read_csv(file_path)
    # 按照'length'升序排列
    df.sort_values(by='length', inplace=True)
    # 根据'length'和'coordinates'列删除重复行，只保留第一次出现的行
    df.drop_duplicates(subset=['length', 'coordinates'], keep='first', inplace=True)
    # 将结果保存到新的CSV文件
    output_file_path = './data_processd/road_round_drop_duplicates.csv'  # 请替换成你想要保存的文件路径
    df.to_csv(output_file_path, index=False)



if __name__ == '__main__':

    # traj_csv_to_js()
    # road_csv_to_js()
    # road_csv_wgs2gcj()
    # road_csv_round()

    # gen_input_traj_csv()
    # gen_input_edges_csv()

    # gen_node_csv()
    fmm_draw_path(True)