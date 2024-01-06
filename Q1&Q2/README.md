

### Q1 & Q2 数据组织格式

【文件夹】

- `data_input`    `fmm` 的输入数据
- `data_output`  `fmm` 的输出数据
- `data_raw`             未处理的原始数据
- `data_processed` 经过预处理的数据 
- `data_cluster`   第二问（轨迹聚类）数据
- `map_draw`            地图绘制文件

【文件】

- `map_matching.py`  用于第一问（轨迹匹配）处理数据
- `coordTransform_utils` 坐标系转化源代码，可直接 `import` 使用
- `cluster.py`          用于第二问（轨迹聚类）



### 第一问：轨迹匹配

#### 1.1  数据准备及算法运行

- 使用 `map_matching.py` 进行数据预处理，根据 fmm 算法的要求将输入文件保存至 `data_input` 文件夹中

- 在 **WSL2** 环境下安装 fmm 算法所需环境
- 编写 `convert.vrt` 文件
- 运行 `ogr2ogr -f "ESRI Shapefile" edges.shp convert.vrt` 生成 `.shp` 文件
- 运行 `ubodt_gen --network ./edges.shp --output ./ubodt.txt --delta 0.05 --use_omp` 生成 `ubodt` 文件
- 运行 `fmm --ubodt ./ubodt.txt --network ./edges.shp --gps ./traj.csv --gps_point -k 8 -r 3000 -e 50 --output mr.txt --use_omp --output_fields cpath` 进行轨迹匹配
- `data_output` 中的 `mr.csv` 为最终的匹配结果

#### 1.2  实验结果分析

- 使用 `map_matching.py` 中的相关函数（`fmm_draw_traj`、`fmm_draw_path`）对数据结果进行可视化分析

#### 1.3  地图可视化

- `map_draw` 文件夹内的 `map2023.html` 可直接点击打开
- `traj.js` 为轨迹数据、`path.js` 为轨迹匹配的道路数据，`road.js` 为道路数据
- 通过`map_matching.py` 中的相关函数可生成对应的 `.js` 文件



### 第二问：轨迹聚类

- 依次运行 `cluster.py`   中的四个函数即可完成轨迹聚类即结果可视化

