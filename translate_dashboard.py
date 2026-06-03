import re

with open('smart_wave_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

translations = [
    ('lang="zh-CN"', 'lang="en"'),
    ('Smart Wave Allocation | 智能波次分配看板', 'Smart Wave Allocation Dashboard'),
    ('基于深度强化学习的医药订单智能波次分配系统', 'Pharma Order Intelligent Wave Allocation via Deep RL'),
    ('今日订单', 'Today Orders'),
    ('活跃波次', 'Active Waves'),
    ('分拣进度', 'Sort Progress'),
    ('人力负载', 'Labor Load'),
    ('⚡ 实时分拣', '⚡ Real-Time'),
    ('📦 波次管理', '📦 Wave Mgmt'),
    ('📊 算法对比', '📊 Comparison'),
    ('🔔 异常预警', '🔔 Alerts'),
    ('▶ 开始仿真', '▶ Start Sim'),
    ('⏸ 暂停', '⏸ Pause'),
    ('⟲ 重置', '⟲ Reset'),
    ('速度:', 'Speed:'),
    ('仿真时间:', 'Sim Time:'),
    ('步数:', 'Steps:'),
    ('当前波次订单', 'Current Wave Orders'),
    ('波次体积', 'Wave Volume'),
    ('累计拣货距离', 'Total Pick Distance'),
    ('累计奖励', 'Total Reward'),
    ('容量:', 'Cap:'),
    ('波次数:', 'Waves:'),
    ('+0/步', '+0/step'),
    ('🏭 仓库区域覆盖', '🏭 Warehouse Zone Coverage'),
    ('2×4 网格布局', '2×4 Grid Layout'),
    ('常温 Ambient', 'Ambient'),
    ('阴凉 Cool', 'Cool'),
    ('冷藏 Cold', 'Cold'),
    ('冷冻 Frozen', 'Frozen'),
    ('📋 最近波次', '📋 Recent Waves'),
    ('点击"开始仿真"查看波次分配过程', 'Click "Start Sim" to see wave allocation'),
    ('仿真已重置', 'Simulation reset'),
    ('📈 奖励趋势', '📈 Reward Trend'),
    ('实时累计', 'Real-time Cumulative'),
    ('🌡️ 温度合规状态', '🌡️ Temp Compliance'),
    ('当前波次', 'Current Wave'),
    ('📦 订单到达流', '📦 Order Arrival Stream'),
    ('最近到达的订单（按温度着色）', 'Recent arrivals (color-coded by temp)'),
    ('等待仿真开始...', 'Waiting for simulation...'),
    ('🌊 所有波次详情', '🌊 All Wave Details'),
    ('请先完成实时仿真', 'Please complete real-time simulation first'),
    ('📊 波次规模分布', '📊 Wave Size Distribution'),
    ('🗺️ 波次区域覆盖', '🗺️ Wave Zone Coverage'),
    ('🏆 算法性能对比', '🏆 Algorithm Comparison'),
    ('方法', 'Method'),
    ('平均奖励', 'Avg Reward'),
    ('波次数', 'Waves'),
    ('拣货距离', 'Distance'),
    ('超时', 'Misses'),
    ('温度违规', 'Violations'),
    ('📊 总奖励对比', '📊 Total Reward Comparison'),
    ('📈 拣货距离对比', '📈 Picking Distance Comparison'),
    ('🔥 温度违规 vs 距离', '🔥 Violations vs Distance'),
    ('📉 PPO 训练曲线', '📉 PPO Training Curve'),
    ('🚨 实时异常', '🚨 Real-time Alerts'),
    ('系统正常运行中。异常将在仿真过程中自动检测并显示。', 'System normal. Alerts auto-detect during simulation.'),
    ('⚠️ 预警统计', '⚠️ Alert Statistics'),
    ('📋 异常日志', '📋 Alert Log'),
    ('暂无异常记录', 'No alerts yet'),
    ('温度混装', 'Temp Mixing'),
    ('容量超载', 'Overload'),
    ('超时风险', 'Deadline Risk'),
    ('正常', 'Normal'),
    ('订单', 'orders'),
    ('区域', 'zones'),
    ('波次', 'Wave'),
    ('存在温度混装风险（常温+冷冻）', 'temp mixing risk (Ambient + Frozen)'),
    ('即将满载', 'almost full'),
    ('请先完成实时仿真', 'Please run simulation first'),
    ('▶ 重新开始', '▶ Restart'),
    ('温度混装警报:', 'TEMP MIX ALERT:'),
    ('容量预警:', 'CAPACITY WARN:'),
]

for cn, en in translations:
    content = content.replace(cn, en)

# Fix temp names in JS
content = content.replace("'常温','阴凉','冷藏','冷冻'", "'Ambient','Cool','Cold','Frozen'")

with open('smart_wave_dashboard_en.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Created smart_wave_dashboard_en.html')
chinese_chars = re.findall(r'[一-鿿]', content)
if chinese_chars:
    print(f'Warning: {len(chinese_chars)} Chinese chars remain')
    print('Sample:', ''.join(sorted(set(chinese_chars))[:50]))
else:
    print('Verification: No Chinese characters remain')
