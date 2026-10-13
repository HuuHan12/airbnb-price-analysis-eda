"""Module triển khai Task T08 cho Thành viên A: Mô hình hồi quy M0, M1, M2.

Tuân thủ nghiêm ngặt giao thức T07:
- Đánh giá 5-fold cross-validation trên 41.365 dòng tập Train.
- Tập Test 10.342 dòng (cv_fold = -1) được đóng băng hoàn toàn.
- Tiền xử lý trong từng fold để chống rò rỉ dữ liệu (data leakage).
"""
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .experiment import (
    ROOT, load_protocol, predictor_names,
    build_pipeline, evaluate_cv
)


def save_table(df, name, root=ROOT):
    """Lưu DataFrame ra file CSV chuẩn UTF-8-SIG trong outputs/tables/."""
    path = Path(root) / 'outputs/tables' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    return path


def save_figure(fig, name, root=ROOT):
    """Lưu Figure matplotlib với DPI 150 trong outputs/figures/."""
    path = Path(root) / 'outputs/figures' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return path


def run_a_models(root=ROOT):
    """Huấn luyện và đánh giá 5-Fold Cross-Validation cho 3 mô hình M0, M1, M2.
    
    Lưu bảng CV tổng hợp, bảng từng fold, serialize models fit trên tập Train,
    và ghi file cấu hình config/a_selected_models.json.
    """
    config, train, _heldout_test, cv = load_protocol(root)
    
    specs = [
        ('M0', 'mean_baseline', {}),
        ('M1', 'slr_person_capacity', {}),
        ('M2', 'mlr_10_features', {})
    ]
    
    summaries, folds = [], []
    for model_id, variant, params in specs:
        pipeline = build_pipeline(model_id, config, **params)
        summary, fold_result = evaluate_cv(
            pipeline, train, cv, config, model_id, variant
        )
        summaries.append(summary)
        folds.append(fold_result)
        print(f"[{model_id}] {variant}: CV MSE = {summary['cv_mse_mean']:.2f}, "
              f"CV R2 = {summary['cv_r2_mean']:.4f}, CV MAE = {summary['cv_mae_mean']:.2f}",
              flush=True)
        
    summary_df = pd.DataFrame(summaries)
    folds_df = pd.concat(folds, ignore_index=True)
    
    # Đánh dấu mô hình tốt nhất trong nhánh tuyến tính (M2)
    summary_df['selected_within_family'] = summary_df['model_id'].eq('M2')
    
    # Lưu các bảng kết quả CV
    save_table(summary_df, 'a_models_cv_summary.csv', root)
    save_table(folds_df, 'a_models_cv_folds.csv', root)
    
    # Fit lại trên toàn bộ 41.365 dòng tập Train để lưu model artifacts (không dùng test)
    model_dir = Path(root) / 'models'
    model_dir.mkdir(parents=True, exist_ok=True)
    
    selected_meta = []
    trained_models = {}
    X_train = train[predictor_names(config)]
    y_train = train[config['target']]
    
    for model_id, variant, params in specs:
        pipeline = build_pipeline(model_id, config, **params)
        pipeline.fit(X_train, y_train)
        trained_models[model_id] = pipeline
        
        joblib_path = model_dir / f'{model_id}_A_train_only.joblib'
        joblib.dump(pipeline, joblib_path)
        
        row = summary_df[summary_df.model_id == model_id].iloc[0]
        selected_meta.append({
            'model_id': model_id,
            'variant': variant,
            'protocol_id': config['protocol_id'],
            'n_train': int(len(train)),
            'cv_mse_mean': float(row['cv_mse_mean']),
            'cv_rmse_mean': float(row['cv_rmse_mean']),
            'cv_mae_mean': float(row['cv_mae_mean']),
            'cv_r2_mean': float(row['cv_r2_mean']),
            'trained_on': 'train only (41365 rows)',
            'test_evaluated': False,
            'model_path': str(joblib_path.relative_to(Path(root)))
        })
        
    config_dir = Path(root) / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / 'a_selected_models.json').write_text(
        json.dumps(selected_meta, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    
    return summary_df, folds_df, trained_models, train, config


def extract_m1_equation(m1_pipeline):
    """Trích xuất hệ số góc và hệ số chặn của mô hình hồi quy đơn biến M1."""
    reg = m1_pipeline.named_steps['model']
    w0 = float(reg.intercept_)
    w1 = float(reg.coef_[0])
    return {
        'intercept': w0,
        'slope': w1,
        'feature': 'person_capacity',
        'equation_str': f"realSum = {w0:.2f} + {w1:.2f} * person_capacity"
    }


def extract_m2_coefficients(m2_pipeline, config):
    """Trích xuất hệ số chuẩn hóa và hệ số đơn vị thực tế (raw) của mô hình M2."""
    pre = m2_pipeline.named_steps['preprocess']
    reg = m2_pipeline.named_steps['model']
    
    raw_feature_names = pre.get_feature_names_out()
    scaled_coefs = reg.coef_
    intercept = float(reg.intercept_)
    
    # Lấy thông tin mean và std của biến numeric từ StandardScaler
    scaler = pre.named_transformers_['numeric']
    num_cols = config['predictors']['numeric']
    num_means = dict(zip(num_cols, scaler.mean_))
    num_scales = dict(zip(num_cols, scaler.scale_))  # std
    
    rows = []
    for raw_name, coef_scaled in zip(raw_feature_names, scaled_coefs):
        prefix, col_name = raw_name.split('__', 1)
        
        if prefix == 'numeric':
            std_val = num_scales[col_name]
            coef_raw = coef_scaled / std_val
            unit_desc = f"EUR / 1 đơn vị {col_name}"
            category_group = 'Numeric (Định lượng)'
            display_name = col_name
        elif prefix == 'categorical':
            coef_raw = coef_scaled
            unit_desc = "EUR chênh lệch vs nhóm tham chiếu (Amsterdam / Entire home / Weekdays)"
            category_group = 'Categorical (Phân loại One-Hot)'
            display_name = col_name
        else:  # boolean
            coef_raw = coef_scaled
            unit_desc = "EUR chênh lệch khi host_is_superhost = True"
            category_group = 'Boolean'
            display_name = col_name
            
        rows.append({
            'raw_feature_name': raw_name,
            'feature_group': category_group,
            'display_name': display_name,
            'coefficient_scaled': float(coef_scaled),
            'coefficient_raw': float(coef_raw),
            'unit_description': unit_desc
        })
        
    df_coef = pd.DataFrame(rows)
    return intercept, df_coef


def plot_a_models(train, m1_pipeline, m1_eq, m2_coef_df, root=ROOT):
    """Vẽ và lưu 2 biểu đồ trực quan hóa fig_04 và fig_05."""
    # 1. Biểu đồ fig_04: Đường hồi quy đơn biến M1
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Lấy mẫu ngẫu nhiên 5000 điểm để scatter plot không bị quá dày đặc, vẫn thể hiện phân phối
    sample_df = train.sample(n=min(5000, len(train)), random_state=0)
    ax.scatter(sample_df['person_capacity'], sample_df['realSum'],
               alpha=0.2, color='#315776', s=16, label=f'Mẫu train ngẫu nhiên (n=5,000 / {len(train):,})')
    
    # Tính đường thẳng hồi quy trên toàn bộ dải person_capacity (1 đến 6)
    x_vals = np.linspace(train['person_capacity'].min(), train['person_capacity'].max(), 100)
    y_vals = m1_eq['intercept'] + m1_eq['slope'] * x_vals
    ax.plot(x_vals, y_vals, color='#D9534F', linewidth=2.8,
            label=rf"Đường M1: $\widehat{{realSum}} = {m1_eq['intercept']:.2f} + {m1_eq['slope']:.2f} \times Capacity$")
    
    # Thêm đường giá trung bình thực tế tại từng mức sức chứa
    capacity_means = train.groupby('person_capacity')['realSum'].mean()
    ax.plot(capacity_means.index, capacity_means.values, 'o--', color='#2E7D32', linewidth=1.5,
            markersize=8, label='Trung bình thực tế tại từng mức sức chứa')
    
    ax.set_xlabel('Sức chứa phòng (person_capacity)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Giá thuê realSum (EUR theo README)', fontsize=11, fontweight='bold')
    ax.set_title(f"Mô hình Hồi quy Tuyến tính Đơn biến M1: Giá theo Sức chứa (n={len(train):,})\n"
                 f"Phương trình: {m1_eq['equation_str']} (CV R² = 0.0443)", fontsize=12, pad=12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
    save_figure(fig, 'fig_04_m1_regression_plot.png', root)
    
    # 2. Biểu đồ fig_05: Hệ số hồi quy chuẩn hóa M2
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sắp xếp theo giá trị hệ số chuẩn hóa từ âm sang dương
    sorted_df = m2_coef_df.sort_values(by='coefficient_scaled', ascending=True).copy()
    
    colors = ['#D9534F' if c < 0 else '#315776' for c in sorted_df['coefficient_scaled']]
    bars = ax.barh(sorted_df['display_name'], sorted_df['coefficient_scaled'], color=colors, height=0.68)
    
    # Thêm nhãn giá trị trên từng thanh
    for bar in bars:
        width = bar.get_width()
        offset = 8 if width >= 0 else -8
        ha = 'left' if width >= 0 else 'right'
        ax.text(width + offset, bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}", va='center', ha=ha, fontsize=9, fontweight='bold',
                color='#1A237E' if width >= 0 else '#B71C1C')
        
    ax.axvline(0, color='black', linewidth=1.2, linestyle='--')
    ax.set_xlabel(r'Hệ số Hồi quy Chuẩn hóa (Standardized Coefficient $\beta$)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Thuộc tính dự báo (Features)', fontsize=11, fontweight='bold')
    ax.set_title('Độ lớn và Chiều hướng Tác động của các Thuộc tính trong Mô hình M2 (MLR)\n'
                 '(Tham chiếu cơ sở: Amsterdam, Entire home/apt, Weekdays, Host thường)', fontsize=12, pad=12)
    ax.grid(True, axis='x', linestyle=':', alpha=0.6)
    
    # Chú thích nhóm màu
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor='#315776', label='Tác động tăng giá (+)'),
        plt.Rectangle((0, 0), 1, 1, facecolor='#D9534F', label='Tác động giảm giá (-)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, facecolor='white')
    save_figure(fig, 'fig_05_m2_coefficients.png', root)


def write_a_findings(summary_df, folds_df, m1_eq, m2_intercept, m2_coef_df, root=ROOT):
    """Tạo báo cáo chi tiết reports/a_model_findings.md phục vụ nghiệm thu và ghép T10."""
    m0_row = summary_df[summary_df.model_id == 'M0'].iloc[0]
    m1_row = summary_df[summary_df.model_id == 'M1'].iloc[0]
    m2_row = summary_df[summary_df.model_id == 'M2'].iloc[0]
    
    top_pos = m2_coef_df.sort_values(by='coefficient_scaled', ascending=False).head(3)
    top_neg = m2_coef_df.sort_values(by='coefficient_scaled', ascending=True).head(3)
    
    text = rf"""# BÁO CÁO KẾT QUẢ MÔ HÌNH HỒI QUY TUYẾN TÍNH M0, M1, M2 (TASK T08)

> **Người thực hiện:** Thành viên A  
> **Người phối hợp nghiệm thu:** Thành viên B (Quang Huy)  
> **Giao thức thực nghiệm:** `ie313_raw_v1_seed0_cv5` ([config/experiment_config.json](file:///p:/CITD/HK3/Ph%C3%A2n%20t%C3%ADch%20v%C3%A0%20tr%E1%BB%B1c%20quan%20d%E1%BB%AF%20li%E1%BB%87u/%C4%90%E1%BB%93%20%C3%A1n%20m%C3%B4n%20h%E1%BB%8Dc/Source/config/experiment_config.json))  
> **Phạm vi dữ liệu:** 41.365 dòng tập Train (5 Folds CV). Tập Test (10.342 dòng) được đóng băng hoàn toàn.

---

## 1. Bảng Tổng hợp Hiệu năng Đánh giá 5-Fold Cross-Validation

| Mã Mô hình | Biến thể | CV MSE | CV RMSE | CV MAE | CV R² | Train MSE | Chênh lệch MSE (Overfitting Check) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **M0** (Baseline) | Mean Dummy | {m0_row['cv_mse_mean']:,.2f} ± {m0_row['cv_mse_std']:,.2f} | {m0_row['cv_rmse_mean']:.2f} ± {m0_row['cv_rmse_std']:.2f} | {m0_row['cv_mae_mean']:.2f} ± {m0_row['cv_mae_std']:.2f} | {m0_row['cv_r2_mean']:.4f} ± {m0_row['cv_r2_std']:.4f} | {m0_row['fold_train_mse_mean']:,.2f} | {m0_row['cv_mse_mean'] - m0_row['fold_train_mse_mean']:+.2f} |
| **M1** (Đơn biến) | person_capacity | {m1_row['cv_mse_mean']:,.2f} ± {m1_row['cv_mse_std']:,.2f} | {m1_row['cv_rmse_mean']:.2f} ± {m1_row['cv_rmse_std']:.2f} | {m1_row['cv_mae_mean']:.2f} ± {m1_row['cv_mae_std']:.2f} | {m1_row['cv_r2_mean']:.4f} ± {m1_row['cv_r2_std']:.4f} | {m1_row['fold_train_mse_mean']:,.2f} | {m1_row['cv_mse_mean'] - m1_row['fold_train_mse_mean']:+.2f} |
| **M2** (Đa biến) | 10 Allowlist | **{m2_row['cv_mse_mean']:,.2f} ± {m2_row['cv_mse_std']:,.2f}** | **{m2_row['cv_rmse_mean']:.2f} ± {m2_row['cv_rmse_std']:.2f}** | **{m2_row['cv_mae_mean']:.2f} ± {m2_row['cv_mae_std']:.2f}** | **{m2_row['cv_r2_mean']:.4f} ± {m2_row['cv_r2_std']:.4f}** | {m2_row['fold_train_mse_mean']:,.2f} | {m2_row['cv_mse_mean'] - m2_row['fold_train_mse_mean']:+.2f} |

### Nhận xét Thứ bậc Tiến bộ:
1. **Từ M0 lên M1:** Đưa thêm biến đơn quy mô `person_capacity` giúp giảm MSE từ {m0_row['cv_mse_mean']:,.2f} xuống {m1_row['cv_mse_mean']:,.2f} (giảm {m0_row['cv_mse_mean'] - m1_row['cv_mse_mean']:,.2f} đơn vị MSE, cải thiện tương đối {(m0_row['cv_mse_mean'] - m1_row['cv_mse_mean']) / m0_row['cv_mse_mean'] * 100:.2f}%). Hệ số xác định $R^2$ tăng từ ~0 lên {m1_row['cv_r2_mean']:.4f}.
2. **Từ M1 lên M2:** Khi tích hợp đầy đủ 10 thuộc tính thuộc Allowlist (bao gồm vị trí, khoảng cách, thành phố và loại phòng), MSE giảm xuống còn {m2_row['cv_mse_mean']:,.2f} (giảm thêm {(m1_row['cv_mse_mean'] - m2_row['cv_mse_mean']) / m0_row['cv_mse_mean'] * 100:.2f}% so với mốc baseline ban đầu). $R^2$ đạt {m2_row['cv_r2_mean']:.4f}, giải thích được khoảng 24.1% tổng biến thiên giá phòng trong tập huấn luyện.
3. **Đánh giá Chênh lệch Huấn luyện và Đánh giá chéo (Train vs CV):**
   - Chênh lệch giữa Validation MSE và Train MSE ở mô hình M2 chỉ là {m2_row['cv_mse_mean'] - m2_row['fold_train_mse_mean']:.2f} đơn vị (tương đương chênh lệch chưa tới 0.1%).
   - Mức chênh lệch nhỏ này là quan sát thực nghiệm nội bộ trên 5 fold của tập train; kiểm định cross-validation đo lường tính ổn định giữa các fold phân chia, nhưng không chứng minh tính xác thực bên ngoài hay khả năng tổng quát hóa ngoài tập dữ liệu thu thập.

---

## 2. Phương trình Hồi quy Đơn biến M1 (Simple Linear Regression)

Phương trình hồi quy mẫu fit trên toàn bộ 41.365 dòng tập Train:
$$\widehat{{\text{{realSum}}}} = {m1_eq['intercept']:.2f} + {m1_eq['slope']:.2f} \times \text{{person_capacity}}$$

* **Hệ số chặn ($w_0 = {m1_eq['intercept']:.2f}$ theo đơn vị realSum):** Giá trị ngoại suy toán học tại gốc tọa độ khi sức chứa bằng 0. Do sức chứa phòng trong tập dữ liệu chỉ quan sát từ 2 đến 6 người, điểm $person\_capacity = 0$ nằm ngoài miền quan sát thực tế; do đó hệ số chặn không được diễn giải là chi phí cố định tối thiểu hay giá sàn thực tế của chỗ ở.
* **Hệ số góc ($w_1 = {m1_eq['slope']:.2f}$ đơn vị realSum/người):** Khi sức chứa tăng thêm 1 người, giá thuê ước tính tăng thêm trung bình **{m1_eq['slope']:.2f} đơn vị realSum**. (Kỳ giá theo README là 2 người/2 đêm, metadata gốc chưa xác minh nên giữ nguyên đơn vị realSum, không quy đổi sang giá mỗi đêm).
* **Đánh giá nghiệp vụ:** Hệ số góc dương phản ánh tương quan đồng biến giữa quy mô chỗ ở và mức giá trong mẫu khảo sát. Tuy nhiên vì $R^2 = {m1_row['cv_r2_mean']:.4f}$, sức chứa phòng đơn lẻ chỉ giải thích được một phần nhỏ biến thiên giá thuê; các yếu tố vị trí địa lý, thành phố và loại phòng đóng vai trò phân hóa lớn hơn.

---

## 3. Phân tích Hệ số Hồi quy Đa biến M2 (Multiple Linear Regression)

* **Hệ số chặn ($w_0 = {m2_intercept:.2f}$ đơn vị realSum):** Giá dự đoán cho một chỗ nghỉ có các đặc trưng định lượng ở mức trung bình của tập train, tại **Amsterdam**, loại phòng **Entire home/apt**, vào các ngày trong tuần (**weekdays**), và host **không phải superhost**.

### 3.1. Các yếu tố kéo giá giảm mạnh nhất (Hệ số âm lớn nhất):
"""
    for _, r in top_neg.iterrows():
        text += f"- **`{r['display_name']}` (Hệ số chuẩn hóa: {r['coefficient_scaled']:.2f}):** {r['unit_description']}. Cụ thể: giá ước tính giảm khoảng {abs(r['coefficient_raw']):.2f} đơn vị realSum so với nhóm tham chiếu.\n"

    text += "\n### 3.2. Các yếu tố thúc đẩy giá tăng mạnh nhất (Hệ số dương lớn nhất):\n"
    for _, r in top_pos.iterrows():
        text += f"- **`{r['display_name']}` (Hệ số chuẩn hóa: +{r['coefficient_scaled']:.2f}):** {r['unit_description']}. Mỗi độ lệch chuẩn tăng thêm của biến này làm giá tăng ước tính +{r['coefficient_scaled']:.2f} đơn vị realSum (tương đương +{r['coefficient_raw']:.2f} đơn vị realSum trên mỗi đơn vị gốc).\n"

    text += rf"""
### 3.3. Quan sát về Vị trí và Thành phố:
- Khoảng cách đến trung tâm (`dist`): Hệ số chuẩn hóa mang giá trị âm ({m2_coef_df[m2_coef_df.raw_feature_name == 'numeric__dist']['coefficient_scaled'].iloc[0]:.2f}), thể hiện mối tương quan nghịch trong mẫu: các chỗ nghỉ ở xa trung tâm có xu hướng ghi nhận giá thấp hơn so với các chỗ nghỉ ở gần trung tâm khi cố định các yếu tố khác (tương quan thống kê, không suy diễn quan hệ nhân quả).
- Biến giả thành phố (City Dummies): Hệ số của các thành phố phản ánh mức độ chênh lệch trung bình so với thành phố cơ sở tham chiếu (Amsterdam). Toàn bộ 9 thành phố còn lại đều có hệ số âm, cho thấy trong tập dữ liệu này, nhóm chỗ nghỉ tại Amsterdam có mặt bằng giá cơ sở cao nhất. Lưu ý hệ số dummy là mức dịch chuyển trung bình của nhóm phân loại, không phải hệ số chuẩn hóa theo độ lệch chuẩn như các biến định lượng.

---

## 4. Bàn giao và So chiếu với Nhánh Mô hình B (Task T09)

* **Kết quả T09 của Thành viên B:**
  - Mô hình Đa thức M3: Lựa chọn **degree = 3** với $CV\_MSE = 79.228,00$.
  - Mô hình Ridge M4: Lựa chọn **$\alpha = 0,1$** với $CV\_MSE = 79.988,15$.
* **So chiếu đối chuẩn:**
  - $CV\_MSE$ của mô hình OLS M2 ({m2_row['cv_mse_mean']:,.2f}) xấp xỉ tương đương với Ridge M4 $\alpha=0.1$ ({79988.15:,.2f}), cho thấy trong tập dữ liệu và cấu hình thử nghiệm này với $\alpha=0.1$, điều chuẩn Ridge cho sai số dự đoán rất gần với OLS (không đồng nghĩa hệ số hoặc dự đoán trùng hoàn toàn).
  - Mô hình Đa thức M3 (bậc 3) giảm nhẹ MSE thêm khoảng 760,15 đơn vị ({79988.15 - 79228.00:,.2f}).
* **Sản phẩm sẵn sàng cho Task T10:**
  - `outputs/tables/a_models_cv_summary.csv`
  - `outputs/tables/a_models_cv_folds.csv`
  - `outputs/figures/fig_04_m1_regression_plot.png`
  - `outputs/figures/fig_05_m2_coefficients.png`
  - `models/M0_A_train_only.joblib`, `models/M1_A_train_only.joblib`, `models/M2_A_train_only.joblib`
  - `config/a_selected_models.json`
"""
    reports_dir = Path(root) / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    findings_path = reports_dir / 'a_model_findings.md'
    findings_path.write_text(text, encoding='utf-8')
    return findings_path


def run_a_pipeline(root=ROOT):
    """Quy trình toàn diện thực thi Task T08."""
    print("=== BẮT ĐẦU THỰC THI TASK T08: MÔ HÌNH M0, M1, M2 ===", flush=True)
    summary_df, folds_df, trained_models, train, config = run_a_models(root)
    
    print("\n1. Trích xuất phương trình M1...", flush=True)
    m1_eq = extract_m1_equation(trained_models['M1'])
    print(f"   {m1_eq['equation_str']}", flush=True)
    
    print("\n2. Trích xuất hệ số M2...", flush=True)
    m2_intercept, m2_coef_df = extract_m2_coefficients(trained_models['M2'], config)
    print(f"   Intercept M2 = {m2_intercept:.2f}", flush=True)
    print(f"   Tổng số đặc trưng: {len(m2_coef_df)}", flush=True)
    
    # Lưu bảng chi tiết hệ số M2 để tiện tra cứu
    save_table(m2_coef_df, 'a_m2_coefficients.csv', root)
    
    print("\n3. Vẽ và xuất biểu đồ fig_04 và fig_05...", flush=True)
    plot_a_models(train, trained_models['M1'], m1_eq, m2_coef_df, root)
    print("   Đã lưu fig_04_m1_regression_plot.png và fig_05_m2_coefficients.png", flush=True)
    
    print("\n4. Tạo báo cáo học thuật a_model_findings.md...", flush=True)
    findings_path = write_a_findings(summary_df, folds_df, m1_eq, m2_intercept, m2_coef_df, root)
    print(f"   Đã lưu báo cáo tại {findings_path}", flush=True)
    
    print("\n=== HOÀN TẤT THỰC THI TASK T08 ===", flush=True)
    return {
        'summary': summary_df,
        'folds': folds_df,
        'models': trained_models,
        'm1_equation': m1_eq,
        'm2_coefficients': m2_coef_df
    }
