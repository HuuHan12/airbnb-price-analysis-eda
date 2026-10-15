"""Build the single presentation notebook from reviewed project code and metadata.

The emitted notebook contains its implementation; no src imports, runpy or exec.
This script is only needed when changing the notebook's source, not to run it.
"""
import ast
import hashlib
import json
from pathlib import Path

import nbformat as nbf
import pandas as pd
from final_han_sections import HAN_SECTIONS

ROOT = Path(__file__).resolve().parents[1]
cells = []
original_config = json.loads((ROOT / 'config/experiment_config.json').read_text(encoding='utf-8'))
embedded_config = {k: original_config[k] for k in [
    'protocol_id', 'data_sha256', 'target', 'trace_keys', 'predictors',
    'slr_feature', 'polynomial_features', 'polynomial_degrees', 'ridge_alphas',
    'excluded_predictors', 'encoding', 'selection_metric']}
reference_manifest = pd.read_csv(ROOT / 'data/processed/split_manifest.csv')
manifest_digest = hashlib.sha256(reference_manifest.to_csv(index=False, lineterminator='\n').encode('utf-8')).hexdigest()


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))


def functions(module, names):
    source = (ROOT / 'src' / module).read_text(encoding='utf-8')
    tree = ast.parse(source)
    found = {n.name: ast.get_source_segment(source, n) for n in tree.body
             if isinstance(n, ast.FunctionDef)}
    return '\n\n\n'.join(found[name] for name in names)


md('''# IE313 — Phân tích giá Airbnb tại 10 thành phố châu Âu

**Notebook trình bày toàn bộ đồ án — Hàn (A) và Huy (B).**

Mục tiêu: mô tả phân phối giá, so sánh thành phố/loại phòng/hai nhóm ngày,
khảo sát liên hệ với các thuộc tính và so sánh năm mô hình hồi quy trên cùng giao thức.
Phân tích giúp giải thích vì sao chỉ nhìn giá trung bình hoặc một hệ số tương quan là chưa đủ,
và kiểm tra mức sai số của mô hình trên các quan sát được giữ riêng.

Phạm vi là dữ liệu gộp từ 20 CSV đã có của nhóm; không bổ sung dữ liệu hay mô hình ngoài kế hoạch.
Nguồn dữ liệu được README ghi là Kaggle / The Devastator. `realSum` giữ nguyên thang giá:
EUR **theo README**, kỳ giá chưa xác minh metadata gốc; không diễn giải thành giá mỗi đêm.
AI hỗ trợ viết code và bản thảo; hai thành viên cần hiểu, kiểm tra và khai báo công cụ thực tế.

**Bộ code/data nộp gồm đúng hai file:** notebook này và `airbnb_combined.csv`, đặt cùng thư mục.
Mở notebook bằng Jupyter hoặc VS Code với thư mục làm việc tại đó, chọn **Restart Kernel and Run All**.
Không cần JSON, manifest CSV, 20 CSV nguồn, `src`, model hoặc output đã có. Notebook không tự tải mạng
và không ghi file trung gian. Code kiểm dữ liệu,
chia tập, EDA, xây dựng Pipeline, CV, dự đoán và phần dư đều nằm trong notebook;
không cần chạy các notebook khác hoặc import `src`.
Môi trường đã kiểm: Python 3.12; numpy 2.5.4, pandas 3.0.6, scipy 1.18.1,
matplotlib 3.11.2, seaborn 0.13.2, scikit-learn 1.9.1 và ipykernel 7.4.0.
Nếu chưa có thư viện, dùng `%pip install numpy==2.5.4 pandas==3.0.6 scipy==1.18.1 matplotlib==3.11.2 seaborn==0.13.2 scikit-learn==1.9.1 ipykernel==7.4.0`
trong một cell riêng, rồi khởi động lại kernel; lệnh này không tự chạy khi mở notebook.
Khi demo, dùng các output đã chạy; không dành thời gian thuyết trình cho việc huấn luyện lại.

Trình tự: 1. Nguồn và kiểm dữ liệu → 2. EDA/Pearson/ANOVA → 3. Giao thức và hồi quy
→ 4. Đánh giá holdout → 5. Phần dư và kết luận → 6. Phân công và cách kiểm tra.
''')
md('''## 1. Nguồn, từ điển và hiện trạng dữ liệu — Hàn, Huy kiểm tra

Nạp CSV gộp giữ đủ 20 cột gốc và bốn cột `city`, `day_type`, `source_file`, `source_row`.
Khóa file/dòng giúp quay lại dữ liệu gốc; `Unnamed: 0` và tọa độ không phải listing ID.
Inventory dưới đây tổng hợp theo `source_file` từ CSV gộp; lượt chạy bản nộp không đọc lại 20 file gốc.
Hash xác minh đúng snapshot dùng khi chốt mô hình; không cần file JSON bên ngoài để kiểm.
''')
code('''from pathlib import Path
import hashlib, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown, JSON
from scipy.stats import pearsonr, f_oneway
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import KFold, train_test_split, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

ROOT = Path.cwd()
DATA_PATH = ROOT / 'airbnb_combined.csv'
if not DATA_PATH.is_file():
    raise FileNotFoundError(f'Thiếu airbnb_combined.csv trong {ROOT}. '
                            'Đặt CSV cạnh notebook và mở kernel tại thư mục đó.')
pd.set_option('display.max_columns', 24)
pd.set_option('display.float_format', lambda x: f'{x:,.4f}')
sns.set_theme(style='whitegrid', font='DejaVu Sans')
print('Thư mục chứa bộ hai file:', ROOT)
print('Python:', sys.version.split()[0])
''')
code('''# Cấu hình đóng băng từ giao thức đã review; không đọc JSON/manifest ngoài.
config = ''' + repr(embedded_config) + '''
hash_now = hashlib.sha256(DATA_PATH.read_bytes().replace(b'\\r\\n', b'\\n')).hexdigest()
if hash_now != config['data_sha256']:
    raise ValueError('CSV không khớp snapshot đã chốt; hãy dùng nguyên file airbnb_combined.csv đi kèm.')
df = pd.read_csv(DATA_PATH)
original_columns = ''' + repr(pd.read_csv(ROOT / 'data/processed/airbnb_combined.csv', nrows=0).columns.tolist()[:20]) + '''
assert df.columns.tolist() == original_columns + ['city', 'day_type', 'source_file', 'source_row']
inventory_rows = []
for name, part in df.groupby('source_file', sort=True):
    city, day = Path(name).stem.rsplit('_', 1)
    assert day in ['weekdays', 'weekends']
    assert part.city.eq(city).all() and part.day_type.eq(day).all()
    assert part.source_row.eq(part['Unnamed: 0']).all()
    inventory_rows.append({'file': name, 'n': len(part), 'original_columns': len(original_columns),
                           'missing_cells': int(part.isna().sum().sum())})
inventory = pd.DataFrame(inventory_rows)
assert df.shape == (51707, 24)
assert len(inventory) == 20 and inventory.n.sum() == len(df)
assert df.city.nunique() == 10
assert df.groupby(['city', 'day_type']).size().shape[0] == 20
display(inventory)
print('Dữ liệu gộp:', df.shape)
''')
dictionary = pd.read_csv(ROOT / 'outputs/tables/data_dictionary.csv').fillna('')
dictionary = dictionary[dictionary.column_name.isin([
    *pd.read_csv(ROOT / 'data/processed/airbnb_combined.csv', nrows=0).columns])]
code('''# Từ điển do nhóm đã review ở T03; nhúng trong notebook, không đọc bảng output cũ.
dictionary = pd.DataFrame(''' + repr(dictionary.to_dict('records')) + ''')
assert set(dictionary.column_name) == set(df.columns)
display(dictionary[['column_name', 'data_type', 'description_vi', 'metadata_status', 'usage_note']])
''')
md('''### 1.1. Vì sao cần kiểm dữ liệu trước khi phân tích?

Không có ô khuyết chưa đủ chứng minh dữ liệu đúng. Cần kiểm giá hữu hạn/dương,
miền thuộc tính, logic cờ loại phòng, khóa truy vết và tọa độ lặp. Không tạo giá trị khuyết giả
hoặc điền khuyết khi không cần. `bedrooms=0` là giá trị quan sát; chưa xác nhận là studio.
Ý nghĩa chi tiết `multi`, `biz`, các index và hệ tọa độ chưa được metadata gốc xác minh.
''')
code('''hidden_nulls = sum(int(df[c].astype(str).str.strip().str.lower().isin(
    ['', '?', '.', 'none', 'null', 'n/a', 'na', 'nan']).sum())
    for c in df.select_dtypes(include=['object', 'str']).columns)
checks = {
    'missing_cells': int(df.isna().sum().sum()),
    'hidden_null_markers': hidden_nulls,
    'nonfinite_numeric_cells': int((~np.isfinite(df.select_dtypes(include='number'))).sum().sum()),
    'nonpositive_prices': int((~df.realSum.gt(0)).sum()),
    'duplicate_trace_keys': int(df.duplicated(['source_file', 'source_row']).sum()),
    'invalid_room_type': int((~df.room_type.isin(['Entire home/apt', 'Private room', 'Shared room'])).sum()),
    'room_shared_mismatch': int((df.room_shared != df.room_type.eq('Shared room')).sum()),
    'room_private_mismatch': int((df.room_private != df.room_type.eq('Private room')).sum()),
    'invalid_boolean_flags': sum(int((~df[c].isin([True, False])).sum())
                                 for c in ['room_shared', 'room_private', 'host_is_superhost']),
    'invalid_capacity': int((~(df.person_capacity.ge(1) & df.person_capacity.mod(1).eq(0))).sum()),
    'invalid_bedrooms': int((~(df.bedrooms.ge(0) & df.bedrooms.mod(1).eq(0))).sum()),
    'negative_distances': int((df[['dist', 'metro_dist']] < 0).sum().sum()),
    'invalid_coordinate_range': int((~(df.lat.between(-90, 90) & df.lng.between(-180, 180))).sum()),
}
display(pd.Series(checks, name='Số vi phạm').to_frame())
assert not any(checks.values())
print('Dòng trùng toàn bộ 20 cột gốc:', df.duplicated(original_columns).sum())
print('Tọa độ city/lat/lng lặp sau lần đầu:', df.duplicated(['city', 'lat', 'lng']).sum())
print('Min metro_dist quan sát:', df.metro_dist.min())
display(df.select_dtypes(include='number').describe().T)
''')
md('''### 1.2. Phân phối, IQR và quyết định giữ giá gốc

Mean, median, độ lệch chuẩn và skew mô tả các mặt khác nhau của phân phối. IQR gắn cờ
quan sát nằm ngoài `[Q1−1,5IQR; Q3+1,5IQR]`; kiểm cả gộp và từng city vì mặt bằng giá khác nhau.
Cờ IQR không chứng minh giá sai hay nhà sang trọng. Giữ nguyên các quan sát cho mọi mô hình;
không cắt đuôi test để giảm lỗi. Trục log chỉ giúp đọc hình, không biến đổi target hồi quy.
''')
code('''def iqr_row(frame):
    price = frame.realSum
    q1, q3 = price.quantile([.25, .75])
    lower, upper = q1 - 1.5*(q3-q1), q3 + 1.5*(q3-q1)
    return {'n': len(frame), 'mean': price.mean(), 'median': price.median(),
            'std': price.std(), 'skew': price.skew(), 'max': price.max(),
            'lower_fence': lower, 'upper_fence': upper,
            'flagged': int((price.lt(lower) | price.gt(upper)).sum())}
price_audit = pd.DataFrame([{'scope': 'all_cities', **iqr_row(df)}] +
                          [{'scope': city, **iqr_row(g)} for city, g in df.groupby('city')])
display(price_audit)
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(df.realSum, bins=70)
axes[0].set(title='Giá gốc: giữ toàn bộ quan sát', xlabel='realSum', ylabel='Count')
axes[1].hist(np.log10(df.realSum), bins=70)
axes[1].set(title='Phân phối log10 để đọc hình', xlabel='log10(realSum)', ylabel='Count')
plt.tight_layout(); plt.show()
''')
md('''### 1.3. Binning mô tả theo phần tiền xử lý đã có

Giữ các ngưỡng nhóm đã dùng trong Notebook 01: khoảng cách 0/1/3/5 km và giá 0/150/350/600.
Khoảng có cận trái đóng, cận phải mở. Đây là quy ước của nhóm để đọc bảng, chưa xác nhận
phân khúc thị trường. `price_tier` dẫn xuất trực tiếp từ target, chỉ dùng mô tả, không vào predictor.
Các cột này tạo trên bản sao riêng để dữ liệu cho mô hình vẫn đúng 24 cột.
''')
code('''descriptive = df.copy()
descriptive['dist_bin'] = pd.cut(descriptive.dist, [0, 1, 3, 5, np.inf],
                                labels=['[0,1)', '[1,3)', '[3,5)', '[5,+inf)'], right=False)
descriptive['price_tier'] = pd.cut(descriptive.realSum, [0, 150, 350, 600, np.inf],
                                  labels=['[0,150)', '[150,350)', '[350,600)', '[600,+inf)'], right=False)
assert not descriptive[['dist_bin', 'price_tier']].isna().any().any()
display(descriptive.groupby('dist_bin', observed=False).realSum.agg(n='size', mean='mean', median='median'))
display(pd.crosstab(descriptive.dist_bin, descriptive.price_tier, margins=True))
assert df.shape == (51707, 24)
''')
md('''**Điểm mạnh:** nhiều quan sát, schema đồng nhất, đủ hai nhóm ngày ở mỗi city, có khóa
file/dòng để kiểm lại và không cần imputation trong snapshot này.

**Điểm yếu:** mẫu loại phòng mất cân đối; giá lệch mạnh; thiếu kỳ thu thập và listing ID;
tọa độ lặp chưa rõ nguyên nhân; định nghĩa một số biến chưa chắc chắn.
Vì vậy cần báo cả n/median/IQR bên cạnh mean, so sánh trong city/room, giữ ngoại lệ và
phân tích lỗi theo nhóm. Kết quả áp dụng cho dữ liệu cung cấp, không đại diện chắc chắn toàn thị trường.
''')
md('''## 2. EDA và bằng chứng liên hệ — Huy, Hàn kiểm tra

**Q1:** giá và số mẫu khác nhau thế nào theo city/room? **Q2:** hai nhóm ngày có khác nhau,
và chênh lệch có đi kèm khác cơ cấu phòng? **Q3:** liên hệ tuyến tính của thuộc tính với giá
gộp và trong từng city? **Q4:** mean giá khác nhau theo nhóm trong ANOVA, với giới hạn gì?

Trước EDA, dùng allowlist cố định và tái tạo split đã chốt để tách bảng full/train. EDA không dùng để
tự động chọn biến theo r/p trên toàn bộ dữ liệu.
''')
code('''# Giữ nguyên thuật toán, thứ tự dòng và seed 0; tái tạo trong bộ nhớ.
expected_train, expected_test = train_test_split(np.arange(len(df)), test_size=.2, random_state=0)
expected_train = np.sort(expected_train)
manifest = df[config['trace_keys']].copy()
manifest['split'], manifest['cv_fold'] = 'test', -1
manifest.loc[expected_train, 'split'] = 'train'
for fold, (_, valid_pos) in enumerate(KFold(5, shuffle=True, random_state=0).split(expected_train)):
    manifest.loc[expected_train[valid_pos], 'cv_fold'] = fold
manifest_hash = hashlib.sha256(manifest.to_csv(index=False, lineterminator='\\n').encode('utf-8')).hexdigest()
assert manifest_hash == ''' + repr(manifest_digest) + ''', 'Split/fold khác bản đã chốt'
assert np.array_equal(np.flatnonzero(manifest.split.eq('train')), expected_train)
assert np.array_equal(np.flatnonzero(manifest.split.eq('test')), np.sort(expected_test))
assert manifest.loc[manifest.split.eq('test'), 'cv_fold'].eq(-1).all()
train = df.loc[manifest.split.eq('train')].reset_index(drop=True)
test = df.loc[manifest.split.eq('test')].reset_index(drop=True)
train_folds = manifest.loc[manifest.split.eq('train'), 'cv_fold'].to_numpy()
cv = [(np.flatnonzero(train_folds != fold), np.flatnonzero(train_folds == fold)) for fold in range(5)]
for fold, (fit_idx, valid_idx) in enumerate(KFold(5, shuffle=True, random_state=0).split(train)):
    assert np.array_equal(cv[fold][0], fit_idx) and np.array_equal(cv[fold][1], valid_idx)
assert len(train) == 41365 and len(test) == 10342
assert set(train_folds) == set(range(5))
display(pd.DataFrame([{'fold': f, 'fit': len(a), 'validation': len(b)} for f, (a,b) in enumerate(cv)]))
''')
code(functions('experiment.py', ['predictor_names']))
code('''# Lưu bảng trong bộ nhớ; không ghi/đọc file trung gian.
tables = {}
LIMIT = ('Mô tả liên hệ, không nhân quả; giá lệch phải/nhóm mất cân đối, '
         'độc lập mẫu chưa xác minh do tọa độ lặp; p nhỏ không đo độ lớn tác động.')
def save_table(frame, name, root=ROOT):
    tables[name] = frame.copy()
    return name

''' + functions('b_tasks.py', ['price_summary', 'build_eda_tables']))
code('''group_summary, sampling, city_pairs = build_eda_tables(df)
display(group_summary.loc[group_summary.grouping.eq('city'), ['city', 'n', 'mean', 'median', 'iqr']])
display(group_summary.loc[group_summary.grouping.eq('room_type'), ['room_type', 'n', 'mean', 'median', 'iqr']])
display(city_pairs[['city', 'n_weekdays', 'n_weekends', 'median_weekdays', 'median_weekends',
                    'median_difference_weekends_minus_weekdays']])
display(tables['eda_day_comparison_by_room.csv'])
''')
md('''### 2.1. Biểu đồ nhóm và cơ cấu mẫu

Đọc count trước khi so sánh giá. Shared room có ít quan sát; tổ hợp không có mẫu có n=0,
giá giữ NaN thay vì điền 0. Chênh weekdays/weekends là hai tập quan sát, không ghép cặp cùng phòng.
Phân nhóm theo loại phòng giúp kiểm tra cơ cấu, chưa đủ để kết luận tác động nhân quả của cuối tuần.
''')
code('''fig, axes = plt.subplots(1, 2, figsize=(14, 5))
city_counts = df.city.value_counts().sort_values()
city_counts.plot.barh(ax=axes[0], color='#315776')
axes[0].set(title='Số mẫu theo city', xlabel='Count')
sns.boxplot(data=df, x='room_type', y='realSum', ax=axes[1], showfliers=True)
axes[1].set_yscale('log')
axes[1].set(title='Giá theo phòng, giữ ngoại lệ', ylabel='realSum — trục log')
plt.tight_layout(); plt.show()
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
city_day = group_summary.loc[group_summary.grouping.eq('city+day_type')]
sns.barplot(data=city_day, x='city', y='median', hue='day_type', errorbar=None, ax=axes[0])
axes[0].tick_params(axis='x', rotation=40)
axes[0].set(title='Median giá của hai nhóm ngày', ylabel='realSum')
shares = sampling.pivot(index=['city', 'day_type'], columns='room_type', values='share_of_city_day')
shares.plot.bar(stacked=True, ax=axes[1], width=.85)
axes[1].set(title='Cơ cấu loại phòng theo city/ngày', ylabel='Tỷ lệ mẫu')
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
''')
code(functions('b_tasks.py', ['p_fields', 'build_evidence']))
code('''pearson, anova, corr = build_evidence(df, train, config)
display(pearson.loc[(pearson.scope == 'full_descriptive') & (pearson.context == 'all_cities'),
                    ['feature', 'n', 'r', 'p_display', 'used_in_core_model']])
display(pearson.loc[(pearson.scope == 'full_descriptive') & (pearson.feature == 'person_capacity'),
                    ['context', 'n', 'r', 'p_display']])
display(anova.loc[(anova.scope == 'full_descriptive') & (anova.context == 'all_cities'),
                  ['feature', 'n', 'min_group_n', 'f', 'p_display', 'variance_ratio_max_min']])
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.heatmap(corr, cmap='vlag', center=0, vmin=-1, vmax=1, ax=axes[0])
axes[0].set(title='Tương quan Pearson: full descriptive')
axes[1].scatter(df.person_capacity, df.realSum, s=4, alpha=.12)
axes[1].set(xlabel='person_capacity', ylabel='realSum', title='Scatter: toàn bộ quan sát')
plt.tight_layout(); plt.show()
''')
md('''### 2.2. Diễn giải Pearson/ANOVA và vì sao không lọc biến máy móc

Pearson đo liên hệ tuyến tính, nhạy với giá lớn và việc gộp city; r gộp nhỏ không bác bỏ
liên hệ trong từng city. ANOVA kiểm khác biệt mean giữa nhóm, không chứng minh mọi cặp khác
nhau hay mức tác động lớn. Giá lệch, nhóm mất cân đối và tính độc lập chưa xác minh làm
giới hạn giả định kiểm định. p underflow được ghi rõ, không gọi xác suất chính xác bằng 0.

Giữ predictor theo ý nghĩa/metadata đã chốt; r/p/F là bằng chứng mô tả. Không áp ngưỡng
Pearson của bài tập giá xe để loại hết biến Airbnb. Tất cả bảng full/train được phân biệt.
''')
md('''## 3. Giao thức và năm mô hình hồi quy — Hàn M0–M2, Huy M3–M4

**41.365 train / 10.342 test**, seed 0, 5-fold CV trong train. Mỗi fold gồm 33.092 fit và
8.273 validation. So sánh cùng fold, target giá gốc và MSE CV trung bình.
Scaler/OneHot/Polynomial nằm trong Pipeline, được fit trong từng fold.

10 predictor gốc: sáu biến số, ba biến phân loại, một cờ Superhost. Không dùng ID,
log giá/price tier, cờ room trùng thông tin, metadata chưa chắc chắn hoặc tọa độ trong core.
`dist_bin` là dẫn xuất từ khoảng cách, được bỏ do dư thừa theo giao thức, không phải biến dẫn xuất từ target.

M0: trung bình train (mốc so sánh); M1: tuyến tính sức chứa; M2: tuyến tính đa biến;
M3: đa thức bậc 2/3 chỉ trên capacity/bedrooms/dist; M4: Ridge với bảy alpha đã định.
M2/M4 có 19 cột sau encoding; M3 bậc 2 có 25, bậc 3 có 35 cột. Chọn biến thể và mô hình
bằng CV trước phần đánh giá test. Test đã được mở ở T10 trước đây; lượt này tái lập giao thức
đã chốt, không giả vờ có một holdout mới chưa từng xem.
''')
code(functions('experiment.py', ['build_pipeline', 'evaluate_cv']))
code('''X_train, y_train = train[predictor_names(config)], train[config['target']]
specs = [('M0', 'mean_baseline', {}), ('M1', 'slr_person_capacity', {}), ('M2', 'mlr_core', {})]
specs += [('M3', f'degree_{d}', {'degree': d}) for d in config['polynomial_degrees']]
specs += [('M4', f'alpha_{a:g}', {'alpha': a}) for a in config['ridge_alphas']]
cv_rows, fold_rows = [], []
for model_id, variant, params in specs:
    pipeline = build_pipeline(model_id, config, **params)
    summary, detail = evaluate_cv(pipeline, train, cv, config, model_id, variant)
    cv_rows.append({**summary, **params})
    fold_rows.append(detail)
    print(model_id, variant, 'CV MSE =', round(summary['cv_mse_mean'], 2))
cv_summary = pd.DataFrame(cv_rows)
cv_folds = pd.concat(fold_rows, ignore_index=True)
assert len(cv_summary) == 12 and len(cv_folds) == 60
display(cv_summary[['model_id', 'variant', 'fold_train_mse_mean', 'cv_mse_mean',
                    'cv_mse_std', 'cv_rmse_mean', 'cv_mae_mean', 'cv_r2_mean']])
save_table(cv_summary, 'all_configurations_cv.csv')
save_table(cv_folds, 'all_configurations_folds.csv')
''')
md('''`cross_validate` gọi điểm validation là `test_*`; hàm đã đổi tên để không nhầm holdout.
MSE/MAE scorer có dấu âm được đổi về dương, R² giữ nguyên. Mean RMSE của folds không nhất
thiết bằng căn mean MSE. Chênh train/CV phản ánh sai số trong cấu hình này; chưa đủ để
tuyên bố chắc chắn mô hình không overfit.
''')
code('''selected_cv = cv_summary.loc[cv_summary.groupby('model_id').cv_mse_mean.idxmin()].copy()
winner_id = selected_cv.loc[selected_cv.cv_mse_mean.idxmin(), 'model_id']
selected_cv['selected_winning_model'] = selected_cv.model_id.eq(winner_id)
models = {}
for row in selected_cv.itertuples():
    params = {'degree': int(row.degree)} if row.model_id == 'M3' else (
             {'alpha': float(row.alpha)} if row.model_id == 'M4' else {})
    model = build_pipeline(row.model_id, config, **params)
    model.fit(X_train, y_train)  # Refit chỉ toàn bộ train sau chọn CV.
    models[row.model_id] = model
display(selected_cv[['model_id', 'variant', 'cv_mse_mean', 'selected_winning_model']])
print('Mô hình khóa bằng CV:', winner_id)
assert winner_id == 'M3'
assert int(selected_cv.loc[selected_cv.model_id.eq('M3'), 'degree'].iloc[0]) == 3
assert float(selected_cv.loc[selected_cv.model_id.eq('M4'), 'alpha'].iloc[0]) == .1
''')
md('''### 3.1. Phương trình và hệ số tuyến tính để giải thích code

M1 dùng sức chứa trên đơn vị gốc. Intercept là giá trị của phương trình tại capacity=0,
không gọi là giá sàn. M2 chuẩn hóa biến số: hệ số tương ứng tăng một độ lệch chuẩn khi
giữ các predictor khác cố định; chia hệ số cho scale để đọc theo đơn vị gốc.
Dummy so với nhóm tham chiếu được in ra. Hệ số là liên hệ trong mô hình, không chứng minh nhân quả.
''')
code('''m1 = models['M1'].named_steps['model']
print(f'M1: realSum_hat = {m1.intercept_:.4f} + {m1.coef_[0]:.4f} * person_capacity')
m2 = models['M2']
names = m2.named_steps['preprocess'].get_feature_names_out()
coefficients = pd.DataFrame({'feature': names, 'coefficient': m2.named_steps['model'].coef_})
coefficients['coefficient_per_original_unit'] = np.nan
scaler = m2.named_steps['preprocess'].named_transformers_['numeric']
coefficients.loc[coefficients.feature.str.startswith('numeric__'), 'coefficient_per_original_unit'] = (
    coefficients.loc[coefficients.feature.str.startswith('numeric__'), 'coefficient'].to_numpy() / scaler.scale_)
print('M2 intercept trên biểu diễn đã biến đổi:', m2.named_steps['model'].intercept_)
encoder = m2.named_steps['preprocess'].named_transformers_['categorical']
print('Nhóm tham chiếu:', {name: categories[0] for name, categories in
                            zip(config['predictors']['categorical'], encoder.categories_)})
display(coefficients)
for model_id in ['M2', 'M3', 'M4']:
    print(model_id, 'số cột sau encoding:', models[model_id].named_steps['preprocess'].transform(X_train.iloc[:1]).shape[1])
''')
md('''## 4. Đánh giá holdout chung — Hàn và Huy

Chỉ predict từ các model đã refit train. MSE = mean((actual−predicted)²), RMSE = sqrt(MSE),
MAE = mean(|actual−predicted|), R² = 1−SSE/SST. Không tune bậc/alpha/split/biến sau test.
MSE có đơn vị bình phương; RMSE/MAE cùng đơn vị với realSum; R² không phải phần trăm accuracy.
''')
code('''X_test, y_test = test[predictor_names(config)], test[config['target']]
comparison_rows, prediction_frames = [], []
for row in selected_cv.itertuples():
    predicted = models[row.model_id].predict(X_test)
    mse = mean_squared_error(y_test, predicted)
    comparison_rows.append({'model_id': row.model_id, 'variant': row.variant,
        'protocol_id': config['protocol_id'], 'n_train': len(train), 'n_test': len(test),
        'cv_mse_mean': row.cv_mse_mean, 'cv_rmse_mean': row.cv_rmse_mean,
        'cv_mae_mean': row.cv_mae_mean, 'cv_r2_mean': row.cv_r2_mean,
        'test_mse': mse, 'test_rmse': np.sqrt(mse),
        'test_mae': mean_absolute_error(y_test, predicted), 'test_r2': r2_score(y_test, predicted),
        'selected_winning_model': row.model_id == winner_id})
    part = test.copy()
    part['actual'], part['predicted'] = y_test.to_numpy(), predicted
    part['residual'] = part.actual - part.predicted
    part['model_id'], part['split'], part['protocol_id'] = row.model_id, 'test', config['protocol_id']
    prediction_frames.append(part)
comparison = pd.DataFrame(comparison_rows)
predictions = pd.concat(prediction_frames, ignore_index=True)
assert len(predictions) == 5 * 10342
assert not predictions.duplicated(['model_id', 'source_file', 'source_row']).any()
display(comparison[['model_id', 'variant', 'cv_mse_mean', 'test_mse', 'test_rmse', 'test_mae',
                    'test_r2', 'selected_winning_model']])
save_table(comparison, 'model_comparison.csv')
save_table(predictions, 'test_predictions.csv')
fig, ax = plt.subplots(figsize=(9, 4))
comparison.set_index('model_id')[['cv_mse_mean', 'test_mse']].plot.bar(ax=ax)
ax.set(title='Cùng thang giá và giao thức', ylabel='MSE')
plt.tight_layout(); plt.show()
''')
md('''## 5. Phần dư, lỗi theo nhóm và kết luận — Huy, Hàn kiểm tra

Residual = actual−predicted: dương nghĩa là dự đoán thấp. Phân tích mô hình đã khóa bằng CV.
Giữ dự đoán âm để phản ánh giới hạn; không clip sau khi nhìn test. Báo lỗi kèm số mẫu từng nhóm.
Các case sai số lớn được truy lại file/dòng, không gọi là gian lận hoặc giá sai.
''')
code('''winner = predictions.loc[predictions.model_id.eq(winner_id)].copy()
assert len(winner) == 10342
pd.testing.assert_frame_equal(winner[config['trace_keys']].reset_index(drop=True), test[config['trace_keys']])
np.testing.assert_allclose(winner.actual, test.realSum, rtol=0, atol=0)
winner['abs_residual'] = winner.residual.abs()
winner['squared_residual'] = winner.residual ** 2
def group_error(frame):
    return {'n': len(frame), 'rmse': np.sqrt(frame.squared_residual.mean()),
            'mae': frame.abs_residual.mean(), 'mean_residual': frame.residual.mean(),
            'negative_predictions': int(frame.predicted.lt(0).sum())}
error_rows = []
for cols in [['city'], ['room_type'], ['day_type'], ['city', 'room_type']]:
    for key, part in winner.groupby(cols, observed=True):
        keys = key if isinstance(key, tuple) else (key,)
        error_rows.append({'grouping': '+'.join(cols), **dict(zip(cols, keys)), **group_error(part)})
group_errors = pd.DataFrame(error_rows)
display(group_errors.loc[group_errors.grouping.isin(['city', 'room_type', 'day_type'])])
save_table(group_errors, 'residual_group_errors.csv')
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].scatter(winner.predicted, winner.residual, s=5, alpha=.2)
axes[0].axhline(0, color='red')
axes[0].set(xlabel='Predicted', ylabel='Actual − predicted', title=f'{winner_id}: toàn bộ holdout')
axes[1].scatter(winner.actual, winner.predicted, s=5, alpha=.2)
low, high = min(winner.actual.min(), winner.predicted.min()), max(winner.actual.max(), winner.predicted.max())
axes[1].plot([low, high], [low, high], color='red')
axes[1].set(xlabel='Actual', ylabel='Predicted', title='Đường chéo: actual = predicted')
plt.tight_layout(); plt.show()
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, col in zip(axes, ['city', 'room_type']):
    part = group_errors.loc[group_errors.grouping.eq(col)].sort_values('rmse')
    ax.barh([f'{r[col]} (n={int(r["n"])})' for _,r in part.iterrows()], part.rmse)
    ax.set(xlabel='RMSE', title=f'Lỗi theo {col}, kèm n')
plt.tight_layout(); plt.show()
''')
code('''ordered = winner.sort_values('squared_residual', ascending=False)
top_n = int(np.ceil(len(winner)*.01))
top_share = ordered.head(top_n).squared_residual.sum()/winner.squared_residual.sum()
cases = ordered.head(10)[['source_file', 'source_row', 'city', 'room_type', 'person_capacity',
                          'bedrooms', 'dist', 'actual', 'predicted', 'residual']]
display(cases)
save_table(cases, 'residual_cases.csv')
case = cases.iloc[0]
raw_case = df.loc[df.source_file.eq(case.source_file) & df.source_row.eq(case.source_row)]
assert len(raw_case) == 1
np.testing.assert_allclose(raw_case.realSum.iloc[0], case.actual, rtol=0, atol=0)
display(raw_case)
print('Đã đối chiếu case trong CSV gộp qua khóa file/dòng; bản nộp không mở lại CSV nguồn.')
print(f'{top_n} dòng lỗi bình phương lớn nhất ({top_n/len(winner):.2%} mẫu) chiếm {top_share:.2%} SSE.')
print('Số dự đoán âm:', winner.predicted.lt(0).sum())
print('Mean residual:', winner.residual.mean(), '| Median AE:', winner.abs_residual.median(),
      '| P90 AE:', winner.abs_residual.quantile(.9))
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(np.arange(1, len(ordered)+1)/len(ordered)*100,
        ordered.squared_residual.cumsum()/ordered.squared_residual.sum()*100)
ax.set(xlabel='% dòng, xếp theo lỗi bình phương giảm dần', ylabel='% SSE lũy tích',
       title='Mức tập trung sai số; giữ nguyên mọi dòng test', xlim=(0,100), ylim=(0,100))
plt.tight_layout(); plt.show()
''')
code('''selected = comparison.loc[comparison.model_id.eq(winner_id)].iloc[0]
baseline = comparison.loc[comparison.model_id.eq('M0')].iloc[0]
improvement = (baseline.test_mse-selected.test_mse)/baseline.test_mse*100
display(Markdown(f"""### 5.1. Kết luận từ kết quả thực nghiệm

Phân tích **{len(df):,} quan sát** cho thấy giá lệch phải và mẫu khác cơ cấu giữa các nhóm.
Mean/median/n, Pearson theo city và ANOVA giúp mô tả những liên hệ này, với giới hạn giả định rõ ràng.
**{winner_id}, đa thức bậc 3**, được chọn bằng CV MSE, không chọn theo điểm test.
Trên **{len(test):,} holdout**, RMSE **{selected.test_rmse:.2f}**, MAE **{selected.test_mae:.2f}**,
R² **{selected.test_r2:.4f}**; MSE giảm **{improvement:.2f}%** so với baseline M0 trên cùng test.
Mức giải thích biến thiên còn thấp và có **{int(winner.predicted.lt(0).sum())} dự đoán âm**.
**{top_n} dòng lỗi lớn nhất** chiếm **{top_share:.2%} SSE**, cho thấy ít quan sát có thể chi phối MSE.
Thiếu metadata kỳ giá/listing ID và khả năng lặp tọa độ giữa train/test hạn chế khả năng khái quát.
Kết quả chưa chứng minh nhân quả, gian lận hoặc chất lượng định giá ở một thị trường khác.
"""))
''')
md('''## 6. Phân công, kiểm tra và cách trình bày

| Phần | Chủ trì | Khi thầy hỏi code cần giải thích |
|---|---|---|
| Dữ liệu/từ điển/IQR (T02–T04) | Hàn, Huy kiểm | Schema, metadata chưa rõ, khóa truy vết, giữ ngoại lệ |
| EDA/Pearson/ANOVA (T05–T06) | Huy, Hàn kiểm | groupby/pivot, n và nhóm trống, r/F/p, giới hạn |
| Giao thức (T07) | Cả hai | Split/fold cố định, allowlist, không leakage |
| M0–M2 (T08) | Hàn, Huy kiểm | Baseline, hệ số, scaler và dummy |
| M3–M4 (T09) | Huy, Hàn kiểm | Đa thức ba biến, bậc/alpha, chọn CV và refit |
| Holdout (T10) | Cả hai | Bốn metric, cùng test, CV khác test |
| Phần dư (T11) | Huy, Hàn kiểm | Dấu phần dư, lỗi nhóm, SSE và case truy nguồn |
| Kết luận/slide (T13/T15) | Huy, Hàn đọc chéo | Kết quả thật và giới hạn, khớp báo cáo |
| Notebook cuối/kiểm gói (T16–T17) | Cả hai | Restart & Run All; kiểm trên cả hai máy |

Notebook này thay cho việc trình bày lần lượt nhiều file. Không tự đánh dấu đã diễn tập,
đã kiểm máy Hàn hoặc đã đủ thông tin nhóm/LMS. Khi nói: giới thiệu câu hỏi và dữ liệu,
chọn vài bảng/hình trả lời câu hỏi, giải thích CV→test và điểm sai lớn; mở code ở đúng phần khi được hỏi.

Code được gom từ `src/experiment.py` và phần bảng EDA của `src/b_tasks.py`, cùng quy trình
dữ liệu/M0–M2/đánh giá/phần dư đã có trong các notebook 01–05. Dictionary lấy từ bản T03 đã review;
các kết quả mô hình và hình trên đây được tính lại trong kernel này, không lấy điểm từ văn bản.
Các đường dẫn source nêu trên chỉ ghi nhận nguồn code của nhóm; bản nộp hai file không đọc chúng.
Split/fold được tái tạo bằng seed 0 và kiểm digest khớp manifest đã review; không cần CSV thứ hai.
''')
code('''# Bằng chứng tính từ lượt chạy này; hiển thị trong notebook, không ghi file JSON.
assert int(winner.predicted.lt(0).sum()) == 167
assert top_n == 104
assert models['M3'].named_steps['preprocess'].transform(X_train.iloc[:1]).shape[1] == 35
evidence = {'n_source_groups': len(inventory), 'data_shape': list(df.shape), 'n_train': len(train),
            'n_test': len(test), 'n_cv_configurations': len(cv_summary), 'n_fold_records': len(cv_folds),
            'prediction_rows': len(predictions), 'selected_by_cv': winner_id,
            'negative_predictions': int(winner.predicted.lt(0).sum()), 'top_1_percent_rows': top_n,
            'top_1_percent_share_sse': float(top_share), 'protocol_id': config['protocol_id'],
            'data_sha256': hash_now, 'manifest_sha256': manifest_hash,
            'comparison': comparison.to_dict('records'),
            'all_assertions_passed': True}
display(JSON(evidence))
print('ĐÃ CHẠY ĐẾN CUỐI: dữ liệu/split/folds/truy vết đạt; không cần file ngoài notebook và CSV.')
''')

# Preserve Han's latest reviewed presentation/code sections while replacing IO.
for cell_index, source in HAN_SECTIONS.items():
    if cell_index == 36:
        cells[cell_index].source = source + '\n\n' + cells[cell_index].source
    else:
        cells[cell_index].source = source

nb = nbf.v4.new_notebook(cells=cells, metadata={
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python'},
    'ie313': {'purpose': 'portable two-file submission notebook', 'source_commit': '67fb260',
              'authors': ['Hàn (A)', 'Huy (B)'], 'generated_by': 'scripts/build_final_notebook.py'}})
path = ROOT / 'notebooks/IE313_Airbnb_Final.ipynb'
nbf.write(nb, path)
print(path, len(cells), 'cells')
