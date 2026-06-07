import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FIG_W, FIG_H = 10, 8

fig, ax = plt.subplots(1, 1, figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis('off')

C_BG = '#1a1a2e'
C_LAYER = '#16213e'
C_CLIENT = '#0f3460'
C_APP = '#e94560'
C_MODEL = '#0a81ab'
C_TEMPLATE = '#3ec1d3'
C_DB = '#f6a025'
C_STORAGE = '#7c3aed'

fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)

def draw_layer(y, h, label, alpha=0.5):
    rect = FancyBboxPatch((0.2, y), FIG_W - 0.4, h,
        boxstyle="round,pad=0.1", facecolor=C_LAYER, edgecolor='none', alpha=alpha, zorder=0)
    ax.add_patch(rect)
    ax.text(0.4, y + h - 0.3, label, fontsize=11, fontweight='bold',
            color='#e94560', ha='left', va='top')

def draw_box(x, y, w, h, label, desc='', color=C_APP):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
        facecolor=color, edgecolor='white', linewidth=1.2, alpha=0.9, zorder=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h*0.58, label, fontsize=9, fontweight='bold',
            color='white', ha='center', va='center', zorder=3)
    if desc:
        ax.text(x + w/2, y + h*0.25, desc, fontsize=7, color='#dddddd',
                ha='center', va='center', zorder=3)

def arrow(x1, y1, x2, y2, color='#888899', style='arc3,rad=0.', lw=1.5):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
        arrowstyle='->,head_length=4,head_width=3',
        color=color, lw=lw, connectionstyle=style, zorder=1, alpha=0.8))

# === Client Layer ===
draw_layer(6.8, 1.0, 'Клиент')
draw_box(1.0, 7.0, 2.5, 0.7, 'Веб-браузер', 'HTTP-запросы', C_CLIENT)
draw_box(4.5, 7.0, 2.5, 0.7, 'Мобильные устройства', 'Адаптивная вёрстка', C_CLIENT)
draw_box(8.0, 7.0, 1.5, 0.7, 'Django Admin', 'Панель управления', C_CLIENT)

# === Django Layer ===
draw_layer(3.0, 3.5, 'Серверная часть (Django)')

draw_box(0.5, 4.2, 1.8, 0.8, 'Django Middleware', 'CSP / CSRF / Сессии', C_APP)
draw_box(2.6, 4.2, 1.8, 0.8, 'URL Router (urls.py)', 'Диспетчеризация', C_APP)
draw_box(4.7, 4.2, 1.8, 0.8, 'Views (views.py)', 'Бизнес-логика', C_APP)
draw_box(6.8, 4.2, 1.8, 0.8, 'Templates (HTML)', 'Рендеринг страниц', C_TEMPLATE)
draw_box(9.0, 4.2, 1.0, 0.8, 'Static', 'CSS / JS', C_TEMPLATE)

draw_box(0.5, 3.2, 1.8, 0.7, 'Forms (forms.py)', 'Валидация', C_MODEL)
draw_box(2.6, 3.2, 1.8, 0.7, 'Models (models.py)', 'ORM Django', C_MODEL)
draw_box(4.7, 3.2, 1.8, 0.7, 'Admin (admin.py)', 'Модерация', C_APP)
draw_box(6.8, 3.2, 1.8, 0.7, 'Management cmd', 'populate_news', C_MODEL)

# === Data Layer ===
draw_layer(0.3, 2.6, 'Хранение данных')
draw_box(1.0, 0.6, 3.5, 2.0, 'PostgreSQL', 'Реляционная БД\nACID / 3НФ', C_DB)
draw_box(5.5, 0.6, 3.0, 2.0, 'Файловая система', 'media/news/\nИзображения', C_STORAGE)

# === Arrows ===
arrow(2.25, 6.9, 3.4, 5.1, '#888899', 'arc3,rad=-0.2')
arrow(2.25, 6.9, 1.4, 5.1, '#888899', 'arc3,rad=0.2')
arrow(5.75, 6.9, 5.5, 5.1)
arrow(5.75, 6.9, 7.7, 5.1, '#888899', 'arc3,rad=0.1')

arrow(8.75, 6.9, 8.75, 6.0)
arrow(8.75, 5.8, 9.5, 5.0, '#888899', 'arc3,rad=0.')
arrow(8.75, 5.8, 5.6, 5.0, '#888899', 'arc3,rad=-0.2')

arrow(4.4, 4.2, 4.65, 4.2, '#e94560')
arrow(6.5, 4.2, 6.75, 4.2, '#3ec1d3')
arrow(4.4, 3.55, 5.0, 4.2, '#0a81ab', 'arc3,rad=-0.3')

arrow(5.6, 2.9, 2.75, 2.7, '#f6a025', 'arc3,rad=-0.1')
arrow(7.5, 2.9, 7.0, 2.7, '#7c3aed', 'arc3,rad=0.1')

# === Title ===
ax.text(FIG_W/2, 7.85, 'Архитектура ResonateNews (MVT)', fontsize=15, fontweight='bold',
        color='white', ha='center', va='center')

ax.text(FIG_W/2, 7.6, 'Django 6.0.4 + PostgreSQL', fontsize=8, color='#aaaaaa',
        ha='center', va='center')

# === Legend ===
legend = [
    mpatches.Patch(facecolor=C_CLIENT, edgecolor='white', label='Клиент'),
    mpatches.Patch(facecolor=C_APP, edgecolor='white', label='Приложение (Views/Admin)'),
    mpatches.Patch(facecolor=C_MODEL, edgecolor='white', label='Модели (ORM)'),
    mpatches.Patch(facecolor=C_TEMPLATE, edgecolor='white', label='Шаблоны/Статика'),
    mpatches.Patch(facecolor=C_DB, edgecolor='white', label='PostgreSQL'),
    mpatches.Patch(facecolor=C_STORAGE, edgecolor='white', label='Файлы'),
]
ax.legend(handles=legend, loc='lower center', bbox_to_anchor=(0.5, 0.0),
          ncol=3, framealpha=0.5, facecolor=C_LAYER, edgecolor='none',
          fontsize=7, labelcolor='white')

plt.savefig(r'D:\DIPLOM\architecture.png', dpi=150, bbox_inches='tight',
            facecolor=C_BG)
plt.close()
print('Done')
