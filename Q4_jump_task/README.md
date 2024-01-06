

### 第四问：下一跳预测

#### 4.1  数据准备

- 直接运行 `data/processData.py` ，将在 `data/output` 文件夹中生成数据，将这些文件保存至 `LibCity\raw_data\data2023` 文件夹下

#### 4.2  模型训练

- `python run_model.py --task traj_loc_pred --dataset data2023 --model DeepMove`

#### 4.3  模型测试

- `python  test_model.py`

#### 4.4 填充文件

- 运行 `Post-processing/id2string.py` ，生成 `ans.csv` 文件





#### 其他说明

- cut 和 encode 处理后的文件均保存在 `LibCity\libcity\cache\dataset_cache` 文件夹内
- 模型权重保存在 `LibCity\libcity\cache\52259\model_cache` 文件夹内