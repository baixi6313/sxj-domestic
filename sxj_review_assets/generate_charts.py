import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def _ensure_cjk_font():
    if not any("CJK" in f or "WenQuanYi" in f for f in matplotlib.rcParams.get('font.sans-serif', [])):
        import subprocess
        subprocess.run(["sed", "-i",
            "s|^#*[[:space:]]*font\\.family[[:space:]]*:.*|font.family: sans-serif|;"
            "s|^#*[[:space:]]*font\\.sans-serif[[:space:]]*:.*|font.sans-serif: Noto Sans CJK SC, WenQuanYi Micro Hei, DejaVu Sans, sans-serif|;"
            "s|^#*[[:space:]]*axes\\.unicode_minus[[:space:]]*:.*|axes.unicode_minus: False|",
            matplotlib.matplotlib_fname()])
        matplotlib.font_manager._load_fontmanager(try_read_cache=False)
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

_ensure_cjk_font()

# ========== Chart 1: 项目维度对比雷达图 ==========
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))

categories = ['身份确权', '事实验证', '跨主权能力', '去中心化程度', 'Agent支持', '无币架构']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# 事现鉴
sxj = [7, 6, 6, 5, 8, 9]
sxj += sxj[:1]

# W3C DID/VC标准
w3c = [9, 8, 9, 7, 3, 5]
w3c += w3c[:1]

# EAS (Ethereum Attestation Service)
eas = [5, 9, 7, 8, 2, 2]
eas += eas[:1]

# Gitcoin Passport
gitcoin = [8, 4, 6, 7, 2, 3]
gitcoin += gitcoin[:1]

# Kleros
kleros = [3, 8, 7, 9, 1, 2]
kleros += kleros[:1]

ax.plot(angles, sxj, 'o-', linewidth=2.5, color='#C41E3A', label='事现鉴 SXJ')
ax.fill(angles, sxj, alpha=0.15, color='#C41E3A')

ax.plot(angles, w3c, 's--', linewidth=1.5, color='#2978B5', label='W3C DID/VC')
ax.fill(angles, w3c, alpha=0.08, color='#2978B5')

ax.plot(angles, eas, '^--', linewidth=1.5, color='#D4A843', label='EAS')
ax.fill(angles, eas, alpha=0.08, color='#D4A843')

ax.plot(angles, gitcoin, 'D--', linewidth=1.5, color='#16A37B', label='Gitcoin Passport')
ax.fill(angles, gitcoin, alpha=0.08, color='#16A37B')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=9, color='#666')
ax.set_title('事现鉴与同类项目多维度能力对比\n（10分制·基于公开信息评估）', fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('sxj_review_assets/radar_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 1 saved: radar_comparison.png")

# ========== Chart 2: 安全/技术债优先级矩阵 ==========
fig, ax = plt.subplots(figsize=(10, 7))

issues = [
    ('C12 ratify字段可篡改', 9.5, 9.0, 'P0'),
    ('C9 CORS CSRF', 8.5, 7.5, 'P0'),
    ('D1 验证递归未闭合', 9.0, 6.0, 'P0'),
    ('C13 SSL证书到期', 7.0, 8.0, 'P0'),
    ('P1 无分页性能问题', 6.5, 8.5, 'P1'),
    ('C8 安全响应头缺失', 5.0, 6.0, 'P1'),
    ('C5 速率限制缺失', 5.5, 5.0, 'P1'),
    ('D2 共创意见重复', 4.0, 4.0, 'P2'),
    ('S1 robots/sitemap缺失', 2.0, 3.0, 'P2'),
    ('A1-10 三页404', 3.0, 2.0, 'P2'),
]

colors_p0 = '#C41E3A'
colors_p1 = '#D4A843'
colors_p2 = '#2978B5'

for name, impact, urgency, priority in issues:
    color = colors_p0 if priority == 'P0' else colors_p1 if priority == 'P1' else colors_p2
    size = 300 if priority == 'P0' else 200 if priority == 'P1' else 150
    ax.scatter(urgency, impact, s=size, c=color, alpha=0.8, edgecolors='white', linewidth=2, zorder=5)
    ax.annotate(name, (urgency, impact), textcoords="offset points",
                xytext=(8, 8), fontsize=9, fontweight='500')

# 象限分割
ax.axvline(x=6, color='#ccc', linestyle='--', alpha=0.7)
ax.axhline(y=6, color='#ccc', linestyle='--', alpha=0.7)

# 象限标签
ax.text(2.5, 9.5, '低紧急\n高影响', ha='center', va='center', fontsize=11, color='#666', fontweight='bold', alpha=0.6)
ax.text(8.5, 9.5, '高紧急\n高影响\n(P0)', ha='center', va='center', fontsize=11, color='#C41E3A', fontweight='bold', alpha=0.7)
ax.text(2.5, 2.5, '低紧急\n低影响\n(P2)', ha='center', va='center', fontsize=11, color='#666', fontweight='bold', alpha=0.6)
ax.text(8.5, 2.5, '高紧急\n低影响', ha='center', va='center', fontsize=11, color='#666', fontweight='bold', alpha=0.6)

ax.set_xlabel('紧急程度 (Urgency)', fontsize=12, fontweight='bold')
ax.set_ylabel('影响程度 (Impact)', fontsize=12, fontweight='bold')
ax.set_title('事现鉴技术问题优先级矩阵\n（基于2026-08-14安全审计报告）', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0, 11)
ax.set_ylim(0, 11)
ax.grid(True, alpha=0.2)

# 图例
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors_p0, markersize=12, label='P0 本周必须'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors_p1, markersize=10, label='P1 两周内'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors_p2, markersize=8, label='P2 一个月内'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig('sxj_review_assets/priority_matrix.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 2 saved: priority_matrix.png")

# ========== Chart 3: 项目成熟度评估 ==========
fig, ax = plt.subplots(figsize=(12, 7))

dimensions = ['协议设计', '技术实现', '安全审计', '治理机制', '用户规模', '学术背书', '生态兼容', '公信力建设']
scores = [7.0, 4.5, 3.5, 5.0, 1.5, 2.0, 3.0, 2.5]
targets = [9.0, 8.0, 9.0, 8.0, 7.0, 7.0, 8.0, 8.0]

y_pos = np.arange(len(dimensions))
bar_height = 0.35

bars1 = ax.barh(y_pos + bar_height/2, scores, bar_height, label='当前水平', color='#C41E3A', alpha=0.8)
bars2 = ax.barh(y_pos - bar_height/2, targets, bar_height, label='目标水平', color='#D4A843', alpha=0.5)

ax.set_yticks(y_pos)
ax.set_yticklabels(dimensions, fontsize=11, fontweight='bold')
ax.set_xlabel('成熟度评分 (0-10)', fontsize=12, fontweight='bold')
ax.set_title('事现鉴项目八维度成熟度评估\n（当前水平 vs 目标愿景）', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0, 10)
ax.legend(fontsize=10, loc='lower right')
ax.grid(True, axis='x', alpha=0.2)

for i, (s, t) in enumerate(zip(scores, targets)):
    gap = t - s
    ax.text(s + 0.1, i + bar_height/2, f'{s:.1f}', va='center', fontsize=9, fontweight='bold', color='#C41E3A')
    ax.text(t + 0.1, i - bar_height/2, f'差距 -{gap:.1f}', va='center', fontsize=8, color='#888')

ax.invert_yaxis()
plt.tight_layout()
plt.savefig('sxj_review_assets/maturity_assessment.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 3 saved: maturity_assessment.png")

print("All charts generated successfully!")
