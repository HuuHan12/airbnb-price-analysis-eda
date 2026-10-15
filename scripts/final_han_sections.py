"""Reviewed Han notebook sections from 67fb260, embedded by the builder.

No runtime dependency: the generated notebook contains these cells directly.
Unsupported coordinate/luxury claims are corrected; no model parameters change.
"""
HAN_SECTIONS = {5: '### 1.1. Kiểm toán chất lượng dữ liệu trước khi phân tích\n'
    '\n'
    'Trong phân tích dữ liệu, việc tập dữ liệu không chứa ô trống (`NaN`) chưa đủ để khẳng định dữ liệu hoàn '
    'toàn hợp lệ. Nhóm thực hiện kiểm toán sâu trên các khía cạnh:\n'
    '- **Tính hợp lý của giá trị số:** Giá thuê (`realSum`) phải là số dương ($> 0$), khoảng cách (`dist`, '
    '`metro_dist`) không được âm, tọa độ địa lý phải nằm trong miền lat/lng hợp lệ (chưa xác minh hệ tọa độ '
    'gốc).\n'
    '- **Tính toàn vẹn logic:** Các cờ logic loại phòng (`room_shared`, `room_private`) phải hoàn toàn nhất '
    'quán với giá trị của cột `room_type`.\n'
    '- **Ký tự khuyết ẩn:** Kiểm tra các chuỗi đặc biệt thường dùng biểu diễn giá trị thiếu như `null`, '
    '`none`, `n/a`, `nan`, `?`.\n'
    '- **Tính duy nhất của khóa truy vết:** Cặp (`source_file`, `source_row`) phải là duy nhất trên toàn bộ '
    'tập dữ liệu để đảm bảo khả năng truy xuất ngược.\n',
 6: 'def audit_data_quality(dataframe):\n'
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
    "        ('12. Khoảng cách âm (dist hoặc metro_dist < 0)', int((dataframe[['dist', 'metro_dist']] < "
    '0).sum().sum())),\n'
    "        ('13. Tọa độ ngoài miền lat/lng hợp lệ', int((~(dataframe.lat.between(-90, 90) & "
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
    '\'lng\']).sum():,} (chưa xác minh nguyên nhân lặp; không coi tọa độ là listing ID)")\n'
    'print(f"-> Khoảng cách metro nhỏ nhất ghi nhận: {df.metro_dist.min():.4f} km")\n'
    "display(df.select_dtypes(include='number').describe().T)\n"
    '\n'
    "assert quality_report['Số lượng vi phạm'].eq(0).all(), 'Có vi phạm dữ liệu cần kiểm lại'\n",
 8: 'def calculate_price_iqr(frame):\n'
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
 10: 'descriptive = df.copy()\n'
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
     "display(pd.crosstab(descriptive.dist_bin, descriptive.price_tier, margins=True, margins_name='Tổng'))\n"
     '\n'
     "assert not descriptive[['dist_bin', 'price_tier']].isna().any().any()\n"
     'assert df.shape == (51707, 24)\n',
 11: '### 1.4. Tổng kết hiện trạng dữ liệu trước khi phân tích\n'
     '\n'
     '- **Điểm mạnh:**\n'
     '  - Quy mô mẫu lớn với 51.707 quan sát phủ khắp 10 thành phố lớn tại châu Âu.\n'
     '  - Cấu trúc dữ liệu đồng nhất trên toàn bộ 20 tệp nguồn; không có giá trị khuyết thiếu trong tập dữ '
     'liệu cung cấp.\n'
     '  - Đầy đủ cả 2 điều kiện khảo sát (ngày thường và cuối tuần) cho từng thành phố.\n'
     '  - Đã thiết lập khóa truy vết (`source_file`, `source_row`) cho phép đối chiếu ngược lại từng dòng '
     'gốc khi kiểm tra sai số mô hình.\n'
     '\n'
     '- **Thách thức và giới hạn:**\n'
     '  - Phân phối giá lệch phải mạnh, tồn tại các căn hộ giá thuê rất cao. Do đó, cần luôn báo cáo song '
     'song cả Trung vị (Median) và IQR bên cạnh Trung bình (Mean).\n'
     '  - Tỷ lệ các loại phòng chênh lệch lớn (Entire home/apt chiếm ~63%, Private room ~36%, trong khi '
     'Shared room chỉ chiếm 0.71%).\n'
     '  - Tồn tại các trường hợp lặp tọa độ địa lý (chưa xác minh nguyên nhân hoặc listing ID).\n'
     '  - Kết quả phân tích áp dụng cho tập dữ liệu khảo sát được cung cấp, không đại diện hoàn toàn cho '
     'toàn bộ thị trường lưu trú châu Âu tại mọi thời điểm.\n'
     '\n'
     '- Metadata kỳ giá và định nghĩa chi tiết multi/biz/index chưa được nguồn gốc xác minh. Bản nộp chỉ '
     'kiểm CSV gộp, không đọc lại các tệp raw.\n',
 23: 'def build_pipeline(model_id, config, degree=None, alpha=None):\n'
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
     "        ('categorical', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False),\n"
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
     "        scoring={'mse': 'neg_mean_squared_error', 'mae': 'neg_mean_absolute_error', 'r2': 'r2'},\n"
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
 27: '### 3.1. Phương trình hồi quy và phân tích hệ số (M1, M2) — Hàn phụ trách\n'
     '\n'
     '- **Mô hình M1 (Hồi quy đơn biến):** Sử dụng duy nhất `person_capacity` trên thang đo gốc ban đầu.\n'
     '  - Phương trình có dạng: $\\widehat{\\text{realSum}} = \\beta_0 + \\beta_1 \\times '
     '\\text{person\\_capacity}$.\n'
     '  - Hệ số chặn $\\beta_0$ thể hiện giá trị lý thuyết của phương trình khi sức chứa bằng 0.\n'
     '- **Mô hình M2 (Hồi quy đa biến tuyến tính):** Sử dụng toàn bộ 10 biến đặc trưng (sau One-Hot Encoding '
     'tạo thành 19 cột).\n'
     '  - Các biến số liên tục được chuẩn hóa qua `StandardScaler`, vì vậy hệ số $\\beta$ phản ánh mức thay '
     'đổi kỳ vọng của giá khi biến độc lập tăng 1 độ lệch chuẩn ($\\sigma$).\n'
     '  - Để hỗ trợ người đọc diễn giải thực tế, nhóm chia hệ số chuẩn hóa cho giá trị scale tương ứng '
     '($\\sigma$) để thu được mức biến thiên theo đơn vị gốc ban đầu (ví dụ: mỗi km khoảng cách, mỗi khách '
     'sức chứa).\n'
     '  - Các biến phân loại được so sánh với nhóm tham chiếu mặc định (nhóm bị loại bỏ đầu tiên trong '
     'One-Hot Encoding).\n',
 28: '# 1. Trích xuất phương trình hồi quy đơn biến M1\n'
     "model_m1 = models['M1'].named_steps['model']\n"
     'print("=" * 60)\n'
     'print("PHƯƠNG TRÌNH HỒI QUY ĐƠN BIẾN M1:")\n'
     'print(f"  realSum_hat = {model_m1.intercept_:.4f} + {model_m1.coef_[0]:.4f} * person_capacity")\n'
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
     'print(f"\\nHệ số chặn (Intercept) của mô hình M2: {model_m2.named_steps[\'model\'].intercept_:.4f}")\n'
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
 35: '## 6. Phân công, kiểm tra và cách trình bày\n'
     '\n'
     '### 6.1. Bảng phân công nhiệm vụ chi tiết giữa các thành viên\n'
     '\n'
     '| Nội dung thực hiện | Thành viên chủ trì | Chi tiết công việc và đóng góp cụ thể |\n'
     '|---|---|---|\n'
     '| **1. Dữ liệu và Kiểm toán chất lượng** | **Hàn** | Chuẩn bị 20 CSV nguồn ở giai đoạn phát triển; bản '
     'nộp nạp CSV gộp, kiểm tra schema, tạo khóa truy vết (`source_file`, `source_row`), xây dựng từ điển dữ '
     'liệu, kiểm toán 12 tiêu chí chất lượng, tính IQR phân phối giá và phân nhóm mô tả. |\n'
     '| **2. Phân tích khám phá (EDA)** | **Huy** | Phân tích cơ cấu số mẫu theo thành phố/loại phòng, so '
     'sánh giá giữa ngày thường và cuối tuần, tính tương quan Pearson trên toàn bộ và từng thành phố, thực '
     'hiện kiểm định ANOVA một nhân tố. |\n'
     '| **3. Thiết lập giao thức thực nghiệm** | **Cả hai thành viên** | Thống nhất chia tập 80% Train / 20% '
     'Test, cấu hình 5-Fold Cross Validation trên tập Train, lựa chọn allowlist 10 đặc trưng cốt lõi nhằm '
     'chống rò rỉ dữ liệu. |\n'
     '| **4. Mô hình cơ sở (M0, M1, M2)** | **Hàn** | Xây dựng Pipeline cho DummyRegressor (M0), Hồi quy đơn '
     'biến (M1), Hồi quy đa biến tuyến tính (M2); trích xuất phương trình hồi quy và phân tích bảng hệ số '
     'theo đơn vị gốc. |\n'
     '| **5. Mô hình nâng cao (M3, M4)** | **Huy** | Xây dựng Pipeline hồi quy đa thức bậc 2 & 3 (M3), hồi '
     'quy Ridge với các tham số $\\alpha$ khác nhau (M4); đánh giá 5-Fold CV để chọn cấu hình tối ưu. |\n'
     '| **6. Đánh giá trên tập Holdout Test** | **Cả hai thành viên** | Refit các mô hình tối ưu trên toàn '
     'bộ 41.365 mẫu Train, kiểm tra trên holdout 10.342 dòng (chưa xác minh độc lập theo listing) bằng 4 chỉ '
     'số (MSE, RMSE, MAE, $R^2$), đối chiếu hiệu năng với Baseline M0. |\n'
     '| **7. Phân tích phần dư & Giới hạn** | **Huy** | Tính toán phần dư, phân tích nồng độ sai số của 1% '
     'mẫu có lỗi bình phương lớn nhất, truy vết mẫu gốc và phân tích nguyên nhân các trường hợp dự đoán âm. '
     '|\n'
     '| **8. Báo cáo tổng kết & Slide thuyết trình** | **Cả hai thành viên** | Đọc chéo và đối chiếu số liệu '
     'giữa Notebook và báo cáo; chuẩn bị slide thuyết trình đồ án và kịch bản vấn đáp. |\n'
     '\n'
     '---\n'
     '\n'
     '### 6.2. Hướng dẫn chạy bộ hai file\n'
     '\n'
     'Đặt `IE313_Airbnb_Final.ipynb` và `airbnb_combined.csv` cùng thư mục, mở kernel tại đó và chọn '
     '**Restart Kernel and Run All**. Dùng môi trường Python/thư viện đã ghi ở đầu notebook. Không cần JSON, '
     'manifest ngoài, src, 20 CSV nguồn hoặc model lưu sẵn; không ghi file trung gian. Cấu hình và '
     'split/fold nằm trong bộ nhớ; digest xác minh khớp manifest đã chốt. Kết quả hiển thị trực tiếp để '
     'trình bày, không cần chạy lại lúc thuyết trình.\n'
     '\n'
     'Phân công trên ghi nhận công việc nhóm; kiểm tự động không xác nhận thay việc diễn tập, kiểm trên máy '
     'Hàn, metadata hoặc nộp LMS. Các phần pipeline và M0–M2 giữ cách trình bày Hàn cập nhật ở commit '
     '67fb260; dictionary giữ metadata đã review để tránh suy diễn về bedrooms=0/index.\n',
 36: '# Tổng kết và in các chỉ số thực nghiệm chính của toàn bộ đồ án\n'
     'print("=" * 80)\n'
     'print("TỔNG KẾT KẾT QUẢ THỰC NGHIỆM ĐỒ ÁN IE313")\n'
     'print("=" * 80)\n'
     '\n'
     'print(f"1. Quy mô dữ liệu: {len(df):,} quan sát từ {len(inventory)} nhóm nguồn trong CSV gộp.")\n'
     'print(f"2. Giao thức phân chia: {len(train):,} mẫu Train (80%) | {len(test):,} mẫu Test (20%).")\n'
     'print(f"3. Đánh giá 5-Fold Cross Validation trên tập Train: hoàn tất 12 cấu hình mô hình.")\n'
     'print(f"4. Mô hình được chọn qua 5-Fold CV: {winner_id} (Đa thức bậc 3).")\n'
     'print(f"   -> Điểm CV MSE trung bình: {selected_cv.loc[selected_cv.model_id.eq(winner_id), '
     '\'cv_mse_mean\'].iloc[0]:,.2f}")\n'
     '\n'
     'print("\\n5. Hiệu năng trên holdout tách theo dòng trên tập Holdout Test (10.342 mẫu):")\n'
     'print(f"   - MSE  : {selected.test_mse:,.2f} (Cải thiện {improvement:.2f}% so với Baseline M0)")\n'
     'print(f"   - RMSE : {selected.test_rmse:,.2f} EUR")\n'
     'print(f"   - MAE  : {selected.test_mae:,.2f} EUR")\n'
     'print(f"   - R²   : {selected.test_r2:.4f}")\n'
     '\n'
     'print(f"\\n6. Phân tích phần dư & giới hạn mô hình:")\n'
     'print(f"   - Số trường hợp dự đoán âm: {int(winner.predicted.lt(0).sum())} mẫu (chiếm '
     '{winner.predicted.lt(0).sum()/len(winner):.2%})")\n'
     'print(f"   - Nồng độ sai số: {top_n} mẫu sai số lớn nhất (1% mẫu) chiếm {top_share:.2%} tổng bình '
     'phương phần dư (SSE).")\n'
     'print("=" * 80)\n'
     'print("-> ĐÃ HOÀN TẤT THỰC THI TOÀN BỘ NOTEBOOK THÀNH CÔNG VÀ NHẤT QUÁN.")\n'}
