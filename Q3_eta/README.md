# Q3. ETA（车辆行驶时间估计）

车辆行驶时间估计是一个通过分析出发时间、出发地点和目标地点来预测车辆到达目的地所需时间的过程。这涉及交通状况、路线长度、路况、可能的延误（如施工或事故）、天气影响以及司机的驾驶习惯等因素的综合考量。

## 1、所选模型
我们选择xgboost模型对车辆行驶时间进行回归分析，实现方式为在pythin里面调用xgboost的包，以完成对模型的训练和预测。
## 2、运行
#### 2.1 数据预处理
对于课程里面的数据eta_task.csv和traj.csv，分别运行transmit_predict.py和tranmit_train.py进行csv文件数据的提取，以便于对模型的训练。
#### 2.2 模型训练及预测
直接运行main.py函数，将会对模型进行训练，并且用已拥有的数据对模型的效果进行mse评估，同时完成对eta车辆到达时间的预测。

## 3、部署

requirements包含所有需要加载的python包，pip install可以直接安装好所需环境。

```
pip install -r requirements.txt
```
## 4、实验结果
该项目会对eta_task.csv进行预测并进行到达时间的填充，mse的值在正常范围，实验表明xgboost确实能对eta进行一定程度的预测。

最终预测文件：`updated_traj_eta.csv`



## 版本控制

我们使用 [Git](https://github.com/wu-ruitao/Map-Matching) 进行版本控制。有关更多信息，请查看仓库中的提交历史。

## 作者

* **judger2003** - *初始工作* - [judger2003](https://github.com/judger2003)

陈俊杰，吴睿韬，黄汉兴 [contributors](https://github.com/wu-ruitao/Map-Matching).


## 致谢

* 感谢任何对项目有所贡献的人
* 灵感来源：数据挖掘导论
