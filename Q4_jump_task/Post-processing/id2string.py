import pandas as pd
import json

geo = pd.read_csv('./data2023.geo')

entity_ids = []
traj_ids = []
ans = []

with open('target2location.json') as f:
    traget2location = json.load(f)

    for key in traget2location:
        entity_id, traj_id = key.split("_")
        traj_id = int(traj_id) - 30000
        res_id = int(traget2location[key])
        res = geo.loc[res_id + 1]['coordinates']
        entity_ids.append(entity_id)
        traj_ids.append(traj_id)
        ans.append(res)
    data = pd.DataFrame({'entity_id': entity_ids, 'traj_id': traj_ids, 'res': ans})
    data.to_csv("ans_only.csv", index=False)

    jump_task = pd.read_csv('./jump_task.csv')

    ans = jump_task.drop('coordinates', axis=1)

    prev_traj_id = -1
    prev_entity_id = -1
    # prev_row = ""
    # prev_index = -1
    cur_traj_id = -1
    cur_entity_id = -1

    coordinates = []
    coordinate = ""
    for index, row in jump_task.iterrows():
        cur_entity_id = row[2]
        cur_traj_id = row[3]
        # coordinates.append(row[4])

        if index == 0:
            pass
        elif cur_traj_id != prev_traj_id:
            key = str(prev_entity_id) + "_" + str(prev_traj_id + 30000)
            res_id = int(traget2location[key])
            # prev_row[4] = geo.loc[res_id + 1]['coordinates']
            # ans.insert_col(prev_index, 4, geo.loc[res_id + 1]['coordinates'])
            # coordinate = geo.loc[res_id + 1]['coordinates']
            coordinates[-1] = geo.loc[res_id + 1]['coordinates']

        coordinates.append(row[4])
        # prev_row = row
        # prev_index = index
        prev_entity_id = cur_entity_id
        prev_traj_id = cur_traj_id
        # coordinates.append(coordinate)

    # 最后一行
    key = str(prev_entity_id) + "_" + str(prev_traj_id + 30000)
    res_id = int(traget2location[key])
    # prev_row[4] = geo.loc[res_id + 1]['coordinates']
    # ans.insert_col(prev_index, 4, geo.loc[res_id + 1]['coordinates'])
    # coordinate = geo.loc[res_id + 1]['coordinates']
    # coordinates.append(coordinate)
    coordinates[-1] = geo.loc[res_id + 1]['coordinates']
    # print(len(coordinates))
    ans['coordinates'] = coordinates
    ans = ans.reindex(
        columns=['id', 'time', 'entity_id', 'traj_id', 'coordinates', 'current_dis', 'speeds', 'holidays'])

    ans.to_csv('./ans.csv', index=False)