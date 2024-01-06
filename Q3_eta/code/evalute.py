from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np


def evaluate_regression(y_true, y_pred, n=None, p=None):
    """
    对回归模型进行评估，计算并返回多个评估指标。

    :param y_true: 真实值数组
    :param y_pred: 预测值数组
    :param n: 样本数量 (用于调整R平方)
    :param p: 特征数量 (用于调整R平方)
    :return: 包含各评估指标的字典
    """
    # 计算评估指标
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # 计算MAPE
    def mean_absolute_percentage_error(y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        non_zero_indices = y_true != 0
        return np.mean(np.abs((y_true[non_zero_indices] - y_pred[non_zero_indices]) / y_true[non_zero_indices])) * 100

    mape = mean_absolute_percentage_error(y_true, y_pred)

    # 计算调整后的R平方
    adjusted_r2 = None
    if n is not None and p is not None:
        adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

    # 将评估指标打包到字典中
    metrics = {
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2,
        'MAPE': mape,
        'Adjusted R2': adjusted_r2
    }

    return metrics

# 使用例子：
# 假设y_true和y_pred是您的真实标签和预测标签
# y_true = ... (这里应该是您模型的真实标签)
# y_pred = ... (这里应该是您模型的预测结果)
# n = ... # 样本数量
# p = ... # 特征数量

# 调用评估函数
# metrics = evaluate_regression(y_true, y_pred, n, p)

# 打印结果
# for metric_name, metric_value in metrics.items():
#     print(f'{metric_name}: {metric_value}')