# 量化策略业务落地与 AI 模型探索 · 多品种看板

基于量化实习研究的交互式 Streamlit 看板，展示：
- **探索一**：多周期趋势策略（8 品种联动，Holt 双指数平滑）
- **探索二**：铜期权隐含波动率（IV）MLP 预测模型
- **数据风控**：前视偏差排雷、独立信号分析

## 本地运行
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 部署
推送到 GitHub 后，在 [Streamlit Community Cloud](https://share.streamlit.io) 一键部署。

## 说明
页面展示为「脱敏重构的数据管道与视觉模型演示」，不含真实交易参数与资金曲线。
