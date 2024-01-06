from libcity.config import ConfigParser
from libcity.data import get_dataset
from libcity.utils import get_model, get_executor, get_logger, set_random_seed
import random
import sys
import torch
import json
from tqdm import tqdm



"""
取一个batch的数据进行初步测试
Take the data of a batch for preliminary testing
"""

# 加载配置文件
config = ConfigParser(task='traj_loc_pred', model='DeepMove',
                      dataset='data2023', other_args={'batch_size': 2, 'exp_id': 52259})
exp_id = config.get('exp_id', None)
if exp_id is None:
    exp_id = int(random.SystemRandom().random() * 100000)
    config['exp_id'] = exp_id

print('running test_model.py, exp_id={}'.format(exp_id))

# logger
logger = get_logger(config)
logger.info(config.config)
# seed
seed = config.get('seed', 0)
set_random_seed(seed)
# 加载数据模块
dataset = get_dataset(config)
# 数据预处理，划分数据集
train_data, valid_data, test_data = dataset.get_data()
data_feature = dataset.get_data_feature()


# 抽取一个 batch 的数据进行模型测试
# batch = test_data.__iter__().__next__()
# print(batch['target'])



# 加载模型
model = get_model(config, data_feature)
model = model.to(config['device'])
# 加载执行器
executor = get_executor(config, model, data_feature)
# 模型预测

f = open('/media/space/wrt/LibCity/id2location.json', 'r')
id2location = json.load(f)
f.close()
target2location = {}


for batch in tqdm(test_data):
    batch.to_tensor(config['device'])
    scores = model.predict(batch)
    # print('scores.shape  ', scores.shape)
    max_id = torch.argmax(scores, dim=1)
    # print('max_id:  ', max_id)
    for i in range(len(batch['uid'])):
        uid = int(batch['uid'][i].item())
        traj_id = int(batch['traj_id'][i].item())
        location = id2location[str(max_id[i].item())]
        dict_key = '{}_{}'.format(uid, traj_id)
        target2location[dict_key] = location



print("dict length:   ", len(target2location))
with open('/media/space/wrt/LibCity/target2location_44333.json', 'w') as f:
    json.dump(target2location, f)

