"""Original Han notebook cells from commit 67fb260.

The builder starts from these exact sources and patches only portable IO,
run instructions and previously identified metadata wording.
"""
HAN_CELLS = [{'cell_type': 'markdown',
  'source': '# IE313 — Phân tích giá Airbnb tại 10 thành phố châu Âu\n'
            '\n'
            '**Notebook trình bày toàn bộ đồ án — Hàn (A) và Huy (B).**\n'
            '\n'
            'Mục tiêu: mô tả phân phối giá, so sánh thành phố/loại phòng/hai nhóm ngày,\n'
            'khảo sát liên hệ với các thuộc tính và so sánh năm mô hình hồi quy trên cùng giao thức.\n'
            'Phân tích giúp giải thích vì sao chỉ nhìn giá trung bình hoặc một hệ số tương quan là chưa đủ,\n'
            'và kiểm tra mức sai số của mô hình trên các quan sát được giữ riêng.\n'
            '\n'
            'Phạm vi là 20 CSV đã có trong repo; không bổ sung dữ liệu, mô hình cây hay ứng dụng ngoài kế '
            'hoạch.\n'
            'Nguồn dữ liệu được README ghi là Kaggle / The Devastator. `realSum` giữ nguyên thang giá:\n'
            'EUR **theo README**, kỳ giá chưa xác minh metadata gốc; không diễn giải thành giá mỗi đêm.\n'
            'AI hỗ trợ viết code và bản thảo; hai thành viên cần hiểu, kiểm tra và khai báo công cụ thực '
            'tế.\n'
            '\n'
            '**Cách sử dụng:** mở file này và chọn **Restart Kernel and Run All**. Code kiểm dữ liệu,\n'
            'chia tập, EDA, xây dựng Pipeline, CV, dự đoán và phần dư đều nằm trong notebook;\n'
            'không cần chạy các notebook khác hoặc import `src`. Các notebook 01–06 giữ lại để truy vết quá '
            'trình.\n'
            'Khi demo, dùng các output đã chạy; không dành thời gian thuyết trình cho việc huấn luyện lại.\n'
            '\n'
            'Trình tự: 1. Nguồn và kiểm dữ liệu → 2. EDA/Pearson/ANOVA → 3. Giao thức và hồi quy\n'
            '→ 4. Đánh giá holdout → 5. Phần dư và kết luận → 6. Phân công và cách kiểm tra.',
  'id': '5a77b461a2638592'},
 {'cell_type': 'markdown',
  'source': '## 1. Nguồn, từ điển và hiện trạng dữ liệu — Hàn, Huy kiểm tra\n'
            '\n'
            'Nạp từng file để kiểm số mẫu/schema, rồi thêm `city`, `day_type`, `source_file`, `source_row`.\n'
            'Khóa file/dòng giúp quay lại dữ liệu gốc; `Unnamed: 0` và tọa độ không phải listing ID.\n'
            'CSV gộp phải khớp dữ liệu nạp lại trước khi sử dụng split đã chốt.',
  'id': '6a15db4efdc4ce80'},
 {'cell_type': 'code',
  'source': 'import hashlib\n'
            'import sys\n'
            'from pathlib import Path\n'
            'import json\n'
            'import numpy as np\n'
            'import pandas as pd\n'
            'import matplotlib.pyplot as plt\n'
            'import seaborn as sns\n'
            'from IPython.display import display, Markdown\n'
            'from scipy.stats import pearsonr, f_oneway\n'
            'from sklearn.compose import ColumnTransformer\n'
            'from sklearn.dummy import DummyRegressor\n'
            'from sklearn.linear_model import LinearRegression, Ridge\n'
            'from sklearn.model_selection import KFold, train_test_split, cross_validate\n'
            'from sklearn.pipeline import Pipeline\n'
            'from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler\n'
            'from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score\n'
            '\n'
            '# Xác định thư mục gốc của dự án\n'
            'ROOT = next((p for p in [Path.cwd(), *Path.cwd().parents]\n'
            "             if (p / 'config/experiment_config.json').is_file()\n"
            "             and (p / 'data/raw').is_dir()), None)\n"
            'if ROOT is None:\n'
            "    raise FileNotFoundError('Vui lòng mở notebook từ thư mục gốc của dự án hoặc thư mục "
            "notebooks.')\n"
            '\n'
            "FINAL_DIR = ROOT / 'outputs/final_notebook'\n"
            'FINAL_DIR.mkdir(parents=True, exist_ok=True)\n'
            '\n'
            '# Cấu hình hiển thị pandas và giao diện biểu đồ\n'
            "pd.set_option('display.max_columns', 25)\n"
            "pd.set_option('display.float_format', lambda x: f'{x:,.4f}')\n"
            "sns.set_theme(style='whitegrid', font='DejaVu Sans')\n"
            '\n'
            'print(f"Thư mục làm việc: {ROOT}")\n'
            'print(f"Phiên bản Python: {sys.version.split()[0]}")\n'
            '\n',
  'id': '62d7ba21a9bea4c1'},
 {'cell_type': 'code',
  'source': '# 1. Nạp và kiểm tra tính nhất quán của 20 tệp dữ liệu thô\n'
            "raw_csv_files = sorted((ROOT / 'data/raw').glob('*.csv'))\n"
            'print(f"-> Tìm thấy {len(raw_csv_files)} tệp CSV thô trong thư mục data/raw.")\n'
            '\n'
            'data_frames = []\n'
            'inventory_records = []\n'
            'original_columns = pd.read_csv(raw_csv_files[0], nrows=0).columns.tolist()\n'
            '\n'
            'for file_path in raw_csv_files:\n'
            '    df_part = pd.read_csv(file_path)\n'
            '    if df_part.columns.tolist() != original_columns:\n'
            '        raise ValueError(f"Tệp {file_path.name} có cấu trúc cột không khớp với chuẩn!")\n'
            '\n'
            "    city_name, day_name = file_path.stem.rsplit('_', 1)\n"
            '    inventory_records.append({\n'
            "        'Tệp': file_path.name,\n"
            "        'Thành phố': city_name,\n"
            "        'Loại ngày': day_name,\n"
            "        'Số dòng': len(df_part),\n"
            "        'Số cột': len(df_part.columns),\n"
            "        'Ô khuyết': int(df_part.isna().sum().sum())\n"
            '    })\n'
            '\n'
            '    # Bổ sung thông tin nguồn và khóa truy vết gốc\n'
            "    df_part['city'] = city_name\n"
            "    df_part['day_type'] = day_name\n"
            "    df_part['source_file'] = file_path.name\n"
            "    df_part['source_row'] = df_part['Unnamed: 0']\n"
            '    data_frames.append(df_part)\n'
            '\n'
            '# Hợp nhất dữ liệu\n'
            'df = pd.concat(data_frames, ignore_index=True)\n'
            'inventory = pd.DataFrame(inventory_records)\n'
            '\n'
            'print(f"-> Đã hợp nhất thành công: {df.shape[0]:,} dòng x {df.shape[1]} cột.")\n'
            'print(f"-> Số lượng thành phố: {df.city.nunique()} | Số nhóm (thành phố x loại ngày): '
            '{df.groupby([\'city\', \'day_type\']).size().shape[0]}")\n'
            'display(inventory)\n',
  'id': '9356a0cbdb0024de'},
 {'cell_type': 'code',
  'source': '# 2. Xây dựng từ điển dữ liệu (Data Dictionary) chuẩn hóa cho 24 thuộc tính\n'
            'dictionary_records = [\n'
            "    {'column_name': 'Unnamed: 0', 'data_type': 'int64', 'category': 'Mã truy vết',\n"
            "     'description_vi': 'Chỉ số dòng gốc trong từng tệp CSV (reset về 0 ở mỗi tệp)',\n"
            "     'usage_note': 'Chỉ dùng làm khóa truy vết nội bộ; không phải ID listing toàn cục, không "
            "dùng làm biến dự báo.'},\n"
            "    {'column_name': 'realSum', 'data_type': 'float64', 'category': 'Biến mục tiêu (Target)',\n"
            "     'description_vi': 'Tổng giá thuê lưu trú (đơn vị EUR theo tài liệu mô tả dữ liệu)',\n"
            "     'usage_note': 'Biến mục tiêu cần dự báo; giữ nguyên thang giá gốc, không biến đổi log khi "
            "huấn luyện mô hình.'},\n"
            "    {'column_name': 'room_type', 'data_type': 'str', 'category': 'Biến phân loại "
            "(Categorical)',\n"
            "     'description_vi': 'Loại phòng cho thuê trên Airbnb (Entire home/apt, Private room, Shared "
            "room)',\n"
            "     'usage_note': 'Đặc trưng phân loại chính; được mã hóa One-Hot Encoding khi đưa vào mô hình "
            "hồi quy.'},\n"
            "    {'column_name': 'room_shared', 'data_type': 'bool', 'category': 'Biến dư thừa',\n"
            "     'description_vi': 'Cờ logic đánh dấu phòng chia sẻ (True nếu room_type là Shared room)',\n"
            "     'usage_note': 'Trùng lặp với room_type. Loại bỏ khỏi tập biến dự báo để tránh đa cộng "
            "tuyến hoàn hảo.'},\n"
            "    {'column_name': 'room_private', 'data_type': 'bool', 'category': 'Biến dư thừa',\n"
            "     'description_vi': 'Cờ logic đánh dấu phòng riêng (True nếu room_type là Private room)',\n"
            "     'usage_note': 'Trùng lặp với room_type. Loại bỏ khỏi tập biến dự báo để tránh đa cộng "
            "tuyến hoàn hảo.'},\n"
            "    {'column_name': 'person_capacity', 'data_type': 'float64', 'category': 'Biến số "
            "(Predictor)',\n"
            "     'description_vi': 'Sức chứa tối đa của chỗ nghỉ (số lượng khách từ 2 đến 6)',\n"
            "     'usage_note': 'Đặc trưng số quan trọng; dùng cho mô hình đơn biến M1 và các mô hình đa "
            "biến.'},\n"
            "    {'column_name': 'host_is_superhost', 'data_type': 'bool', 'category': 'Biến nhị phân "
            "(Predictor)',\n"
            "     'description_vi': 'Chủ nhà đạt danh hiệu Superhost trên nền tảng Airbnb',\n"
            "     'usage_note': 'Biến nhị phân logic; chuyển đổi sang dạng số 0/1 trong Pipeline.'},\n"
            "    {'column_name': 'multi', 'data_type': 'int64', 'category': 'Biến phụ',\n"
            "     'description_vi': 'Cờ nhị phân liên quan đến nhiều chỗ nghỉ của chủ nhà',\n"
            "     'usage_note': 'Không đưa vào mô hình cốt lõi do thiếu định nghĩa chính thức trong tài liệu "
            "gốc.'},\n"
            "    {'column_name': 'biz', 'data_type': 'int64', 'category': 'Biến phụ',\n"
            "     'description_vi': 'Cờ nhị phân liên quan đến hoạt động kinh doanh chuyên nghiệp',\n"
            "     'usage_note': 'Không đưa vào mô hình cốt lõi do thiếu định nghĩa chính thức trong tài liệu "
            "gốc.'},\n"
            "    {'column_name': 'cleanliness_rating', 'data_type': 'float64', 'category': 'Biến số "
            "(Predictor)',\n"
            "     'description_vi': 'Điểm đánh giá mức độ sạch sẽ của chỗ nghỉ (thang điểm quan sát 2 - "
            "10)',\n"
            "     'usage_note': 'Chuẩn hóa bằng StandardScaler trước khi đưa vào mô hình hồi quy đa "
            "biến.'},\n"
            "    {'column_name': 'guest_satisfaction_overall', 'data_type': 'float64', 'category': 'Biến số "
            "(Predictor)',\n"
            "     'description_vi': 'Điểm hài lòng tổng thể từ khách lưu trú (thang điểm quan sát 20 - "
            "100)',\n"
            "     'usage_note': 'Chuẩn hóa bằng StandardScaler trước khi đưa vào mô hình hồi quy đa "
            "biến.'},\n"
            "    {'column_name': 'bedrooms', 'data_type': 'int64', 'category': 'Biến số (Predictor)',\n"
            "     'description_vi': 'Số lượng phòng ngủ (từ 0 đến 10; giá trị 0 là phòng studio/phòng mở)',\n"
            "     'usage_note': 'Đặc trưng số nguyên hợp lệ; chuẩn hóa bằng StandardScaler.'},\n"
            "    {'column_name': 'dist', 'data_type': 'float64', 'category': 'Biến số (Predictor)',\n"
            "     'description_vi': 'Khoảng cách từ chỗ nghỉ đến trung tâm thành phố (đơn vị km)',\n"
            "     'usage_note': 'Đặc trưng vị trí địa lý cốt lõi; chuẩn hóa bằng StandardScaler.'},\n"
            "    {'column_name': 'metro_dist', 'data_type': 'float64', 'category': 'Biến số (Predictor)',\n"
            "     'description_vi': 'Khoảng cách từ chỗ nghỉ đến ga metro gần nhất (đơn vị km)',\n"
            "     'usage_note': 'Đặc trưng vị trí địa lý; chuẩn hóa bằng StandardScaler.'},\n"
            "    {'column_name': 'attr_index', 'data_type': 'float64', 'category': 'Chỉ số thô',\n"
            "     'description_vi': 'Chỉ số sức hấp dẫn du lịch khu vực (giá trị thô)',\n"
            "     'usage_note': 'Chỉ dùng cho mục đích khám phá mô tả; không đưa vào mô hình cốt lõi.'},\n"
            "    {'column_name': 'attr_index_norm', 'data_type': 'float64', 'category': 'Chỉ số chuẩn hóa',\n"
            "     'description_vi': 'Chỉ số sức hấp dẫn du lịch đã chuẩn hóa thang 100',\n"
            "     'usage_note': 'Chỉ dùng cho mục đích khám phá mô tả; không đưa vào mô hình cốt lõi.'},\n"
            "    {'column_name': 'rest_index', 'data_type': 'float64', 'category': 'Chỉ số thô',\n"
            "     'description_vi': 'Chỉ số nhà hàng/ẩm thực khu vực (giá trị thô)',\n"
            "     'usage_note': 'Chỉ dùng cho mục đích khám phá mô tả; không đưa vào mô hình cốt lõi.'},\n"
            "    {'column_name': 'rest_index_norm', 'data_type': 'float64', 'category': 'Chỉ số chuẩn hóa',\n"
            "     'description_vi': 'Chỉ số nhà hàng/ẩm thực đã chuẩn hóa thang 100',\n"
            "     'usage_note': 'Chỉ dùng cho mục đích khám phá mô tả; không đưa vào mô hình cốt lõi.'},\n"
            "    {'column_name': 'lng', 'data_type': 'float64', 'category': 'Tọa độ địa lý',\n"
            "     'description_vi': 'Kinh độ địa lý của chỗ nghỉ',\n"
            "     'usage_note': 'Dùng cho trực quan hóa bản đồ theo từng thành phố; không làm biến hồi quy "
            "tuyến tính toàn cục.'},\n"
            "    {'column_name': 'lat', 'data_type': 'float64', 'category': 'Tọa độ địa lý',\n"
            "     'description_vi': 'Vĩ độ địa lý của chỗ nghỉ',\n"
            "     'usage_note': 'Dùng cho trực quan hóa bản đồ theo từng thành phố; không làm biến hồi quy "
            "tuyến tính toàn cục.'},\n"
            "    {'column_name': 'city', 'data_type': 'str', 'category': 'Biến phân loại (Predictor)',\n"
            "     'description_vi': 'Tên thành phố tại châu Âu (10 thành phố)',\n"
            "     'usage_note': 'Biến phân nhóm quan trọng; mã hóa One-Hot Encoding trong Pipeline.'},\n"
            "    {'column_name': 'day_type', 'data_type': 'str', 'category': 'Biến phân loại (Predictor)',\n"
            "     'description_vi': 'Loại ngày khảo sát (weekdays - ngày thường hoặc weekends - cuối "
            "tuần)',\n"
            "     'usage_note': 'Mã hóa One-Hot Encoding đại diện cho yếu tố thời điểm khảo sát.'},\n"
            "    {'column_name': 'source_file', 'data_type': 'str', 'category': 'Mã truy vết',\n"
            "     'description_vi': 'Tên tệp CSV nguồn gốc chứa bản ghi',\n"
            "     'usage_note': 'Dùng đối chiếu và truy vết sai số; không dùng làm biến dự báo.'},\n"
            "    {'column_name': 'source_row', 'data_type': 'int64', 'category': 'Mã truy vết',\n"
            "     'description_vi': 'Chỉ số dòng gốc trong tệp CSV nguồn',\n"
            "     'usage_note': 'Dùng đối chiếu và truy vết sai số; không dùng làm biến dự báo.'}\n"
            ']\n'
            '\n'
            'dictionary = pd.DataFrame(dictionary_records)\n'
            "display(dictionary[['column_name', 'data_type', 'category', 'description_vi', 'usage_note']])\n",
  'id': '346549ba200f24cf'},
 {'cell_type': 'markdown',
  'source': '### 1.1. Kiểm toán chất lượng dữ liệu trước khi phân tích\n'
            '\n'
            'Trong phân tích dữ liệu, việc tập dữ liệu không chứa ô trống (`NaN`) chưa đủ để khẳng định dữ '
            'liệu hoàn toàn hợp lệ. Nhóm thực hiện kiểm toán sâu trên các khía cạnh:\n'
            '- **Tính hợp lý của giá trị số:** Giá thuê (`realSum`) phải là số dương ($> 0$), khoảng cách '
            '(`dist`, `metro_dist`) không được âm, tọa độ địa lý phải nằm trong phạm vi hợp lệ của châu Âu.\n'
            '- **Tính toàn vẹn logic:** Các cờ logic loại phòng (`room_shared`, `room_private`) phải hoàn '
            'toàn nhất quán với giá trị của cột `room_type`.\n'
            '- **Ký tự khuyết ẩn:** Kiểm tra các chuỗi đặc biệt thường dùng biểu diễn giá trị thiếu như '
            '`null`, `none`, `n/a`, `nan`, `?`.\n'
            '- **Tính duy nhất của khóa truy vết:** Cặp (`source_file`, `source_row`) phải là duy nhất trên '
            'toàn bộ tập dữ liệu để đảm bảo khả năng truy xuất ngược.\n',
  'id': 'c7194aa48fc9dd00'},
 {'cell_type': 'code',
  'source': 'def audit_data_quality(dataframe):\n'
            '    """Kiểm tra toàn diện tính toàn vẹn và các quy tắc nghiệp vụ của dữ liệu."""\n'
            '    hidden_null_count = sum(\n'
            '        int(dataframe[col].astype(str).str.strip().str.lower().isin(\n'
            "            ['', '?', '.', 'none', 'null', 'n/a', 'na', 'nan']).sum())\n"
            "        for col in dataframe.select_dtypes(include=['object', 'str']).columns\n"
            '    )\n'
            '\n'
            '    rules = [\n'
            "        ('1. Ô khuyết thiếu (Missing cells)', int(dataframe.isna().sum().sum())),\n"
            "        ('2. Ký tự khuyết ẩn (null, none, n/a, ?)', hidden_null_count),\n"
            "        ('3. Giá trị số không hữu hạn (NaN, Inf)', "
            "int((~np.isfinite(dataframe.select_dtypes(include='number'))).sum().sum())),\n"
            "        ('4. Giá thuê không hợp lệ (realSum <= 0)', int((~dataframe.realSum.gt(0)).sum())),\n"
            "        ('5. Trùng lặp khóa truy vết (source_file, source_row)', "
            "int(dataframe.duplicated(['source_file', 'source_row']).sum())),\n"
            "        ('6. Loại phòng không thuộc danh mục hợp lệ', int((~dataframe.room_type.isin(['Entire "
            "home/apt', 'Private room', 'Shared room'])).sum())),\n"
            "        ('7. Không khớp logic cờ room_shared', int((dataframe.room_shared != "
            "dataframe.room_type.eq('Shared room')).sum())),\n"
            "        ('8. Không khớp logic cờ room_private', int((dataframe.room_private != "
            "dataframe.room_type.eq('Private room')).sum())),\n"
            "        ('9. Cờ logic nhận giá trị ngoài True/False', sum(int((~dataframe[c].isin([True, "
            "False])).sum()) for c in ['room_shared', 'room_private', 'host_is_superhost'])),\n"
            "        ('10. Sức chứa không hợp lệ (person_capacity < 1 hoặc không nguyên)', "
            'int((~(dataframe.person_capacity.ge(1) & dataframe.person_capacity.mod(1).eq(0))).sum())),\n'
            "        ('11. Số phòng ngủ không hợp lệ (bedrooms < 0 hoặc không nguyên)', "
            'int((~(dataframe.bedrooms.ge(0) & dataframe.bedrooms.mod(1).eq(0))).sum())),\n'
            "        ('12. Khoảng cách âm (dist hoặc metro_dist < 0)', int((dataframe[['dist', "
            "'metro_dist']] < 0).sum().sum())),\n"
            "        ('13. Tọa độ địa lý ngoài phạm vi châu Âu', int((~(dataframe.lat.between(-90, 90) & "
            'dataframe.lng.between(-180, 180))).sum()))\n'
            '    ]\n'
            '\n'
            "    report = pd.DataFrame(rules, columns=['Quy tắc kiểm tra', 'Số lượng vi phạm'])\n"
            "    report['Đánh giá'] = np.where(report['Số lượng vi phạm'] == 0, 'Đạt', 'Không đạt')\n"
            '    return report\n'
            '\n'
            'quality_report = audit_data_quality(df)\n'
            'display(quality_report)\n'
            '\n'
            'print(f"-> Số dòng trùng lặp hoàn toàn 20 cột gốc: {df.duplicated(original_columns).sum()}")\n'
            'print(f"-> Số bản ghi trùng tọa độ (city, lat, lng): {df.duplicated([\'city\', \'lat\', '
            '\'lng\']).sum():,} (đặc tính lấy mẫu trên cùng tòa nhà/khu vực)")\n'
            'print(f"-> Khoảng cách metro nhỏ nhất ghi nhận: {df.metro_dist.min():.4f} km")\n'
            "display(df.select_dtypes(include='number').describe().T)\n",
  'id': '76433a76c8687131'},
 {'cell_type': 'markdown',
  'source': '### 1.2. Phân tích phân phối giá và nhận diện điểm ngoại lai (IQR)\n'
            '\n'
            '- **Đặc điểm phân phối:** Giá thuê (`realSum`) có phân phối lệch phải rất mạnh (hệ số bất đối '
            'xứng Skewness $> 20$). Giá trung bình (Mean $\\approx 279,88$ EUR) bị kéo lệch đáng kể so với '
            'trung vị (Median $\\approx 211,34$ EUR) bởi các bất động sản cao cấp có giá lên đến hàng nghìn '
            'EUR.\n'
            '- **Phương pháp IQR:** Khoảng tứ phân vị $\\text{IQR} = Q_3 - Q_1$ được sử dụng để xác định '
            'ranh giới giá thông thường: $[Q_1 - 1,5 \\times \\text{IQR},\\ Q_3 + 1,5 \\times '
            '\\text{IQR}]$.\n'
            '- **Quyết định phân tích:** Nhóm quyết định **giữ nguyên 100% các quan sát ngoại lai** trong '
            'quá trình phân tích và huấn luyện mô hình. Lý do: trong lĩnh vực lưu trú và du lịch, các căn hộ '
            'hạng sang có giá thuê cao là thực tế kinh doanh khách quan, không phải do lỗi nhập liệu. Việc '
            'loại bỏ nhân tạo sẽ làm sai lệch bản chất thị trường.\n',
  'id': 'f6ce9f0c983a3fe2'},
 {'cell_type': 'code',
  'source': 'def calculate_price_iqr(frame):\n'
            '    """Tính toán các chỉ số thống kê mô tả và ngưỡng IQR cho cột giá realSum."""\n'
            '    price = frame.realSum\n'
            '    q1 = price.quantile(0.25)\n'
            '    q3 = price.quantile(0.75)\n'
            '    iqr = q3 - q1\n'
            '    lower_fence = q1 - 1.5 * iqr\n'
            '    upper_fence = q3 + 1.5 * iqr\n'
            '\n'
            '    return {\n'
            "        'Số mẫu': len(frame),\n"
            "        'Mean': price.mean(),\n"
            "        'Median': price.median(),\n"
            "        'Std': price.std(),\n"
            "        'Skewness': price.skew(),\n"
            "        'Max': price.max(),\n"
            "        'Cận dưới IQR': lower_fence,\n"
            "        'Cận trên IQR': upper_fence,\n"
            "        'Số ngoại lai': int((price.lt(lower_fence) | price.gt(upper_fence)).sum())\n"
            '    }\n'
            '\n'
            "price_summary_rows = [{'Phạm vi': 'Toàn bộ 10 thành phố', **calculate_price_iqr(df)}]\n"
            "for city_name, city_group in df.groupby('city'):\n"
            "    price_summary_rows.append({'Phạm vi': city_name, **calculate_price_iqr(city_group)})\n"
            '\n'
            'price_audit = pd.DataFrame(price_summary_rows)\n'
            'display(price_audit)\n'
            '\n'
            'fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))\n'
            "axes[0].hist(df.realSum, bins=70, color='#2b5c8f', edgecolor='black', alpha=0.7)\n"
            "axes[0].set_title('Phân phối giá gốc realSum (Giữ nguyên toàn bộ ngoại lai)', fontsize=11)\n"
            "axes[0].set_xlabel('Giá realSum (EUR)')\n"
            "axes[0].set_ylabel('Số lượng chỗ nghỉ')\n"
            '\n'
            "axes[1].hist(np.log10(df.realSum), bins=70, color='#e07a5f', edgecolor='black', alpha=0.7)\n"
            "axes[1].set_title('Phân phối log10(realSum) để quan sát hình dạng dữ liệu', fontsize=11)\n"
            "axes[1].set_xlabel('log10(realSum)')\n"
            "axes[1].set_ylabel('Số lượng chỗ nghỉ')\n"
            '\n'
            'plt.tight_layout()\n'
            'plt.show()\n',
  'id': '73ca033b78187438'},
 {'cell_type': 'markdown',
  'source': '### 1.3. Phân nhóm mô tả khoảng cách và mức giá (Binning)\n'
            '\n'
            'Để hỗ trợ phân tích cơ cấu và trực quan hóa phân bố, nhóm thực hiện phân nhóm hai thuộc tính '
            'liên tục:\n'
            '- **Khoảng cách đến trung tâm (`dist_bin`):** Chia thành 4 khoảng: `[0, 1)` km, `[1, 3)` km, '
            '`[3, 5)` km và `[5, +inf)` km.\n'
            '- **Phân khúc giá (`price_tier`):** Chia thành 4 phân khúc: `[0, 150)` EUR, `[150, 350)` EUR, '
            '`[350, 600)` EUR và `[600, +inf)` EUR.\n'
            '\n'
            '*Lưu ý phương pháp luận:* Các thuộc tính phân nhóm này được tạo trên một bản sao riêng '
            '(`descriptive`) nhằm mục đích mô tả và lập bảng tần số chéo, **không đưa vào làm biến dự báo '
            '(predictor)** trong các mô hình học máy để tránh rò rỉ dữ liệu hoặc đa cộng tuyến.\n',
  'id': '19dc8ee0828c8fe6'},
 {'cell_type': 'code',
  'source': 'descriptive = df.copy()\n'
            '\n'
            "descriptive['dist_bin'] = pd.cut(\n"
            '    descriptive.dist,\n'
            '    bins=[0, 1, 3, 5, np.inf],\n'
            "    labels=['[0, 1) km', '[1, 3) km', '[3, 5) km', '[5, +inf) km'],\n"
            '    right=False\n'
            ')\n'
            '\n'
            "descriptive['price_tier'] = pd.cut(\n"
            '    descriptive.realSum,\n'
            '    bins=[0, 150, 350, 600, np.inf],\n'
            "    labels=['[0, 150) EUR', '[150, 350) EUR', '[350, 600) EUR', '[600, +inf) EUR'],\n"
            '    right=False\n'
            ')\n'
            '\n'
            'print("1. Thống kê giá theo các khoảng khoảng cách đến trung tâm:")\n'
            "display(descriptive.groupby('dist_bin', observed=False).realSum.agg(\n"
            "    n='size',\n"
            "    mean='mean',\n"
            "    median='median',\n"
            "    std='std'\n"
            '))\n'
            '\n'
            'print("\\n2. Bảng tần số chéo (Crosstab) giữa khoảng cách trung tâm và phân khúc giá:")\n'
            'display(pd.crosstab(descriptive.dist_bin, descriptive.price_tier, margins=True, '
            "margins_name='Tổng'))\n",
  'id': '7dbe9531eeca58e5'},
 {'cell_type': 'markdown',
  'source': '### 1.4. Tổng kết hiện trạng dữ liệu trước khi phân tích\n'
            '\n'
            '- **Điểm mạnh:**\n'
            '  - Quy mô mẫu lớn với 51.707 quan sát phủ khắp 10 thành phố lớn tại châu Âu.\n'
            '  - Cấu trúc dữ liệu đồng nhất trên toàn bộ 20 tệp nguồn; không có giá trị khuyết thiếu trong '
            'tập dữ liệu cung cấp.\n'
            '  - Đầy đủ cả 2 điều kiện khảo sát (ngày thường và cuối tuần) cho từng thành phố.\n'
            '  - Đã thiết lập khóa truy vết (`source_file`, `source_row`) cho phép đối chiếu ngược lại từng '
            'dòng gốc khi kiểm tra sai số mô hình.\n'
            '\n'
            '- **Thách thức và giới hạn:**\n'
            '  - Phân phối giá lệch phải mạnh, tồn tại các căn hộ giá thuê rất cao. Do đó, cần luôn báo cáo '
            'song song cả Trung vị (Median) và IQR bên cạnh Trung bình (Mean).\n'
            '  - Tỷ lệ các loại phòng chênh lệch lớn (Entire home/apt chiếm ~63%, Private room ~36%, trong '
            'khi Shared room chỉ chiếm 0.71%).\n'
            '  - Tồn tại các trường hợp lặp tọa độ địa lý (các phòng khác nhau trong cùng một tòa nhà hoặc '
            'khu phức hợp).\n'
            '  - Kết quả phân tích áp dụng cho tập dữ liệu khảo sát được cung cấp, không đại diện hoàn toàn '
            'cho toàn bộ thị trường lưu trú châu Âu tại mọi thời điểm.\n',
  'id': 'db4776bf2859fd6b'},
 {'cell_type': 'markdown',
  'source': '## 2. EDA và bằng chứng liên hệ — Huy, Hàn kiểm tra\n'
            '\n'
            '**Q1:** giá và số mẫu khác nhau thế nào theo city/room? **Q2:** hai nhóm ngày có khác nhau,\n'
            'và chênh lệch có đi kèm khác cơ cấu phòng? **Q3:** liên hệ tuyến tính của thuộc tính với giá\n'
            'gộp và trong từng city? **Q4:** mean giá khác nhau theo nhóm trong ANOVA, với giới hạn gì?\n'
            '\n'
            'Trước EDA, đọc allowlist và khóa split đã chốt để tách bảng full/train. EDA không dùng để\n'
            'tự động chọn biến theo r/p trên toàn bộ dữ liệu.',
  'id': '12d8661e414b13e2'},
 {'cell_type': 'code',
  'source': "config = json.loads((ROOT / 'config/experiment_config.json').read_text(encoding='utf-8'))\n"
            "manifest = pd.read_csv(ROOT / config['split']['manifest'])\n"
            "hash_now = hashlib.sha256((ROOT / config['data_file']).read_bytes().replace(b'\\r\\n', "
            "b'\\n')).hexdigest()\n"
            "assert hash_now == config['data_sha256']\n"
            "pd.testing.assert_frame_equal(df[config['trace_keys']], manifest[config['trace_keys']])\n"
            'expected_train, expected_test = train_test_split(np.arange(len(df)), test_size=.2, '
            'random_state=0)\n'
            'expected_train = np.sort(expected_train)\n'
            "assert np.array_equal(np.flatnonzero(manifest.split.eq('train')), expected_train)\n"
            "assert np.array_equal(np.flatnonzero(manifest.split.eq('test')), np.sort(expected_test))\n"
            "assert manifest.loc[manifest.split.eq('test'), 'cv_fold'].eq(-1).all()\n"
            "train = df.loc[manifest.split.eq('train')].reset_index(drop=True)\n"
            "test = df.loc[manifest.split.eq('test')].reset_index(drop=True)\n"
            "train_folds = manifest.loc[manifest.split.eq('train'), 'cv_fold'].to_numpy()\n"
            'cv = [(np.flatnonzero(train_folds != fold), np.flatnonzero(train_folds == fold)) for fold in '
            'range(5)]\n'
            'for fold, (fit_idx, valid_idx) in enumerate(KFold(5, shuffle=True, '
            'random_state=0).split(train)):\n'
            '    assert np.array_equal(cv[fold][0], fit_idx) and np.array_equal(cv[fold][1], valid_idx)\n'
            'assert len(train) == 41365 and len(test) == 10342\n'
            'assert set(train_folds) == set(range(5))\n'
            "display(pd.DataFrame([{'fold': f, 'fit': len(a), 'validation': len(b)} for f, (a,b) in "
            'enumerate(cv)]))',
  'id': 'fa9be3eea5a07f13'},
 {'cell_type': 'code',
  'source': 'def predictor_names(config):\n'
            "    p = config['predictors']\n"
            "    return p['numeric'] + p['categorical'] + p['boolean']",
  'id': '9c3d9367321a16c6'},
 {'cell_type': 'code',
  'source': '# Các bảng của notebook cuối ghi riêng; không ghi đè sản phẩm bàn giao cũ.\n'
            "LIMIT = ('Mô tả liên hệ, không nhân quả; giá lệch phải/nhóm mất cân đối, '\n"
            "         'độc lập mẫu chưa xác minh do tọa độ lặp; p nhỏ không đo độ lớn tác động.')\n"
            'def save_table(frame, name, root=ROOT):\n'
            '    path = FINAL_DIR / name\n'
            "    frame.to_csv(path, index=False, encoding='utf-8-sig')\n"
            '    return path\n'
            '\n'
            'def price_summary(df, columns):\n'
            "    table = df.groupby(columns, observed=True)['realSum'].agg(\n"
            "        n='size', mean='mean', median='median', std='std',\n"
            '        q1=lambda s: s.quantile(.25), q3=lambda s: s.quantile(.75)).reset_index()\n'
            '    if len(columns) > 1:\n'
            '        grid = pd.MultiIndex.from_product([sorted(df[c].unique()) for c in columns], '
            'names=columns)\n'
            '        table = table.set_index(columns).reindex(grid).reset_index()\n'
            "        table['n'] = table.n.fillna(0).astype(int)\n"
            "    table['iqr'] = table.q3 - table.q1\n"
            "    table['grouping'] = '+'.join(columns)\n"
            "    table['availability'] = np.where(table.n.eq(0), 'no_observations', 'observed')\n"
            '    return table\n'
            '\n'
            '\n'
            'def build_eda_tables(df, root=ROOT):\n'
            '    """Q1/Q2: bao gồm nhóm trống nhưng không gán giá 0 cho nhóm không có mẫu."""\n'
            "    sets = [['city'], ['room_type'], ['city', 'day_type'], ['city', 'room_type'],\n"
            "            ['city', 'room_type', 'day_type']]\n"
            '    tables = [price_summary(df, cols) for cols in sets]\n'
            '    summaries = pd.concat(tables, ignore_index=True)\n'
            "    for _, g in summaries.groupby('grouping'):\n"
            '        assert g.n.sum() == len(df)\n'
            "        assert g.loc[g.n.eq(0), 'median'].isna().all()\n"
            '    sampling = tables[-1].copy()\n'
            "    sampling['share_of_city_day'] = sampling.n / sampling.groupby(['city', "
            "'day_type']).n.transform('sum')\n"
            "    pairs = sampling.pivot(index=['city', 'room_type'], columns='day_type', values=['n', "
            "'mean', 'median'])\n"
            "    pairs.columns = [metric + '_' + day for metric, day in pairs.columns]\n"
            '    pairs = pairs.reset_index()\n'
            "    pairs['median_difference_weekends_minus_weekdays'] = pairs.median_weekends - "
            'pairs.median_weekdays\n'
            "    pairs['interpretation'] = 'Chênh hai nhóm quan sát; không ghép cặp cùng listing'\n"
            '    # So sánh gộp city/day riêng, để thấy khác cơ cấu loại phòng.\n'
            '    city_day = tables[2]\n'
            "    city_pairs = city_day.pivot(index='city', columns='day_type', values=['n', 'mean', "
            "'median'])\n"
            "    city_pairs.columns = [metric + '_' + day for metric, day in city_pairs.columns]\n"
            '    city_pairs = city_pairs.reset_index()\n'
            "    city_pairs['median_difference_weekends_minus_weekdays'] = city_pairs.median_weekends - "
            'city_pairs.median_weekdays\n'
            "    save_table(summaries, 'eda_group_summary.csv', root)\n"
            "    save_table(sampling, 'eda_sampling_counts.csv', root)\n"
            "    save_table(pairs, 'eda_day_comparison_by_room.csv', root)\n"
            "    save_table(city_pairs, 'eda_day_comparison_by_city.csv', root)\n"
            '    return summaries, sampling, city_pairs',
  'id': 'd07798a00edb2e32'},
 {'cell_type': 'code',
  'source': 'group_summary, sampling, city_pairs = build_eda_tables(df)\n'
            "display(group_summary.loc[group_summary.grouping.eq('city'), ['city', 'n', 'mean', 'median', "
            "'iqr']])\n"
            "display(group_summary.loc[group_summary.grouping.eq('room_type'), ['room_type', 'n', 'mean', "
            "'median', 'iqr']])\n"
            "display(city_pairs[['city', 'n_weekdays', 'n_weekends', 'median_weekdays', 'median_weekends',\n"
            "                    'median_difference_weekends_minus_weekdays']])\n"
            "display(pd.read_csv(FINAL_DIR / 'eda_day_comparison_by_room.csv'))",
  'id': 'dddbaef09f816c3b'},
 {'cell_type': 'markdown',
  'source': '### 2.1. Biểu đồ nhóm và cơ cấu mẫu\n'
            '\n'
            'Đọc count trước khi so sánh giá. Shared room có ít quan sát; tổ hợp không có mẫu có n=0,\n'
            'giá giữ NaN thay vì điền 0. Chênh weekdays/weekends là hai tập quan sát, không ghép cặp cùng '
            'phòng.\n'
            'Phân nhóm theo loại phòng giúp kiểm tra cơ cấu, chưa đủ để kết luận tác động nhân quả của cuối '
            'tuần.',
  'id': '4c795d430de6629c'},
 {'cell_type': 'code',
  'source': 'fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n'
            'city_counts = df.city.value_counts().sort_values()\n'
            "city_counts.plot.barh(ax=axes[0], color='#315776')\n"
            "axes[0].set(title='Số mẫu theo city', xlabel='Count')\n"
            "sns.boxplot(data=df, x='room_type', y='realSum', ax=axes[1], showfliers=True)\n"
            "axes[1].set_yscale('log')\n"
            "axes[1].set(title='Giá theo phòng, giữ ngoại lệ', ylabel='realSum — trục log')\n"
            'plt.tight_layout(); plt.show()\n'
            'fig, axes = plt.subplots(1, 2, figsize=(15, 5))\n'
            "city_day = group_summary.loc[group_summary.grouping.eq('city+day_type')]\n"
            "sns.barplot(data=city_day, x='city', y='median', hue='day_type', errorbar=None, ax=axes[0])\n"
            "axes[0].tick_params(axis='x', rotation=40)\n"
            "axes[0].set(title='Median giá của hai nhóm ngày', ylabel='realSum')\n"
            "shares = sampling.pivot(index=['city', 'day_type'], columns='room_type', "
            "values='share_of_city_day')\n"
            'shares.plot.bar(stacked=True, ax=axes[1], width=.85)\n'
            "axes[1].set(title='Cơ cấu loại phòng theo city/ngày', ylabel='Tỷ lệ mẫu')\n"
            'axes[1].legend(fontsize=8)\n'
            'plt.tight_layout(); plt.show()',
  'id': 'aa0c25e21c3f7b43'},
 {'cell_type': 'code',
  'source': 'def p_fields(p):\n'
            '    """SciPy có thể underflow p thành 0; không diễn giải là xác suất bằng 0."""\n'
            '    underflow = p == 0.0\n'
            "    return {'p_value': np.nan if underflow else p,\n"
            "            'p_display': 'underflow_float64; not exact zero' if underflow else f'{p:.4e}',\n"
            "            'p_underflow': underflow, 'p_lt_0_05': bool(p < .05)}\n"
            '\n'
            '\n'
            'def build_evidence(df, train, config, root=ROOT):\n'
            "    numeric = ['person_capacity', 'bedrooms', 'dist', 'metro_dist', 'cleanliness_rating',\n"
            "               'guest_satisfaction_overall', 'attr_index', 'attr_index_norm',\n"
            "               'rest_index', 'rest_index_norm', 'lng', 'lat']\n"
            '    allowed = set(predictor_names(config))\n'
            '    pearson_rows, anova_rows, group_rows = [], [], []\n'
            "    for scope, data in [('full_descriptive', df), ('train_descriptive', train)]:\n"
            '        # Bảng train chỉ là diễn giải kiểm tra; allowlist không được lọc bằng r/p này.\n'
            "        contexts = [('all_cities', data)] + list(data.groupby('city', sort=True))\n"
            '        for context, group in contexts:\n'
            '            for feature in numeric:\n'
            '                x, y = group[feature], group.realSum\n'
            '                valid = x.notna() & y.notna()\n'
            '                if valid.sum() < 3 or x[valid].nunique() < 2:\n'
            '                    r, p = np.nan, np.nan\n'
            '                else:\n'
            '                    r, p = pearsonr(x[valid].to_numpy(), y[valid].to_numpy())\n'
            "                row = {'scope': scope, 'context': context, 'feature': feature, 'n': "
            'int(valid.sum()),\n'
            "                       'method': 'Pearson', 'r': r, 'abs_r_ge_0_3': bool(abs(r) >= .3),\n"
            "                       'used_in_core_model': feature in allowed, 'limitations': LIMIT}\n"
            '                row.update(p_fields(p)); pearson_rows.append(row)\n'
            "        for feature, context, group in [('city', 'all_cities', data),\n"
            "                                         ('room_type', 'all_cities', data)] + [\n"
            "                                         ('room_type', city, g) for city, g in "
            "data.groupby('city')]:\n"
            '            groups = [(label, g.realSum.to_numpy()) for label, g in group.groupby(feature, '
            'observed=True)]\n'
            '            arrays = [a for _, a in groups]\n'
            '            variances = [np.var(a, ddof=1) for a in arrays if len(a) > 1]\n'
            '            if len(arrays) >= 2 and all(len(a) >= 2 for a in arrays):\n'
            '                f, p = f_oneway(*arrays)\n'
            '            else:\n'
            '                f, p = np.nan, np.nan\n'
            "            row = {'scope': scope, 'context': context, 'feature': feature, 'method': 'One-way "
            "ANOVA',\n"
            "                   'n': len(group), 'n_groups': len(groups), 'min_group_n': min(map(len, "
            'arrays)),\n'
            "                   'f': f, 'variance_ratio_max_min': max(variances)/min(variances) if variances "
            'and min(variances)>0 else np.nan,\n'
            "                   'used_in_core_model': feature in allowed, 'limitations': LIMIT}\n"
            '            row.update(p_fields(p)); anova_rows.append(row)\n'
            '            for label, a in groups:\n'
            "                group_rows.append({'scope': scope, 'context': context, 'feature': feature,\n"
            "                                   'group': label, 'n': len(a), 'mean': np.mean(a), 'median': "
            'np.median(a),\n'
            "                                   'std': np.std(a, ddof=1) if len(a)>1 else np.nan})\n"
            '    pearson = pd.DataFrame(pearson_rows)\n'
            '    anova = pd.DataFrame(anova_rows)\n'
            '    evidence = pd.concat([pearson, anova], ignore_index=True)\n'
            "    evidence['decision'] = np.where(evidence.used_in_core_model, 'semantic_core_candidate', "
            "'descriptive_only_excluded_core')\n"
            "    evidence['decision_basis'] = 'Allowlist định trước theo ý nghĩa/metadata; r/p/F là mô tả, "
            "không tự động chọn theo y'\n"
            "    save_table(pearson, 'pearson_price_evidence.csv', root)\n"
            "    save_table(anova, 'anova_price_evidence.csv', root)\n"
            "    save_table(pd.DataFrame(group_rows), 'anova_group_details.csv', root)\n"
            "    save_table(evidence, 'feature_evidence.csv', root)\n"
            "    corr = df[numeric + ['realSum']].corr()\n"
            "    save_table(corr.reset_index(names='feature'), 'eda_correlation_matrix.csv', root)\n"
            '    return pearson, anova, corr',
  'id': 'bc25c0ed98b3572d'},
 {'cell_type': 'code',
  'source': 'pearson, anova, corr = build_evidence(df, train, config)\n'
            "display(pearson.loc[(pearson.scope == 'full_descriptive') & (pearson.context == 'all_cities'),\n"
            "                    ['feature', 'n', 'r', 'p_display', 'used_in_core_model']])\n"
            "display(pearson.loc[(pearson.scope == 'full_descriptive') & (pearson.feature == "
            "'person_capacity'),\n"
            "                    ['context', 'n', 'r', 'p_display']])\n"
            "display(anova.loc[(anova.scope == 'full_descriptive') & (anova.context == 'all_cities'),\n"
            "                  ['feature', 'n', 'min_group_n', 'f', 'p_display', "
            "'variance_ratio_max_min']])\n"
            'fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n'
            "sns.heatmap(corr, cmap='vlag', center=0, vmin=-1, vmax=1, ax=axes[0])\n"
            "axes[0].set(title='Tương quan Pearson: full descriptive')\n"
            'axes[1].scatter(df.person_capacity, df.realSum, s=4, alpha=.12)\n'
            "axes[1].set(xlabel='person_capacity', ylabel='realSum', title='Scatter: toàn bộ quan sát')\n"
            'plt.tight_layout(); plt.show()',
  'id': '346c3effe048925e'},
 {'cell_type': 'markdown',
  'source': '### 2.2. Diễn giải Pearson/ANOVA và vì sao không lọc biến máy móc\n'
            '\n'
            'Pearson đo liên hệ tuyến tính, nhạy với giá lớn và việc gộp city; r gộp nhỏ không bác bỏ\n'
            'liên hệ trong từng city. ANOVA kiểm khác biệt mean giữa nhóm, không chứng minh mọi cặp khác\n'
            'nhau hay mức tác động lớn. Giá lệch, nhóm mất cân đối và tính độc lập chưa xác minh làm\n'
            'giới hạn giả định kiểm định. p underflow được ghi rõ, không gọi xác suất chính xác bằng 0.\n'
            '\n'
            'Giữ predictor theo ý nghĩa/metadata đã chốt; r/p/F là bằng chứng mô tả. Không áp ngưỡng\n'
            'Pearson của bài tập giá xe để loại hết biến Airbnb. Tất cả bảng full/train được phân biệt.',
  'id': '301cf18eb827d88d'},
 {'cell_type': 'markdown',
  'source': '## 3. Giao thức và năm mô hình hồi quy — Hàn M0–M2, Huy M3–M4\n'
            '\n'
            '**41.365 train / 10.342 test**, seed 0, 5-fold CV trong train. Mỗi fold gồm 33.092 fit và\n'
            '8.273 validation. So sánh cùng fold, target giá gốc và MSE CV trung bình.\n'
            'Scaler/OneHot/Polynomial nằm trong Pipeline, được fit trong từng fold.\n'
            '\n'
            '10 predictor gốc: sáu biến số, ba biến phân loại, một cờ Superhost. Không dùng ID,\n'
            'log giá/price tier, cờ room trùng thông tin, metadata chưa chắc chắn hoặc tọa độ trong core.\n'
            '`dist_bin` là dẫn xuất từ khoảng cách, được bỏ do dư thừa theo giao thức, không phải biến dẫn '
            'xuất từ target.\n'
            '\n'
            'M0: trung bình train (mốc so sánh); M1: tuyến tính sức chứa; M2: tuyến tính đa biến;\n'
            'M3: đa thức bậc 2/3 chỉ trên capacity/bedrooms/dist; M4: Ridge với bảy alpha đã định.\n'
            'M2/M4 có 19 cột sau encoding; M3 bậc 2 có 25, bậc 3 có 35 cột. Chọn biến thể và mô hình\n'
            'bằng CV trước phần đánh giá test. Test đã được mở ở T10 trước đây; lượt này tái lập giao thức\n'
            'đã chốt, không giả vờ có một holdout mới chưa từng xem.',
  'id': 'e9629380d676e67d'},
 {'cell_type': 'code',
  'source': 'def build_pipeline(model_id, config, degree=None, alpha=None):\n'
            '    """\n'
            '    Xây dựng Pipeline khép kín cho từng mô hình hồi quy.\n'
            '    Đảm bảo việc chuẩn hóa và mã hóa biến phân loại chỉ fit trên tập huấn luyện của từng fold.\n'
            '    """\n'
            "    numeric_features = config['predictors']['numeric']\n"
            '\n'
            '    # M0: Mô hình Baseline trung bình (Mean Baseline)\n'
            "    if model_id == 'M0':\n"
            "        return Pipeline([('model', DummyRegressor(strategy='mean'))])\n"
            '\n'
            '    # M1: Mô hình hồi quy đơn biến (SLR) với sức chứa\n'
            "    if model_id == 'M1':\n"
            '        preprocessor = ColumnTransformer(\n'
            "            [('slr', 'passthrough', [config['slr_feature']])],\n"
            "            remainder='drop'\n"
            '        )\n'
            "        return Pipeline([('preprocess', preprocessor), ('model', LinearRegression())])\n"
            '\n'
            '    # Các bước tiền xử lý cho M2, M3, M4\n'
            '    transformers = []\n'
            '\n'
            '    # M3: Mở rộng đa thức cho các biến tương tác (person_capacity, bedrooms, dist)\n'
            "    if model_id == 'M3':\n"
            "        poly_features = config['polynomial_features']\n"
            "        transformers.append(('polynomial', Pipeline([\n"
            "            ('expand', PolynomialFeatures(degree=degree, include_bias=False)),\n"
            "            ('scale', StandardScaler())\n"
            '        ]), poly_features))\n'
            '        numeric_features = [col for col in numeric_features if col not in poly_features]\n'
            '\n'
            '    # Chuẩn hóa biến số và mã hóa One-Hot cho biến phân loại\n'
            '    transformers += [\n'
            "        ('numeric', StandardScaler(), numeric_features),\n"
            "        ('categorical', OneHotEncoder(drop='first', handle_unknown='ignore', "
            'sparse_output=False),\n'
            "         config['predictors']['categorical']),\n"
            "        ('boolean', 'passthrough', config['predictors']['boolean'])\n"
            '    ]\n'
            '\n'
            "    preprocessor = ColumnTransformer(transformers, remainder='drop')\n"
            "    estimator = Ridge(alpha=alpha) if model_id == 'M4' else LinearRegression()\n"
            '\n'
            "    return Pipeline([('preprocess', preprocessor), ('model', estimator)])\n"
            '\n'
            '\n'
            'def evaluate_cv(pipeline, train_data, cv_folds, config, model_id, variant_name):\n'
            '    """\n'
            '    Đánh giá mô hình qua 5-Fold Cross Validation trên tập Train.\n'
            '    Ghi nhận chi tiết kết quả từng fold và giá trị trung bình kèm độ lệch chuẩn.\n'
            '    """\n'
            '    X = train_data[predictor_names(config)]\n'
            "    y = train_data[config['target']]\n"
            '\n'
            '    cv_results = cross_validate(\n'
            '        pipeline, X, y, cv=cv_folds,\n'
            "        scoring={'mse': 'neg_mean_squared_error', 'mae': 'neg_mean_absolute_error', 'r2': "
            "'r2'},\n"
            "        return_train_score=True, n_jobs=1, error_score='raise'\n"
            '    )\n'
            '\n'
            '    fold_records = []\n'
            '    for fold_idx in range(len(cv_folds)):\n'
            '        record = {\n'
            "            'model_id': model_id,\n"
            "            'variant': variant_name,\n"
            "            'fold': fold_idx,\n"
            "            'n_fold_train': len(cv_folds[fold_idx][0]),\n"
            "            'n_fold_validation': len(cv_folds[fold_idx][1]),\n"
            "            'protocol_id': config['protocol_id']\n"
            '        }\n'
            "        for split_key, prefix in [('test', 'validation'), ('train', 'train')]:\n"
            "            record[f'{prefix}_mse'] = -cv_results[f'{split_key}_mse'][fold_idx]\n"
            "            record[f'{prefix}_rmse'] = np.sqrt(record[f'{prefix}_mse'])\n"
            "            record[f'{prefix}_mae'] = -cv_results[f'{split_key}_mae'][fold_idx]\n"
            "            record[f'{prefix}_r2'] = cv_results[f'{split_key}_r2'][fold_idx]\n"
            '        fold_records.append(record)\n'
            '\n'
            '    df_folds = pd.DataFrame(fold_records)\n'
            '    summary = {\n'
            "        'model_id': model_id,\n"
            "        'variant': variant_name,\n"
            "        'protocol_id': config['protocol_id'],\n"
            "        'n_train': len(train_data),\n"
            "        'n_folds': len(cv_folds)\n"
            '    }\n'
            "    for split_key, prefix in [('validation', 'cv'), ('train', 'fold_train')]:\n"
            "        for metric in ['mse', 'rmse', 'mae', 'r2']:\n"
            "            summary[f'{prefix}_{metric}_mean'] = df_folds[f'{split_key}_{metric}'].mean()\n"
            "            summary[f'{prefix}_{metric}_std'] = df_folds[f'{split_key}_{metric}'].std(ddof=1)\n"
            '\n'
            '    return summary, df_folds\n',
  'id': '92184cb244193f3f'},
 {'cell_type': 'code',
  'source': "X_train, y_train = train[predictor_names(config)], train[config['target']]\n"
            "specs = [('M0', 'mean_baseline', {}), ('M1', 'slr_person_capacity', {}), ('M2', 'mlr_core', "
            '{})]\n'
            "specs += [('M3', f'degree_{d}', {'degree': d}) for d in config['polynomial_degrees']]\n"
            "specs += [('M4', f'alpha_{a:g}', {'alpha': a}) for a in config['ridge_alphas']]\n"
            'cv_rows, fold_rows = [], []\n'
            'for model_id, variant, params in specs:\n'
            '    pipeline = build_pipeline(model_id, config, **params)\n'
            '    summary, detail = evaluate_cv(pipeline, train, cv, config, model_id, variant)\n'
            '    cv_rows.append({**summary, **params})\n'
            '    fold_rows.append(detail)\n'
            "    print(model_id, variant, 'CV MSE =', round(summary['cv_mse_mean'], 2))\n"
            'cv_summary = pd.DataFrame(cv_rows)\n'
            'cv_folds = pd.concat(fold_rows, ignore_index=True)\n'
            'assert len(cv_summary) == 12 and len(cv_folds) == 60\n'
            "display(cv_summary[['model_id', 'variant', 'fold_train_mse_mean', 'cv_mse_mean',\n"
            "                    'cv_mse_std', 'cv_rmse_mean', 'cv_mae_mean', 'cv_r2_mean']])\n"
            "save_table(cv_summary, 'all_configurations_cv.csv')\n"
            "save_table(cv_folds, 'all_configurations_folds.csv')",
  'id': '760203f0f86f3c36'},
 {'cell_type': 'markdown',
  'source': '`cross_validate` gọi điểm validation là `test_*`; hàm đã đổi tên để không nhầm holdout.\n'
            'MSE/MAE scorer có dấu âm được đổi về dương, R² giữ nguyên. Mean RMSE của folds không nhất\n'
            'thiết bằng căn mean MSE. Chênh train/CV phản ánh sai số trong cấu hình này; chưa đủ để\n'
            'tuyên bố chắc chắn mô hình không overfit.',
  'id': '843a2d4b386fdc6d'},
 {'cell_type': 'code',
  'source': "selected_cv = cv_summary.loc[cv_summary.groupby('model_id').cv_mse_mean.idxmin()].copy()\n"
            "winner_id = selected_cv.loc[selected_cv.cv_mse_mean.idxmin(), 'model_id']\n"
            "selected_cv['selected_winning_model'] = selected_cv.model_id.eq(winner_id)\n"
            'models = {}\n'
            'for row in selected_cv.itertuples():\n'
            "    params = {'degree': int(row.degree)} if row.model_id == 'M3' else (\n"
            "             {'alpha': float(row.alpha)} if row.model_id == 'M4' else {})\n"
            '    model = build_pipeline(row.model_id, config, **params)\n'
            '    model.fit(X_train, y_train)  # Refit chỉ toàn bộ train sau chọn CV.\n'
            '    models[row.model_id] = model\n'
            "display(selected_cv[['model_id', 'variant', 'cv_mse_mean', 'selected_winning_model']])\n"
            "print('Mô hình khóa bằng CV:', winner_id)\n"
            "assert winner_id == 'M3'\n"
            "assert int(selected_cv.loc[selected_cv.model_id.eq('M3'), 'degree'].iloc[0]) == 3\n"
            "assert float(selected_cv.loc[selected_cv.model_id.eq('M4'), 'alpha'].iloc[0]) == .1",
  'id': '595195a76aad1aed'},
 {'cell_type': 'markdown',
  'source': '### 3.1. Phương trình hồi quy và phân tích hệ số (M1, M2) — Hàn phụ trách\n'
            '\n'
            '- **Mô hình M1 (Hồi quy đơn biến):** Sử dụng duy nhất `person_capacity` trên thang đo gốc ban '
            'đầu.\n'
            '  - Phương trình có dạng: $\\widehat{\\text{realSum}} = \\beta_0 + \\beta_1 \\times '
            '\\text{person\\_capacity}$.\n'
            '  - Hệ số chặn $\\beta_0$ thể hiện giá trị lý thuyết của phương trình khi sức chứa bằng 0.\n'
            '- **Mô hình M2 (Hồi quy đa biến tuyến tính):** Sử dụng toàn bộ 10 biến đặc trưng (sau One-Hot '
            'Encoding tạo thành 19 cột).\n'
            '  - Các biến số liên tục được chuẩn hóa qua `StandardScaler`, vì vậy hệ số $\\beta$ phản ánh '
            'mức thay đổi kỳ vọng của giá khi biến độc lập tăng 1 độ lệch chuẩn ($\\sigma$).\n'
            '  - Để hỗ trợ người đọc diễn giải thực tế, nhóm chia hệ số chuẩn hóa cho giá trị scale tương '
            'ứng ($\\sigma$) để thu được mức biến thiên theo đơn vị gốc ban đầu (ví dụ: mỗi km khoảng cách, '
            'mỗi khách sức chứa).\n'
            '  - Các biến phân loại được so sánh với nhóm tham chiếu mặc định (nhóm bị loại bỏ đầu tiên '
            'trong One-Hot Encoding).\n',
  'id': '4f6ce9f39501d550'},
 {'cell_type': 'code',
  'source': '# 1. Trích xuất phương trình hồi quy đơn biến M1\n'
            "model_m1 = models['M1'].named_steps['model']\n"
            'print("=" * 60)\n'
            'print("PHƯƠNG TRÌNH HỒI QUY ĐƠN BIẾN M1:")\n'
            'print(f"  realSum_hat = {model_m1.intercept_:.4f} + {model_m1.coef_[0]:.4f} * '
            'person_capacity")\n'
            'print("=" * 60)\n'
            '\n'
            '# 2. Trích xuất bảng hệ số hồi quy đa biến M2\n'
            "model_m2 = models['M2']\n"
            "m2_feature_names = model_m2.named_steps['preprocess'].get_feature_names_out()\n"
            'coefficients = pd.DataFrame({\n'
            "    'feature': m2_feature_names,\n"
            "    'coefficient': model_m2.named_steps['model'].coef_\n"
            '})\n'
            '\n'
            '# Tính hệ số theo đơn vị gốc cho các biến số\n'
            "m2_scaler = model_m2.named_steps['preprocess'].named_transformers_['numeric']\n"
            "coefficients['coefficient_per_original_unit'] = np.nan\n"
            "is_numeric = coefficients.feature.str.startswith('numeric__')\n"
            "coefficients.loc[is_numeric, 'coefficient_per_original_unit'] = (\n"
            "    coefficients.loc[is_numeric, 'coefficient'].to_numpy() / m2_scaler.scale_\n"
            ')\n'
            '\n'
            'print(f"\\nHệ số chặn (Intercept) của mô hình M2: '
            '{model_m2.named_steps[\'model\'].intercept_:.4f}")\n'
            "m2_encoder = model_m2.named_steps['preprocess'].named_transformers_['categorical']\n"
            'reference_groups = {name: categories[0] for name, categories in '
            "zip(config['predictors']['categorical'], m2_encoder.categories_)}\n"
            'print(f"Nhóm tham chiếu mặc định: {reference_groups}")\n'
            '\n'
            'print("\\nBảng hệ số các thuộc tính trong mô hình M2:")\n'
            'display(coefficients)\n'
            '\n'
            "for m_id in ['M2', 'M3', 'M4']:\n"
            "    n_cols = models[m_id].named_steps['preprocess'].transform(X_train.iloc[:1]).shape[1]\n"
            '    print(f"-> {m_id}: Số lượng đặc trưng sau tiền xử lý/mã hóa = {n_cols} cột")\n',
  'id': '6ea78f41ebee6891'},
 {'cell_type': 'markdown',
  'source': '## 4. Đánh giá holdout chung — Hàn và Huy\n'
            '\n'
            'Chỉ predict từ các model đã refit train. MSE = mean((actual−predicted)²), RMSE = sqrt(MSE),\n'
            'MAE = mean(|actual−predicted|), R² = 1−SSE/SST. Không tune bậc/alpha/split/biến sau test.\n'
            'MSE có đơn vị bình phương; RMSE/MAE cùng đơn vị với realSum; R² không phải phần trăm accuracy.',
  'id': '50d77d567503ccff'},
 {'cell_type': 'code',
  'source': "X_test, y_test = test[predictor_names(config)], test[config['target']]\n"
            'comparison_rows, prediction_frames = [], []\n'
            'for row in selected_cv.itertuples():\n'
            '    predicted = models[row.model_id].predict(X_test)\n'
            '    mse = mean_squared_error(y_test, predicted)\n'
            "    comparison_rows.append({'model_id': row.model_id, 'variant': row.variant,\n"
            "        'protocol_id': config['protocol_id'], 'n_train': len(train), 'n_test': len(test),\n"
            "        'cv_mse_mean': row.cv_mse_mean, 'cv_rmse_mean': row.cv_rmse_mean,\n"
            "        'cv_mae_mean': row.cv_mae_mean, 'cv_r2_mean': row.cv_r2_mean,\n"
            "        'test_mse': mse, 'test_rmse': np.sqrt(mse),\n"
            "        'test_mae': mean_absolute_error(y_test, predicted), 'test_r2': r2_score(y_test, "
            'predicted),\n'
            "        'selected_winning_model': row.model_id == winner_id})\n"
            '    part = test.copy()\n'
            "    part['actual'], part['predicted'] = y_test.to_numpy(), predicted\n"
            "    part['residual'] = part.actual - part.predicted\n"
            "    part['model_id'], part['split'], part['protocol_id'] = row.model_id, 'test', "
            "config['protocol_id']\n"
            '    prediction_frames.append(part)\n'
            'comparison = pd.DataFrame(comparison_rows)\n'
            'predictions = pd.concat(prediction_frames, ignore_index=True)\n'
            'assert len(predictions) == 5 * 10342\n'
            "assert not predictions.duplicated(['model_id', 'source_file', 'source_row']).any()\n"
            "display(comparison[['model_id', 'variant', 'cv_mse_mean', 'test_mse', 'test_rmse', 'test_mae',\n"
            "                    'test_r2', 'selected_winning_model']])\n"
            "save_table(comparison, 'model_comparison.csv')\n"
            "save_table(predictions, 'test_predictions.csv')\n"
            'fig, ax = plt.subplots(figsize=(9, 4))\n'
            "comparison.set_index('model_id')[['cv_mse_mean', 'test_mse']].plot.bar(ax=ax)\n"
            "ax.set(title='Cùng thang giá và giao thức', ylabel='MSE')\n"
            'plt.tight_layout(); plt.show()',
  'id': '57f86d75ea6ab14c'},
 {'cell_type': 'markdown',
  'source': '## 5. Phần dư, lỗi theo nhóm và kết luận — Huy, Hàn kiểm tra\n'
            '\n'
            'Residual = actual−predicted: dương nghĩa là dự đoán thấp. Phân tích mô hình đã khóa bằng CV.\n'
            'Giữ dự đoán âm để phản ánh giới hạn; không clip sau khi nhìn test. Báo lỗi kèm số mẫu từng '
            'nhóm.\n'
            'Các case sai số lớn được truy lại file/dòng, không gọi là gian lận hoặc giá sai.',
  'id': '2858c39da8d69897'},
 {'cell_type': 'code',
  'source': 'winner = predictions.loc[predictions.model_id.eq(winner_id)].copy()\n'
            'assert len(winner) == 10342\n'
            "pd.testing.assert_frame_equal(winner[config['trace_keys']].reset_index(drop=True), "
            "test[config['trace_keys']])\n"
            'np.testing.assert_allclose(winner.actual, test.realSum, rtol=0, atol=0)\n'
            "winner['abs_residual'] = winner.residual.abs()\n"
            "winner['squared_residual'] = winner.residual ** 2\n"
            'def group_error(frame):\n'
            "    return {'n': len(frame), 'rmse': np.sqrt(frame.squared_residual.mean()),\n"
            "            'mae': frame.abs_residual.mean(), 'mean_residual': frame.residual.mean(),\n"
            "            'negative_predictions': int(frame.predicted.lt(0).sum())}\n"
            'error_rows = []\n'
            "for cols in [['city'], ['room_type'], ['day_type'], ['city', 'room_type']]:\n"
            '    for key, part in winner.groupby(cols, observed=True):\n'
            '        keys = key if isinstance(key, tuple) else (key,)\n'
            "        error_rows.append({'grouping': '+'.join(cols), **dict(zip(cols, keys)), "
            '**group_error(part)})\n'
            'group_errors = pd.DataFrame(error_rows)\n'
            "display(group_errors.loc[group_errors.grouping.isin(['city', 'room_type', 'day_type'])])\n"
            "save_table(group_errors, 'residual_group_errors.csv')\n"
            'fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n'
            'axes[0].scatter(winner.predicted, winner.residual, s=5, alpha=.2)\n'
            "axes[0].axhline(0, color='red')\n"
            "axes[0].set(xlabel='Predicted', ylabel='Actual − predicted', title=f'{winner_id}: toàn bộ "
            "holdout')\n"
            'axes[1].scatter(winner.actual, winner.predicted, s=5, alpha=.2)\n'
            'low, high = min(winner.actual.min(), winner.predicted.min()), max(winner.actual.max(), '
            'winner.predicted.max())\n'
            "axes[1].plot([low, high], [low, high], color='red')\n"
            "axes[1].set(xlabel='Actual', ylabel='Predicted', title='Đường chéo: actual = predicted')\n"
            'plt.tight_layout(); plt.show()\n'
            'fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n'
            "for ax, col in zip(axes, ['city', 'room_type']):\n"
            "    part = group_errors.loc[group_errors.grouping.eq(col)].sort_values('rmse')\n"
            '    ax.barh([f\'{r[col]} (n={int(r["n"])})\' for _,r in part.iterrows()], part.rmse)\n'
            "    ax.set(xlabel='RMSE', title=f'Lỗi theo {col}, kèm n')\n"
            'plt.tight_layout(); plt.show()',
  'id': '6d2db0181409c8d7'},
 {'cell_type': 'code',
  'source': "ordered = winner.sort_values('squared_residual', ascending=False)\n"
            'top_n = int(np.ceil(len(winner)*.01))\n'
            'top_share = ordered.head(top_n).squared_residual.sum()/winner.squared_residual.sum()\n'
            "cases = ordered.head(10)[['source_file', 'source_row', 'city', 'room_type', 'person_capacity',\n"
            "                          'bedrooms', 'dist', 'actual', 'predicted', 'residual']]\n"
            'display(cases)\n'
            "save_table(cases, 'residual_cases.csv')\n"
            'case = cases.iloc[0]\n'
            "raw_case = pd.read_csv(ROOT / 'data/raw' / case.source_file)\n"
            "raw_case = raw_case.loc[raw_case['Unnamed: 0'].eq(case.source_row)]\n"
            'assert len(raw_case) == 1\n'
            'np.testing.assert_allclose(raw_case.realSum.iloc[0], case.actual, rtol=0, atol=0)\n'
            'display(raw_case)\n'
            "print(f'{top_n} dòng lỗi bình phương lớn nhất ({top_n/len(winner):.2%} mẫu) chiếm "
            "{top_share:.2%} SSE.')\n"
            "print('Số dự đoán âm:', winner.predicted.lt(0).sum())\n"
            "print('Mean residual:', winner.residual.mean(), '| Median AE:', winner.abs_residual.median(),\n"
            "      '| P90 AE:', winner.abs_residual.quantile(.9))\n"
            'fig, ax = plt.subplots(figsize=(9, 4))\n'
            'ax.plot(np.arange(1, len(ordered)+1)/len(ordered)*100,\n'
            '        ordered.squared_residual.cumsum()/ordered.squared_residual.sum()*100)\n'
            "ax.set(xlabel='% dòng, xếp theo lỗi bình phương giảm dần', ylabel='% SSE lũy tích',\n"
            "       title='Mức tập trung sai số; giữ nguyên mọi dòng test', xlim=(0,100), ylim=(0,100))\n"
            'plt.tight_layout(); plt.show()',
  'id': '5f6b9a6ea41d7550'},
 {'cell_type': 'code',
  'source': 'selected = comparison.loc[comparison.model_id.eq(winner_id)].iloc[0]\n'
            "baseline = comparison.loc[comparison.model_id.eq('M0')].iloc[0]\n"
            'improvement = (baseline.test_mse-selected.test_mse)/baseline.test_mse*100\n'
            'display(Markdown(f"""### 5.1. Kết luận từ kết quả thực nghiệm\n'
            '\n'
            'Phân tích **{len(df):,} quan sát** cho thấy giá lệch phải và mẫu khác cơ cấu giữa các nhóm.\n'
            'Mean/median/n, Pearson theo city và ANOVA giúp mô tả những liên hệ này, với giới hạn giả định '
            'rõ ràng.\n'
            '**{winner_id}, đa thức bậc 3**, được chọn bằng CV MSE, không chọn theo điểm test.\n'
            'Trên **{len(test):,} holdout**, RMSE **{selected.test_rmse:.2f}**, MAE '
            '**{selected.test_mae:.2f}**,\n'
            'R² **{selected.test_r2:.4f}**; MSE giảm **{improvement:.2f}%** so với baseline M0 trên cùng '
            'test.\n'
            'Mức giải thích biến thiên còn thấp và có **{int(winner.predicted.lt(0).sum())} dự đoán âm**.\n'
            '**{top_n} dòng lỗi lớn nhất** chiếm **{top_share:.2%} SSE**, cho thấy ít quan sát có thể chi '
            'phối MSE.\n'
            'Thiếu metadata kỳ giá/listing ID và khả năng lặp tọa độ giữa train/test hạn chế khả năng khái '
            'quát.\n'
            'Kết quả chưa chứng minh nhân quả, gian lận hoặc chất lượng định giá ở một thị trường khác.\n'
            '"""))',
  'id': '88f453e1a21e5050'},
 {'cell_type': 'markdown',
  'source': '## 6. Phân công, kiểm tra và cách trình bày\n'
            '\n'
            '### 6.1. Bảng phân công nhiệm vụ chi tiết giữa các thành viên\n'
            '\n'
            '| Nội dung thực hiện | Thành viên chủ trì | Chi tiết công việc và đóng góp cụ thể |\n'
            '|---|---|---|\n'
            '| **1. Dữ liệu và Kiểm toán chất lượng** | **Hàn** | Nạp 20 file CSV, kiểm tra schema, tạo khóa '
            'truy vết (`source_file`, `source_row`), xây dựng từ điển dữ liệu, kiểm toán 12 tiêu chí chất '
            'lượng, tính IQR phân phối giá và phân nhóm mô tả. |\n'
            '| **2. Phân tích khám phá (EDA)** | **Huy** | Phân tích cơ cấu số mẫu theo thành phố/loại '
            'phòng, so sánh giá giữa ngày thường và cuối tuần, tính tương quan Pearson trên toàn bộ và từng '
            'thành phố, thực hiện kiểm định ANOVA một nhân tố. |\n'
            '| **3. Thiết lập giao thức thực nghiệm** | **Cả hai thành viên** | Thống nhất chia tập 80% '
            'Train / 20% Test, cấu hình 5-Fold Cross Validation trên tập Train, lựa chọn allowlist 10 đặc '
            'trưng cốt lõi nhằm chống rò rỉ dữ liệu. |\n'
            '| **4. Mô hình cơ sở (M0, M1, M2)** | **Hàn** | Xây dựng Pipeline cho DummyRegressor (M0), Hồi '
            'quy đơn biến (M1), Hồi quy đa biến tuyến tính (M2); trích xuất phương trình hồi quy và phân '
            'tích bảng hệ số theo đơn vị gốc. |\n'
            '| **5. Mô hình nâng cao (M3, M4)** | **Huy** | Xây dựng Pipeline hồi quy đa thức bậc 2 & 3 '
            '(M3), hồi quy Ridge với các tham số $\\alpha$ khác nhau (M4); đánh giá 5-Fold CV để chọn cấu '
            'hình tối ưu. |\n'
            '| **6. Đánh giá trên tập Holdout Test** | **Cả hai thành viên** | Refit các mô hình tối ưu trên '
            'toàn bộ 41.365 mẫu Train, kiểm tra độc lập trên 10.342 mẫu Test bằng 4 chỉ số (MSE, RMSE, MAE, '
            '$R^2$), đối chiếu hiệu năng với Baseline M0. |\n'
            '| **7. Phân tích phần dư & Giới hạn** | **Huy** | Tính toán phần dư, phân tích nồng độ sai số '
            'của 1% mẫu có lỗi bình phương lớn nhất, truy vết mẫu gốc và phân tích nguyên nhân các trường '
            'hợp dự đoán âm. |\n'
            '| **8. Báo cáo tổng kết & Slide thuyết trình** | **Cả hai thành viên** | Đọc chéo, đối chiếu '
            '100% số liệu giữa Notebook và Báo cáo nghiệm thu; chuẩn bị slide thuyết trình đồ án và kịch bản '
            'vấn đáp. |\n'
            '\n'
            '---\n'
            '\n'
            '### 6.2. Hướng dẫn môi trường và tái lập kết quả đồ án (Reproducibility Guide)\n'
            '\n'
            '- **Môi trường yêu cầu:** Python phiên bản 3.10 trở lên.\n'
            '- **Các thư viện chính:** `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, '
            '`ipython`.\n'
            '- **Cách thức thực thi:**\n'
            '  1. Đảm bảo cấu trúc thư mục chứa đầy đủ `data/raw/` (20 tệp CSV) và '
            '`config/experiment_config.json`.\n'
            '  2. Mở tệp notebook `IE313_Airbnb_Final.ipynb` trong môi trường Jupyter Notebook hoặc VS '
            'Code.\n'
            '  3. Chọn lệnh **Kernel -> Restart Kernel and Run All Cells**.\n'
            '  4. Quá trình tính toán chạy tuần tự từ Cell 0 đến Cell cuối cùng trong khoảng 2–3 phút mà '
            'không yêu cầu thêm bất kỳ thao tác thủ công nào.\n',
  'id': 'bfd590228a7cf6d'},
 {'cell_type': 'code',
  'source': '# Tổng kết và in các chỉ số thực nghiệm chính của toàn bộ đồ án\n'
            'print("=" * 80)\n'
            'print("TỔNG KẾT KẾT QUẢ THỰC NGHIỆM ĐỒ ÁN IE313")\n'
            'print("=" * 80)\n'
            '\n'
            'print(f"1. Quy mô dữ liệu: {len(df):,} quan sát từ {len(raw_csv_files)} tệp CSV thô.")\n'
            'print(f"2. Giao thức phân chia: {len(train):,} mẫu Train (80%) | {len(test):,} mẫu Test '
            '(20%).")\n'
            'print(f"3. Đánh giá 5-Fold Cross Validation trên tập Train: hoàn tất 12 cấu hình mô hình.")\n'
            'print(f"4. Mô hình được chọn qua 5-Fold CV: {winner_id} (Đa thức bậc 3).")\n'
            'print(f"   -> Điểm CV MSE trung bình: {selected_cv.loc[selected_cv.model_id.eq(winner_id), '
            '\'cv_mse_mean\'].iloc[0]:,.2f}")\n'
            '\n'
            'print("\\n5. Hiệu năng kiểm tra độc lập trên tập Holdout Test (10.342 mẫu):")\n'
            'print(f"   - MSE  : {selected.test_mse:,.2f} (Cải thiện {improvement:.2f}% so với Baseline '
            'M0)")\n'
            'print(f"   - RMSE : {selected.test_rmse:,.2f} EUR")\n'
            'print(f"   - MAE  : {selected.test_mae:,.2f} EUR")\n'
            'print(f"   - R²   : {selected.test_r2:.4f}")\n'
            '\n'
            'print(f"\\n6. Phân tích phần dư & giới hạn mô hình:")\n'
            'print(f"   - Số trường hợp dự đoán âm: {int(winner.predicted.lt(0).sum())} mẫu (chiếm '
            '{winner.predicted.lt(0).sum()/len(winner):.2%})")\n'
            'print(f"   - Nồng độ sai số: {top_n} mẫu sai số lớn nhất (1% mẫu) chiếm {top_share:.2%} tổng '
            'bình phương phần dư (SSE).")\n'
            'print("=" * 80)\n'
            'print("-> ĐÃ HOÀN TẤT THỰC THI TOÀN BỘ NOTEBOOK THÀNH CÔNG VÀ NHẤT QUÁN.")\n',
  'id': '955e52439ab0148e'}]
