from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
import pickle

def train_xgboost(X_train, y_train, X_test, y_test):
    # 初始化XGBoost回归器
    model = XGBRegressor(n_estimators=1000, learning_rate=0.01, max_depth=3, random_state=42)

    # 训练模型
    model.fit(X_train, y_train,
              early_stopping_rounds=10,
              eval_set=[(X_test, y_test)],
              verbose=False)

    # 在测试集上进行预测
    y_pred = model.predict(X_test)

    # 计算并打印MSE作为性能指标
    mse = mean_squared_error(y_test, y_pred)
    print(f"测试集的均方误差(MSE): {mse}")

    import  predict
    predict.predict(model)
    return
    from evalute import evaluate_regression
    metrics = evaluate_regression(y_test, y_pred, X_test.shape[0], X_test.shape[1])

    # 打印评估结果
    for metric_name, metric_value in metrics.items():
        print(f'{metric_name}: {metric_value}')

    with open('instance.pkl', 'wb') as file:
        pickle.dump(model, file)

    return model, y_pred

# 使用前面处理好的数据进行训练
#model, y_pred = train_xgboost(X_train, y_train, X_test, y_test)

# 如果需要，现在可以保存模型，也可以对y_pred进行进一步的分析。