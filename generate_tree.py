import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 1, figsize=(6, 5))
ax.set_xlim(0, 6)
ax.set_ylim(0, 5)
ax.axis('off')

C_BG = '#1a1a2e'
C_ROOT = '#e94560'
C_DIR = '#3ec1d3'
C_FILE = '#cccccc'
C_PY = '#f6a025'
C_HTML = '#a78bfa'
C_DIM = '#888899'

fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)

ax.text(3.0, 4.8, 'Структура ResonateNews', fontsize=14, fontweight='bold',
        color='white', ha='center', va='center')

entries = []
y = 4.3
step = 0.4

def d(x, y, name, color=C_DIR):
    entries.append((x, y, '+-- ' + name, color, 'bold'))

def f(x, y, name, color=C_FILE):
    entries.append((x, y, '+-- ' + name, color, 'normal'))

d(0.3, y, 'itinfo/ (проект)'); y -= step
f(1.0, y, 'settings.py', C_PY); y -= step
f(1.0, y, 'urls.py', C_PY); y -= step
y -= 0.1

d(0.3, y, 'news/ (приложение)'); y -= step
f(1.0, y, 'views.py', C_PY); y -= step
f(1.0, y, 'models.py', C_PY); y -= step
f(1.0, y, 'urls.py', C_PY); y -= step
f(1.0, y, 'forms.py', C_PY); y -= step
f(1.0, y, 'admin.py', C_PY); y -= step
d(1.0, y, 'migrations/'); y -= step
y -= 0.1

d(0.3, y, 'templates/'); y -= step
f(1.0, y, 'base.html', C_HTML); y -= step
d(1.0, y, 'news/ (7 шаблонов)'); y -= step
y -= 0.1

d(0.3, y, 'static/css/'); y -= step
f(1.0, y, 'style.css'); y -= step
y -= 0.1

d(0.3, y, 'media/news/'); y -= step
f(1.0, y, '<изображения>', C_DIM); y -= step
y -= 0.1

f(0.3, y, 'manage.py', C_PY); y -= step
f(0.3, y, '.env'); y -= step
f(0.3, y, 'requirements.txt'); y -= step

for x, y, text, color, weight in entries:
    ax.text(x, y, text, fontsize=8, fontweight=weight,
            color=color, ha='left', va='center', fontfamily='monospace')

plt.savefig(r'D:\DIPLOM\project_structure.png', dpi=150, bbox_inches='tight',
            facecolor=C_BG)
plt.close()
print('Done')
