## 量化策略业务落地与优化模型探索 · 多品种看板

基于量化实习研究内容，制作交互式 Streamlit 看板，展示：
- 探索一：多周期趋势策略（8 品种联动，Holt 双指数平滑）
- 探索二：铜期权隐含波动率（IV）MLP 预测模型
- 数据风控：前视偏差排雷、独立信号分析

## 已部署至 Streamlit，点击查看
https://quant-dashboard-a25iugewwo9kwswt7q94qd.streamlit.app/

## 说明
页面展示为「脱敏重构的数据管道与视觉模型演示」，不含真实交易参数与资金曲线。

## 本地运行
```bash
pip install -r requirements.txt
streamlit run app.py
