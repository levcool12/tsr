import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import os

# ==========================================
# НАСТРОЙКИ ПУТИ
# ==========================================
FILE_PATH = r"medical_data.csv"
# ==========================================

# 1. Безопасная загрузка данных
if os.path.exists(FILE_PATH):
    try:
        df = pd.read_csv(FILE_PATH, encoding='utf-8')
    except Exception:
        df = pd.read_csv(FILE_PATH, encoding='windows-1251')
else:
    print(f"⚠️ Файл не найден по пути: {FILE_PATH}")
    print("Запускаю встроенную программную симуляцию медицинского датасета...")
    
    import random
    random.seed(42)
    symptoms_pool = ['Fatigue', 'Fever', 'Cough', 'Shortness of breath', 'Sore throat', 'Headache', 'Runny nose', 'Body ache']
    
    demo_rows = []
    for i in range(1, 2001):
        p_s = random.sample(symptoms_pool, k=random.randint(1, 3))
        s1 = p_s if len(p_s) > 0 else 'None'
        s2 = p_s if len(p_s) > 1 else 'None'
        s3 = p_s if len(p_s) > 2 else 'None'
        demo_rows.append({
            'Patient_ID': i, 'Age': 45, 'Gender': 'Male',
            'Symptom_1': s1, 'Symptom_2': s2, 'Symptom_3': s3,
            'Heart_Rate_bpm': 70, 'Body_Temperature_C': 36.6,
            'Blood_Pressure_mmHg': '120/80', 'Oxygen_Saturation_%': 98,
            'Diagnosis': 'Cold', 'Severity': 'Mild', 'Treatment_Plan': 'Rest'
        })
    df = pd.DataFrame(demo_rows)

# 2. Обработка симптомов
symptom_cols = ['Symptom_1', 'Symptom_2', 'Symptom_3']
patient_combinations = []
all_symptoms = set()

for _, row in df.iterrows():
    symptoms = []
    for col in symptom_cols:
        val = row[col]
        # Проверяем на пустоту (работает и со списками, и со строками)
        if pd.notna(val) is True or (hasattr(val, '__len__') and len(val) > 0):
            # Если внутри ячейки оказался список/массив, вытаскиваем элементы
            if isinstance(val, (list, tuple, set)):
                symptoms.extend([str(item).strip() for item in val])
            else:
                symptoms.append(str(val).strip())
                
    symptoms = [s for s in symptoms if s.lower() not in ['none', 'nan', '']]
    symptoms.sort()
    if symptoms:
        patient_combinations.append(tuple(symptoms))
        all_symptoms.update(symptoms)

symptoms_list = sorted(list(all_symptoms))
num_symptoms = len(symptoms_list)

individual_counts = Counter()
for s_tuple in patient_combinations:
    individual_counts.update(s_tuple)
left_bars_values = [individual_counts[s] for s in symptoms_list]

all_combo_counts = Counter(patient_combinations).most_common()

COLOR_PRIMARY = '#2b5c8f'   
COLOR_DOT_EMPTY = '#f4f6f6' 
COLOR_BG_STRIPE = '#fbfcfc' 

# ==============================================================================
# ОКНО №1: ГОРИЗОНТАЛЬНЫЙ ГРАФИК (ТОП-20) + АВТОСОХРАНЕНИЕ
# ==============================================================================
plot_combos_top = all_combo_counts[:20]
num_display_top = len(plot_combos_top)

fig1 = plt.figure(figsize=(15, 8))
gs1 = fig1.add_gridspec(2, 2, width_ratios=[0.25, 0.75], height_ratios=[0.4, 0.6], wspace=0.12, hspace=0.02)

# Исправлено: Явно указаны квадратные скобки со срезами для gs1
ax_top_bar = fig1.add_subplot(gs1[0, 1])   
ax_matrix = fig1.add_subplot(gs1[1, 1], sharex=ax_top_bar) 
ax_left_bar = fig1.add_subplot(gs1[1, 0])  

top_values_top = [count for combo, count in plot_combos_top]
bars1 = ax_top_bar.bar(range(num_display_top), top_values_top, color=COLOR_PRIMARY, width=0.4, zorder=3)
ax_top_bar.set_ylabel('Пациентов в\nпересечении', fontsize=10, weight='bold')
ax_top_bar.grid(axis='y', linestyle=':', alpha=0.6, zorder=0)
ax_top_bar.spines['top'].set_visible(False)
ax_top_bar.spines['right'].set_visible(False)
ax_top_bar.tick_params(labelbottom=False, bottom=False)

for bar in bars1:
    ax_top_bar.annotate(f'{int(bar.get_height())}',
                        xy=(bar.get_x() + bar.get_width() / 2, 0),
                        xytext=(0, 6), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, weight='bold', color='white', rotation=90, zorder=4)

for y in range(num_symptoms):
    bg_color = COLOR_BG_STRIPE if y % 2 == 0 else 'white'
    ax_matrix.axhspan(y - 0.5, y + 0.5, facecolor=bg_color, zorder=0, alpha=0.5)

dot_size1 = max(90, min(150, 1200 / num_display_top))

for x, (combo, count) in enumerate(plot_combos_top):
    active_y_indices = [symptoms_list.index(s) for s in combo]
    inactive_y = [y for y in range(num_symptoms) if y not in active_y_indices]
    
    ax_matrix.scatter([x] * len(inactive_y), inactive_y, color=COLOR_DOT_EMPTY, s=dot_size1, alpha=0.5, zorder=2)
    if len(active_y_indices) > 1:
        ax_matrix.plot([x, x], [min(active_y_indices), max(active_y_indices)], color=COLOR_PRIMARY, linewidth=2.5, zorder=2)
    ax_matrix.scatter([x] * len(active_y_indices), active_y_indices, color=COLOR_PRIMARY, s=dot_size1 + 15, zorder=3)

ax_matrix.set_xlim(-0.5, num_display_top - 0.5)
ax_matrix.set_ylim(-0.5, num_symptoms - 0.5)
ax_matrix.axis('off')

y_pos1 = range(num_symptoms)
left_bars1 = ax_left_bar.barh(y_pos1, left_bars_values, color='#4a5568', height=0.4, zorder=3)
ax_left_bar.set_xlabel('Всего с симптомом\n(выборка: {})'.format(len(df)), fontsize=10, weight='bold')
ax_left_bar.set_yticks(y_pos1)
ax_left_bar.set_yticklabels(symptoms_list, fontsize=10, weight='bold')
ax_left_bar.invert_xaxis()  
ax_left_bar.grid(axis='x', linestyle=':', alpha=0.6, zorder=0)
ax_left_bar.spines['top'].set_visible(False)
ax_left_bar.spines['left'].set_visible(False)
ax_left_bar.spines['bottom'].set_visible(False)
ax_left_bar.set_ylim(-0.5, num_symptoms - 0.5)

for bar in left_bars1:
    ax_left_bar.annotate(f'{int(bar.get_width())} ', xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                        xytext=(-3, 0), textcoords="offset points", ha='right', va='center', fontsize=9, color='white', weight='bold')

plt.suptitle('Медицинский UpSet Plot: Топ-20 комбинаций', fontsize=14, weight='bold', y=0.97)
plt.savefig('upset_plot_top20.png', dpi=300, bbox_inches='tight')
print("💾 График Топ-20 сохранен в файл 'upset_plot_top20.png'")


# ==============================================================================
# ОКНО №2: ИСПРАВЛЕННЫЙ КОМПАКТНЫЙ ВЕРТИКАЛЬНЫЙ ГРАФИК (ВСЕ КОМБИНАЦИИ)
# ==============================================================================
plot_combos_all = all_combo_counts  
num_display_all = len(plot_combos_all)

# 1. Динамическая высота: увеличиваем коэффициент с 0.28 до 0.32 для достаточного интервала между строками
fig2_height = max(14, num_display_all * 0.32)
fig2 = plt.figure(figsize=(12, fig2_height))

gs2 = fig2.add_gridspec(2, 2, width_ratios=[0.40, 0.60], height_ratios=[0.05, 0.95], 
                      wspace=0.05, hspace=0.02)

ax_all_total_symptoms = fig2.add_subplot(gs2[0, 0])             
ax_all_matrix = fig2.add_subplot(gs2[1, 0], sharex=ax_all_total_symptoms) 
ax_all_side_bar = fig2.add_subplot(gs2[1, 1], sharey=ax_all_matrix)       

# --- 2.1 Серый верхний график ---
x_pos2 = range(num_symptoms)
total_symptom_bars = ax_all_total_symptoms.bar(x_pos2, left_bars_values, color='#7f8c8d', width=0.4, zorder=3)
ax_all_total_symptoms.set_ylabel('Всего с\nсимптомом', fontsize=8, weight='bold')
ax_all_total_symptoms.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
ax_all_total_symptoms.spines['top'].set_visible(False)
ax_all_total_symptoms.spines['right'].set_visible(False)
ax_all_total_symptoms.spines['bottom'].set_visible(False)
ax_all_total_symptoms.spines['left'].set_visible(False)
ax_all_total_symptoms.tick_params(labelbottom=False, bottom=False, left=False, labelleft=False)

for bar in total_symptom_bars:
    ax_all_total_symptoms.annotate(f'{int(bar.get_height())}', 
                                   xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                                   xytext=(0, 2), textcoords="offset points", 
                                   ha='center', va='bottom', fontsize=8, weight='bold', color='#4f5b66')

# --- 2.2 Левая компактная матрица точек ---
ax_all_matrix.set_ylim(num_display_all - 0.5, -0.5)

for x in range(num_symptoms):
    bg_color = COLOR_BG_STRIPE if x % 2 == 0 else 'white'
    ax_all_matrix.axvspan(x - 0.5, x + 0.5, facecolor=bg_color, zorder=0, alpha=0.5)

dot_size2 = 45 

for y, (combo, count) in enumerate(plot_combos_all):
    active_x_indices = [symptoms_list.index(s) for s in combo]
    inactive_x = [x for x in range(num_symptoms) if x not in active_x_indices]
    
    ax_all_matrix.scatter(inactive_x, [y] * len(inactive_x), color=COLOR_DOT_EMPTY, s=dot_size2, alpha=0.4, zorder=2)
    if len(active_x_indices) > 1:
        ax_all_matrix.plot([min(active_x_indices), max(active_x_indices)], [y, y], color=COLOR_PRIMARY, linewidth=1.8, zorder=2)
    ax_all_matrix.scatter(active_x_indices, [y] * len(active_x_indices), color=COLOR_PRIMARY, s=dot_size2 + 10, zorder=3)

ax_all_matrix.set_xlim(-0.5, num_symptoms - 0.5)

# Подписи симптомов снизу матрицы
ax_all_matrix.set_xticks(range(num_symptoms))
ax_all_matrix.set_xticklabels(symptoms_list, fontsize=10, weight='bold', rotation=45, ha='right')
ax_all_matrix.tick_params(axis='x', bottom=True, labelbottom=True)

ax_all_matrix.spines['top'].set_visible(False)
ax_all_matrix.spines['right'].set_visible(False)
ax_all_matrix.spines['left'].set_visible(False)
ax_all_matrix.spines['bottom'].set_visible(False)
ax_all_matrix.tick_params(axis='y', left=False, labelleft=False)

# --- 2.3 Правый блок: горизонтальные столбцы и понятные подписи ---
all_values = [count for combo, count in plot_combos_all]
side_bars = ax_all_side_bar.barh(range(num_display_all), all_values, color=COLOR_PRIMARY, height=0.7, zorder=3)
ax_all_side_bar.set_xlabel('Пациентов в комбинации', fontsize=10, weight='bold')
ax_all_side_bar.grid(axis='x', linestyle=':', alpha=0.6, zorder=0)

ax_all_side_bar.spines['top'].set_visible(False)
ax_all_side_bar.spines['right'].set_visible(False)
ax_all_side_bar.spines['bottom'].set_visible(False)
ax_all_side_bar.spines['left'].set_visible(False)
ax_all_side_bar.tick_params(labelleft=False, left=False) 

max_val = max(all_values)

# 2. Запас 15% по оси X, чтобы значения за пределами столбцов не выходили за границы рисунка
ax_all_side_bar.set_xlim(0, max_val * 1.15)  

# 3. Отступ подписи от конца столбца (1.5% от max_val)
label_offset = max_val * 0.015

# 4. Адаптивный размер шрифта в зависимости от количества строк
font_size = max(6, min(9, 250 / num_display_all))

# 5. Вывод чисел строго справа от каждого столбца на белом фоне (ha='left')
for bar in side_bars:
    width = bar.get_width()
    ax_all_side_bar.annotate(
        f'{int(width)}',
        xy=(width + label_offset, bar.get_y() + bar.get_height() / 2),
        ha='left', va='center',
        fontsize=font_size, weight='bold', color='#2c3e50', zorder=4
    )

plt.suptitle('Вертикальный UpSet Plot: Распределение всех {} комбинаций датасета'.format(num_display_all), 
             fontsize=12, weight='bold', y=0.99)

# Сохранение и вывод на экран
plt.savefig('upset_plot_all_vertical.png', dpi=300, bbox_inches='tight')
print(" Вертикальный график всех фич сохранен в файл 'upset_plot_all_vertical.png'")

plt.show()