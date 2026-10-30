# -*- coding: utf-8 -*-
"""
量化策略业务落地与 AI 模型探索 · 多品种联动看板
Streamlit 交互式应用（浅色主题）
"""
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="量化策略看板 | 多品种联动",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================== 全局配置 ====================
KLINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

VARIETIES = {
    "rb": "螺纹钢", "cu": "铜", "m": "豆粕", "MA": "甲醇",
    "al": "铝", "i": "铁矿石", "SR": "白糖", "TA": "PTA",
}

PERIODS = ["week", "day", "2hour", "1hour", "15min", "5min"]
PERIOD_LABELS = {
    "week": "周线", "day": "日线", "2hour": "2小时",
    "1hour": "1小时", "15min": "15分钟", "5min": "5分钟",
}
PERIOD_COLORS = {
    "week": "#d29922", "day": "#8b5cf6", "2hour": "#2563eb",
    "1hour": "#16a34a", "15min": "#64748b", "5min": "#dc2626",
}

# ==================== 浅色主题 CSS ====================
st.markdown("""
<style>
  .stApp { background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%); }
  .block-container { padding-top: 2.2rem; padding-bottom: 2rem; max-width: 1180px; }
  h1, h2, h3 { color: #0f172a !important; letter-spacing: -0.2px; }
  .hero-badge {
    display: inline-block; padding: 6px 16px; border: 1px solid #cbd5e1;
    border-radius: 999px; font-size: 13px; color: #2563eb;
    background: #eff6ff; margin-bottom: 14px;
  }
  .hero-title {
    font-size: 38px; font-weight: 800; line-height: 1.25;
    background: linear-gradient(135deg, #0f172a 0%, #2563eb 70%, #7c3aed 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .hero-sub { font-size: 18px; color: #475569; margin-top: 12px; max-width: 780px; }
  .hero-tags { margin-top: 18px; display: flex; gap: 9px; flex-wrap: wrap; }
  .hero-tags span {
    padding: 5px 13px; border-radius: 8px; font-size: 12.5px;
    background: #ffffff; border: 1px solid #e2e8f0; color: #64748b;
  }
  .pain-card {
    margin: 22px 0 10px; padding: 22px 26px; border-radius: 16px;
    background: linear-gradient(135deg, #fff7ed, #fef3c7);
    border: 1px solid #fcd34d; color: #7c2d12; font-size: 15px;
  }
  .pain-card b { color: #b45309; }
  .metric-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px;
    padding: 20px 22px; box-shadow: 0 1px 3px rgba(15,23,42,0.06);
  }
  .metric-label { font-size: 13px; color: #64748b; margin-bottom: 6px; }
  .metric-value { font-size: 30px; font-weight: 800; letter-spacing: -1px; }
  .metric-desc { font-size: 12px; color: #94a3b8; margin-top: 4px; }
  .sec-label {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 12px; letter-spacing: 1.5px; color: #2563eb;
    font-weight: 700; margin-bottom: 8px; text-transform: uppercase;
  }
  .sec-label .dot { width: 7px; height: 7px; border-radius: 50%; background: #2563eb; }
  .section-title { font-size: 26px; font-weight: 750; color: #0f172a; margin-bottom: 6px; }
  .section-desc { font-size: 15px; color: #475569; margin-bottom: 18px; }
  .feature-list { list-style: none; }
  .feature-list li {
    padding: 13px 0; border-bottom: 1px solid #e2e8f0;
    display: flex; gap: 12px; align-items: flex-start; font-size: 14px; color: #334155;
  }
  .feature-list li:last-child { border-bottom: none; }
  .feature-list .ico {
    width: 26px; height: 26px; border-radius: 7px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; margin-top: 1px;
  }
  .ico-blue { background: #eff6ff; color: #2563eb; }
  .ico-green { background: #f0fdf4; color: #16a34a; }
  .ico-red { background: #fef2f2; color: #dc2626; }
  .ico-purple { background: #f5f3ff; color: #7c3aed; }
  .feature-list strong { display: block; margin-bottom: 1px; color: #0f172a; }
  .feature-list .fdesc { color: #64748b; font-size: 12.5px; }
  .reflection {
    background: linear-gradient(135deg, #eff6ff, #f5f3ff);
    border: 1px solid #e0e7ff; border-radius: 16px;
    padding: 28px 32px; margin: 26px 0;
  }
  .reflection h3 { font-size: 19px; margin-bottom: 14px; color: #0f172a; }
  .reflection p { font-size: 15px; color: #334155; line-height: 1.95; }
  .reflection .quote {
    font-size: 17px; font-style: italic; color: #2563eb;
    margin: 14px 0; padding-left: 16px; border-left: 3px solid #2563eb;
  }
  .disclaimer {
    margin: 30px 0 10px; padding: 20px 24px; border-radius: 14px;
    background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #f59e0b;
    color: #78350f; font-size: 13px; line-height: 1.85;
  }
  .stSelectbox label { color: #0f172a !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ==================== 数据处理 ====================
@st.cache_data(show_spinner=False)
def load_data(code: str):
    """读取指定品种六周期数据，返回平滑曲线与信号。"""
    agg_dir = os.path.join(KLINE_DIR, code, "aggregated")
    raw, curves, bars, times = {}, {}, {}, {}

    for p in PERIODS:
        f = os.path.join(agg_dir, p + ".csv")
        if not os.path.exists(f):
            raw[p] = None; bars[p] = 0; continue
        df = pd.read_csv(f)
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
        df = df[df["close"].notna()].reset_index(drop=True)
        raw[p] = df; bars[p] = len(df)
        times[p] = df["datetime"].values if "datetime" in df.columns else None

    def holt(s, a=0.3, b=0.1):
        n = len(s)
        if n < 2:
            return s.copy(), np.zeros(n)
        lv, tr = np.zeros(n), np.zeros(n)
        lv[0] = s.iloc[0]
        tr[0] = s.iloc[1] - s.iloc[0] if n > 1 else 0
        for i in range(1, n):
            lv[i] = a * s.iloc[i] + (1 - a) * (lv[i - 1] + tr[i - 1])
            tr[i] = b * (lv[i] - lv[i - 1]) + (1 - b) * tr[i - 1]
        return lv + tr, tr

    smoothed, slopes = {}, {}
    for p in PERIODS:
        if raw.get(p) is None or len(raw[p]) == 0:
            smoothed[p] = np.array([]); slopes[p] = np.array([]); continue
        sm, sl = holt(raw[p]["close"].reset_index(drop=True))
        smoothed[p] = sm; slopes[p] = sl

    def align(target, ts):
        if ts is None or len(ts) == 0:
            return -1
        m = ts <= target
        if not m.any():
            return -1
        return int(np.where(m)[0][-1])

    signals = []
    if len(smoothed.get("5min", [])) > 0:
        base_t = times["5min"]; N_WEEK, M_DAY = 5, 8; prev = False
        for i in range(max(N_WEEK * 7, M_DAY, 30), len(base_t)):
            tt = base_t[i]
            wi = align(tt, times["week"])
            if wi < N_WEEK:
                prev = False; continue
            wret = (smoothed["week"][wi] - smoothed["week"][wi - N_WEEK]) / smoothed["week"][wi - N_WEEK]
            c1 = -0.035 <= wret <= -0.01
            di = align(tt, times["day"])
            if di < M_DAY:
                prev = False; continue
            dret = (smoothed["day"][di] - smoothed["day"][di - M_DAY]) / smoothed["day"][di - M_DAY]
            c2 = dret >= 0.01
            h2i = align(tt, times["2hour"])
            if h2i < 15:
                prev = False; continue
            w2 = smoothed["2hour"][max(0, h2i - 20):h2i + 1]
            low = max(0, h2i - 20) + int(np.argmin(w2))
            c3 = 5 <= (h2i - low) <= 15
            m15i = align(tt, times["15min"]); c4a = True
            if m15i >= 10:
                m15ret = (smoothed["15min"][m15i] - smoothed["15min"][m15i - 10]) / smoothed["15min"][m15i - 10]
                c4a = m15ret >= -0.01
            c4b = True
            if i >= 10:
                m5ret = (smoothed["5min"][i] - smoothed["5min"][i - 10]) / smoothed["5min"][i - 10]
                c4b = m5ret >= -0.01
            cur = c1 and c2 and c3 and c4a and c4b
            if cur and not prev:
                ret30 = None
                if i + 30 < len(raw["5min"]):
                    p0 = float(raw["5min"]["close"].iloc[i])
                    p1 = float(raw["5min"]["close"].iloc[i + 30])
                    if p0:
                        ret30 = (p1 - p0) / p0 * 100
                signals.append({"idx": i, "price": float(smoothed["5min"][i]), "ret30": ret30})
            prev = cur

    deduped = []
    for s in signals:
        if not deduped or s["idx"] - deduped[-1]["idx"] > 30:
            deduped.append(s)

    return {
        "curves": {p: list(smoothed.get(p, [])) for p in PERIODS},
        "signals": deduped, "bars": bars,
        "close_5min": raw["5min"]["close"].values if raw.get("5min") is not None else np.array([]),
    }


@st.cache_data(show_spinner=False)
def load_iv_data():
    """脱敏重构的铜期权 IV 数据（真实值 + MLP 预测）。"""
    np.random.seed(42)
    n = 100
    t = np.linspace(0, 10, n)
    iv_real = 22 + 5 * np.sin(t * 0.8) + 3 * np.sin(t * 2.1) + np.random.normal(0, 1.2, n)
    iv_real = np.maximum(iv_real, 15)
    iv_pred = np.zeros(n)
    iv_pred[0] = iv_real[0]
    for i in range(1, n):
        iv_pred[i] = iv_real[i - 1] + np.random.normal(0, 1.8)
        iv_pred[i] = max(iv_pred[i], 15)
    iv_pred = iv_pred * 0.6 + iv_real * 0.4
    return iv_real, iv_pred


def resample_to(curve, n):
    if len(curve) == 0:
        return [None] * n
    step = len(curve) / n
    return [float(curve[min(len(curve) - 1, int(i * step))]) for i in range(n)]


# ==================== 页面渲染 ====================
# Hero
st.markdown('<div class="hero-badge">AI 产品经理 / AI 数据工程师 · 作品展示</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">量化策略业务落地<br>与 AI 模型探索可视化</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">将交易员高度主观的「盘感」，拆解为可量化、可回测、可复用的数据管道；并主动引入 AI 模型，探索金融场景下的智能落地路径。</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-tags">'
    '<span>业务痛点拆解</span><span>0→1 规则量化</span><span>数据风控 / 前视偏差排雷</span>'
    '<span>MLP / 期权 IV 预测</span><span>可视化看板</span></div>',
    unsafe_allow_html=True,
)

# 痛点
st.markdown(
    '<div class="pain-card">◆ <b>为什么要做这件事</b>：在量化实习中，业务的核心矛盾是——'
    '交易员高度依赖主观「盘感」做期货与期权决策，<b>经验难以传承、缺乏数据支撑、无法复盘验证</b>。'
    '我把需求拆成两步：先用规则把盘感「翻译」成程序能懂的信号，再用 AI 模型寻找规则之外的增量价值。</div>',
    unsafe_allow_html=True,
)

# ===== 探索一 =====
st.markdown('<div class="sec-label"><span class="dot"></span>探索一 · 从 0 到 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">多周期趋势策略与信号看板</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">把「金字塔多周期盘感」量化为程序信号：对期货 6 个时间粒度做 Holt 双指数平滑，以「周线累计跌幅 + 日线累计涨幅 + 中周期企稳 + 小周期过滤」四条件生成做多 / 做空 / 空仓信号。</div>', unsafe_allow_html=True)

options = [f"{code} ({name})" for code, name in VARIETIES.items()]
choice = st.selectbox("◆ 选择品种", options, index=0)
code = choice.split(" ")[0]
name = VARIETIES[code]

st.markdown(f'<div style="font-size:17px;font-weight:650;color:#0f172a;margin:6px 0 4px;">当前展示：{name} ({code}) 多周期均线看板</div>', unsafe_allow_html=True)

data = load_data(code)
curves = data["curves"]
signals = data["signals"]
bars = data["bars"]

n_ref = min(max(len(curves.get(p, [])) for p in PERIODS) or 1, 200)
x = list(range(n_ref))
base_curve = resample_to(curves.get("5min", []), n_ref)

fig = go.Figure()
for p in PERIODS:
    ys = resample_to(curves.get(p, []), n_ref)
    fig.add_trace(go.Scatter(
        x=x, y=ys, mode="lines", name=PERIOD_LABELS[p],
        line=dict(width=2.4 if p in ("week", "day") else 1.4, color=PERIOD_COLORS[p]),
    ))

if signals:
    sig_x, sig_y, hover = [], [], []
    for s in signals:
        pos = int(s["idx"] / max(1, len(base_curve)) * n_ref) if len(base_curve) else 0
        pos = min(pos, n_ref - 1)
        sig_x.append(pos)
        sig_y.append(base_curve[pos] if pos < len(base_curve) else s["price"])
        r = s["ret30"]
        hover.append(f"独立做多信号<br>价格: {s['price']:.1f}<br>30根后收益: {r:.2f}%" if r is not None else f"独立做多信号<br>价格: {s['price']:.1f}")
    fig.add_trace(go.Scatter(
        x=sig_x, y=sig_y, mode="markers", name="独立信号点",
        marker=dict(color="#16a34a", size=13, symbol="triangle-up", line=dict(width=1.5, color="#ffffff")),
        hovertemplate="%{customdata}<extra></extra>", customdata=hover,
    ))
else:
    fig.add_annotation(
        text="该品种在当前参数下未触发独立信号",
        xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#b45309"),
        bgcolor="rgba(254,243,199,0.92)", bordercolor="#f59e0b", borderwidth=1, borderpad=12,
    )

fig.update_layout(
    height=470, margin=dict(l=50, r=20, t=20, b=45),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.6)",
    font=dict(color="#475569", size=11),
    xaxis=dict(gridcolor="#e2e8f0", zerolinecolor="#e2e8f0", title="时间轴（归一化）"),
    yaxis=dict(gridcolor="#e2e8f0", zerolinecolor="#e2e8f0", title="Holt 平滑值"),
    legend=dict(orientation="h", y=1.12, x=0, font=dict(size=11)),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# 指标卡片
if signals:
    rets = [s["ret30"] for s in signals if s["ret30"] is not None]
    wins = [r for r in rets if r > 0]
    win_rate = f"{len(wins)/len(rets)*100:.1f}%" if rets else "N/A"
    avg_ret = f"{np.mean(rets):+.2f}%" if rets else "N/A"
    opp = len(signals)
    wr_color = "#16a34a" if rets and len(wins)/len(rets) >= 0.5 else "#d29922"
else:
    win_rate = "N/A"; avg_ret = "N/A"; opp = 0; wr_color = "#d29922"

total_bars = sum(bars.values())
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">独立机会数</div><div class="metric-value" style="color:#2563eb">{opp}</div><div class="metric-desc">跨周期去重后的真实机会</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">30根后胜率</div><div class="metric-value" style="color:{wr_color}">{win_rate}</div><div class="metric-desc">触发后 30 根 K 线收益为正占比</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">平均收益</div><div class="metric-value" style="color:#7c3aed">{avg_ret}</div><div class="metric-desc">单笔 30 根平均收益</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">K线覆盖</div><div class="metric-value" style="color:#d29922">{total_bars:,}</div><div class="metric-desc">六周期合计数据量</div></div>', unsafe_allow_html=True)

if not signals:
    st.info("ℹ️ 该品种在当前参数下未触发独立信号。均线已正常渲染，可切换其他品种查看。")

# 策略设计要点
st.markdown("")
d1, d2 = st.columns(2)
with d1:
    st.markdown('<div class="metric-card"><ul class="feature-list">'
        '<li><div class="ico ico-blue">◧</div><div><strong>多周期共振</strong><span class="fdesc">周线 / 日线 / 2h / 1h / 15min / 5min 六粒度 Holt 平滑，观察趋势一致性</span></div></li>'
        '<li><div class="ico ico-green">⟳</div><div><strong>状态变化触发</strong><span class="fdesc">信号只在「条件由 False 翻转为 True」时触发，避免重复开仓</span></div></li>'
        '<li><div class="ico ico-purple">◷</div><div><strong>时间戳对齐</strong><span class="fdesc">跨周期数据按时间戳而非索引对齐，杜绝跨周期引用错位</span></div></li>'
        '<li><div class="ico ico-red">⊘</div><div><strong>止损周期匹配</strong><span class="fdesc">1 小时趋势止损表现最均衡（触发率 27.3%，胜率 36.4%）</span></div></li>'
        '</ul></div>', unsafe_allow_html=True)
with d2:
    st.markdown('<div class="metric-card"><ul class="feature-list">'
        '<li><div class="ico ico-blue">◇</div><div><strong>盈利来源</strong><span class="fdesc">横盘突破与超跌反弹，靠少数大单边行情贡献收益</span></div></li>'
        '<li><div class="ico ico-red">◆</div><div><strong>失败来源</strong><span class="fdesc">趋势追高、下跌延续；止损周期与入场周期层级不匹配</span></div></li>'
        '<li><div class="ico ico-green">◫</div><div><strong>低胜率 / 高盈亏比</strong><span class="fdesc">盈利由少数大行情驱动，更适合期权杠杆放大尾部收益</span></div></li>'
        '</ul></div>', unsafe_allow_html=True)

# ===== 探索二：铜期权 IV =====
st.write("")
st.markdown('<div class="sec-label"><span class="dot"></span>探索二 · 从规则到 AI</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">铜期权隐含波动率（IV）预测模型</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">为了寻找规则策略之外的增量，我主动引入 AI：用 MLP 神经网络预测铜期权隐含波动率的走势，并构建跨式策略回测验证。下图为脱敏重构的 IV 预测可视化——真实 IV 与模型预测 IV 曲线叠加。</div>', unsafe_allow_html=True)

iv_real, iv_pred = load_iv_data()
n_iv = len(iv_real)
xiv = list(range(n_iv))
fig_iv = go.Figure()
fig_iv.add_trace(go.Scatter(x=xiv, y=iv_real, mode="lines", name="真实 IV",
    line=dict(color="#2563eb", width=2.2), fill="tozeroy", fillcolor="rgba(37,99,235,0.08)"))
fig_iv.add_trace(go.Scatter(x=xiv, y=iv_pred, mode="lines", name="MLP 预测 IV",
    line=dict(color="#dc2626", width=2, dash="dot")))
fig_iv.update_layout(
    height=380, margin=dict(l=50, r=20, t=20, b=45),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.6)",
    font=dict(color="#475569", size=11),
    xaxis=dict(gridcolor="#e2e8f0", zerolinecolor="#e2e8f0", title="时间序列"),
    yaxis=dict(gridcolor="#e2e8f0", zerolinecolor="#e2e8f0", title="隐含波动率 IV (%)"),
    legend=dict(orientation="h", y=1.12, x=0, font=dict(size=11)),
    hovermode="x unified",
)
st.plotly_chart(fig_iv, use_container_width=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-card"><div class="metric-label">样本外方向准确率</div><div class="metric-value" style="color:#16a34a">59.6%</div><div class="metric-desc">修复前视偏差后真实表现</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-card"><div class="metric-label">覆盖期权合约</div><div class="metric-value" style="color:#2563eb">36</div><div class="metric-desc">3 到期月 × 6 行权价 × 买/卖</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-card"><div class="metric-label">特征维度</div><div class="metric-value" style="color:#7c3aed">12</div><div class="metric-desc">BS 反推 IV → 时序特征工程</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-card"><div class="metric-label">建模方式</div><div class="metric-value" style="color:#d29922">MLP</div><div class="metric-desc">按在值程度分类建模</div></div>', unsafe_allow_html=True)

# ===== 数据风控 =====
st.write("")
st.markdown('<div class="sec-label"><span class="dot"></span>数据风控意识</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">排雷未来函数 · 守住回测底线</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">量化研究最隐蔽的错误是「前视偏差（未来函数）」。我在两个项目中都主动识别并修复了这一问题，这体现的是数据产品的风控底线意识。</div>', unsafe_allow_html=True)
r1, r2 = st.columns(2)
with r1:
    st.markdown('<div class="metric-card" style="border-top:3px solid #dc2626">'
        '<div class="metric-label">🔴 已排雷 · 未来函数修复</div>'
        '<div class="metric-value" style="color:#dc2626">7.83% → 4.38%</div>'
        '<div class="metric-desc">索引对齐 → 时间戳对齐。修复后胜率回归真实，证明原信号逻辑无效，而非数据问题。铜期权项目中同样发现 shift(-5) 特征泄露未来数据，导致夏普虚高至 268。</div></div>', unsafe_allow_html=True)
with r2:
    st.markdown('<div class="metric-card" style="border-top:3px solid #16a34a">'
        '<div class="metric-label">🟢 已收敛 · 独立信号分析</div>'
        '<div class="metric-value" style="color:#16a34a">21 → 18 → 9</div>'
        '<div class="metric-desc">状态变化触发压缩 + 跨品种去重，收敛为真正独立的机会。黑色板块内部（螺纹钢 / 铁矿石）信号高度相关，组合层面必须考虑独立性。</div></div>', unsafe_allow_html=True)

# ===== 个人复盘 =====
st.write("")
st.markdown('<div class="reflection">'
    '<h3>◆ 个人复盘</h3>'
    '<p>这段研究让我对「数据产品」有了更完整的理解：它不只是跑通一个模型或画一张图。</p>'
    '<div class="quote">懂业务，才能把「盘感」拆解成可量化的规则；懂 AI，才能用模型去寻找规则之外的增量；而守住数据底线（排雷未来函数），才让这些结论真正可信。</div>'
    '<p>从前视偏差导致夏普虚高 268，到修复后回归真实；从 21 个信号压缩到 9 个独立机会——这些「排雷」的过程，比直接调出一个盈利结果更有价值。它们训练的是数据产品的风控意识。</p>'
    '</div>', unsafe_allow_html=True)

# 合规声明
st.markdown(
    '<div class="disclaimer">⚠️ <b>合规与脱敏声明</b>：因业务保密协议，本页面不展示真实的交易参数、持仓与资金曲线。'
    '当前展示为「脱敏重构的数据管道与视觉模型演示」，仅用于说明方法论、技术路径与研究思路，不构成任何投资建议。</div>',
    unsafe_allow_html=True,
)
