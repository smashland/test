import os
import ast
import pickle
import numpy as np
import pandas as pd
import logging
import sklearn
from typing import Final, Optional, List, Dict, Callable, Tuple, Union, Any, Sequence, cast, TYPE_CHECKING

# 常量定义
SECONDS_PER_MINUTE = 60
TWO_MINUTES = 2 * SECONDS_PER_MINUTE
THREE_MINUTES = 3 * SECONDS_PER_MINUTE
FIVE_MINUTES = 5 * SECONDS_PER_MINUTE
ROR_PERIOD = 15  # 升温速率计算周期（秒）

_log: Final[logging.Logger] = logging.getLogger(__name__)
def calculate_roast_features(timex, beantemp):
    """从时间和温度数据计算预测特征。
    
    参数:
        timex (list): 时间点
        beantemp (list): 豆温度读数
        
    返回:
        dict: 用于预测的特征，如果出错则返回None
    """
    _log.exception(f"测试: {timex}{beantemp}")
    try:
        # 转换为numpy数组并确保为浮点类型
        timex = np.array(timex, dtype=float)
        beantemp = np.array(beantemp, dtype=float)
        
        # 过滤掉负时间点
        valid_indices = timex >= 0
        timex = timex[valid_indices]
        beantemp = beantemp[valid_indices]
        
        if len(timex) == 0 or len(beantemp) == 0:
            print("过滤后没有有效的时间/温度数据点")
            _log.exception(f"过滤后没有有效的时间/温度数据点")
            return None
        
        # 创建插值温度曲线
        curve = pd.DataFrame({'time': timex, 'bean_temp': beantemp}).astype(float)
        
        min_time, max_time = curve['time'].min(), curve['time'].max()
        # 创建稀疏时间序列以减少内存使用
        sample_rate = max(1, int((max_time - min_time) / 300))
        all_times = pd.Series(np.arange(min_time, max_time + 1, sample_rate), name='time')
        curve = pd.merge(all_times.to_frame(), curve, on='time', how='left')
        curve['bean_temp'] = curve['bean_temp'].interpolate(method='linear')
        
        features = {}
        
        # 基本特征
        features['duration'] = max_time
        features['end_temp'] = curve['bean_temp'].iloc[-1]
        features['turning_point_temp'] = curve['bean_temp'].min()
        
        # 2分钟后曲线下面积
        if TWO_MINUTES in curve['time'].values or max_time > TWO_MINUTES:
            features['auc_after_2min'] = curve[curve['time'] >= TWO_MINUTES]['bean_temp'].sum()
        else:
            features['auc_after_2min'] = None
        
        # 特定时间点的温度
        for time_point, col_name in [(THREE_MINUTES, 'temp_3min'), (FIVE_MINUTES, 'temp_5min')]:
            if curve.empty:
                features[col_name] = None
                continue
                
            # 如果精确时间点不存在，找到最接近的
            if time_point <= max_time:
                closest_time = curve['time'].iloc[(curve['time'] - time_point).abs().argsort()[0]]
                if abs(closest_time - time_point) <= 5:  # 在5秒内
                    features[col_name] = curve.loc[curve['time'] == closest_time, 'bean_temp'].iloc[0]
                else:
                    features[col_name] = None
            else:
                features[col_name] = None
        
        # 计算升温速率（Rate of Rise）
        def calculate_ror(time_point, period=ROR_PERIOD):
            if time_point > max_time or time_point - period < min_time:
                return None
                
            # 找到最接近的时间点
            closest_now = curve['time'].iloc[(curve['time'] - time_point).abs().argsort()[0]]
            closest_prev = curve['time'].iloc[(curve['time'] - (time_point - period)).abs().argsort()[0]]
            
            if abs(closest_now - time_point) > 5 or abs(closest_prev - (time_point - period)) > 5:
                return None
                
            temp_now = curve.loc[curve['time'] == closest_now, 'bean_temp'].iloc[0]
            temp_prev = curve.loc[curve['time'] == closest_prev, 'bean_temp'].iloc[0]
            time_diff = closest_now - closest_prev
            
            if time_diff <= 0:
                return None
                
            return (temp_now - temp_prev) * SECONDS_PER_MINUTE / time_diff
        
        features['ror_3min'] = calculate_ror(THREE_MINUTES)
        features['ror_5min'] = calculate_ror(FIVE_MINUTES)
        
        return features
    except Exception as e:
        print(f"计算烘焙特征出错: {str(e)}")
        _log.exception(f"计算烘焙特征出错: {str(e)}")
        return None

def load_model_components(model_path='./'):
    """从磁盘加载所有模型组件。
    
    参数:
        model_path (str): 模型文件路径
        
    返回:
        dict: 加载的模型组件，如果出错则返回None
    """
    try:
        # 尝试首先加载组合模型
        if os.path.exists(f'{model_path}moe_model.pkl'):
            with open(f'{model_path}moe_model.pkl', 'rb') as f:
                return pickle.load(f)

        _log.exception(f"beantimex: {model_path}")
        # 否则加载各个组件
        components = {}
        
        with open(f'{model_path}gmm.pkl', 'rb') as f:
            components['gmm'] = pickle.load(f)
            
        with open(f'{model_path}scaler.pkl', 'rb') as f:
            components['scaler'] = pickle.load(f)
            
        with open(f'{model_path}feature_cols.pkl', 'rb') as f:
            components['feature_cols'] = pickle.load(f)
            
        with open(f'{model_path}product_offsets.pkl', 'rb') as f:
            components['product_offsets'] = pickle.load(f)
        
        # 加载专家模型
        experts = []
        i = 0
        while True:
            try:
                with open(f'{model_path}expert_{i}.pkl', 'rb') as f:
                    experts.append(pickle.load(f))
                i += 1
            except FileNotFoundError:
                break
        
        if not experts:
            print("未找到专家模型")
            _log.exception("未找到专家模型")
            return None
            
        components['experts'] = experts
        return components
        
    except Exception as e:
        print(f"加载模型组件出错: {str(e)}")
        _log.exception(f"加载模型组件出错: {str(e)}")
        return None

def predict_agtron(features, product=None, model_path='./'):
    """使用MoE模型预测Agtron颜色。
    
    参数:
        features (dict): 特征值字典
        product (str): 产品名称，用于产品偏移调整
        model_path (str): 模型文件路径
        
    返回:
        float: 预测的Agtron颜色值
    """
    try:
        model_components = load_model_components(model_path)
        _log.exception(f"model_components: {model_components}")
        if not model_components:
            return None
            
        gmm = model_components['gmm']
        experts = model_components['experts']
        scaler = model_components['scaler']
        feature_cols = model_components['feature_cols']
        product_offsets = model_components['product_offsets']
        _log.exception(f"product_offsets: {product_offsets}")
        # 准备特征值数组
        X_new = np.array([[features[col] for col in feature_cols]])
        X_new_scaled = scaler.transform(X_new)
        
        # 预测聚类概率
        cluster_probs = gmm.predict_proba(X_new_scaled)[0]
        predictions = [expert.predict(X_new_scaled)[0] for expert in experts if expert is not None]
        
        # 计算有效概率
        valid_probs = [prob for i, prob in enumerate(cluster_probs) if experts[i] is not None]
        if not predictions:
            return np.nan
        
        # 计算加权平均预测
        total_prob = sum(valid_probs)
        if total_prob > 0:
            base_prediction = sum(p * pred for p, pred in zip(valid_probs, predictions)) / total_prob
        else:
            base_prediction = sum(predictions) / len(predictions)
        
        # 应用产品偏移
        final_prediction = base_prediction + product_offsets.get(product, 0)
        
        return final_prediction
    except Exception as e:
        print(f"预测Agtron值出错: {e}")
        _log.exception(f"预测Agtron值出错: {e}")
        return None

def predict_agtron_color(timex, beantemp, product=None, model_path='./'):
    """
    从时间和温度数据预测Agtron颜色值
    
    参数:
        timex (list): 时间点列表
        beantemp (list): 对应的豆温列表
        product (str): 产品名称，用于产品特定偏移
        model_path (str): 模型文件路径
        
    返回:
        float: 预测的Agtron颜色值，如果预测失败则返回None
    """
    # 计算特征
    features = calculate_roast_features(timex, beantemp)
    if not features:
        print("计算烘焙特征失败")
        _log.exception("计算烘焙特征失败")
        return None
    
    # 预测Agtron值
    predicted_value = predict_agtron(features, product, model_path)
    
    return predicted_value