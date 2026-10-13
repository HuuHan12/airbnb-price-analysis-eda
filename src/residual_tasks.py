"""T11: mô tả sai số holdout đã mở ở T10; không fit/chọn lại mô hình."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .experiment import ROOT, load_protocol


def load_checked_predictions(root=ROOT):
    root = Path(root)
    config, _, test, _ = load_protocol(root)
    comparison = pd.read_csv(root / 'outputs/tables/model_comparison_cv_vs_test.csv')
    predictions = pd.read_csv(root / 'outputs/tables/test_predictions.csv')
    keys = config['trace_keys']
    if set(comparison.model_id) != {'M0', 'M1', 'M2', 'M3', 'M4'} or comparison.model_id.duplicated().any():
        raise ValueError('Bảng so sánh phải có đúng năm mô hình duy nhất')
    selected = comparison.loc[comparison.selected_winning_model.eq(True)]
    if len(selected) != 1 or selected.iloc[0].model_id != comparison.loc[comparison.cv_mse_mean.idxmin(), 'model_id']:
        raise ValueError('Mô hình chốt không khớp tiêu chí CV đã có')
    if set(predictions.model_id) != set(comparison.model_id):
        raise ValueError('Sai tập mô hình trong dự đoán')
    if not predictions.split.eq('test').all() or not predictions.protocol_id.eq(config['protocol_id']).all():
        raise ValueError('Sai split/protocol')
    checked = []
    for row in comparison.itertuples():
        part = predictions.loc[predictions.model_id.eq(row.model_id)].copy()
        if len(part) != len(test) or part.duplicated(keys).any():
            raise ValueError('Thiếu/trùng dự đoán: ' + row.model_id)
        joined = test.merge(part, on=keys, how='outer', validate='one_to_one', indicator=True)
        if not joined['_merge'].eq('both').all():
            raise ValueError('Khóa dự đoán không khớp holdout')
        if not np.isfinite(joined[['actual', 'predicted', 'residual']]).all().all():
            raise ValueError('Dự đoán không hữu hạn')
        if not np.allclose(joined.actual, joined.realSum, rtol=1e-12, atol=1e-10):
            raise ValueError('Giá thực tế không khớp CSV gốc')
        if not np.allclose(joined.residual, joined.actual - joined.predicted, rtol=1e-12, atol=1e-10):
            raise ValueError('Sai định nghĩa phần dư')
        stats = metrics(joined)
        for name in ['mse', 'rmse', 'mae', 'r2']:
            if not np.isclose(stats[name], getattr(row, 'test_' + name), rtol=1e-10, atol=1e-8):
                raise ValueError('Metric không khớp T10: ' + row.model_id + '/' + name)
        joined['abs_residual'] = joined.residual.abs()
        joined['squared_residual'] = joined.residual ** 2
        checked.append(joined.drop(columns='_merge'))
    return config, comparison, pd.concat(checked, ignore_index=True), selected.iloc[0].model_id


def metrics(frame):
    residual = frame.actual - frame.predicted
    mse = float(np.mean(residual ** 2))
    total = float(np.sum((frame.actual - frame.actual.mean()) ** 2))
    return {'n': len(frame), 'mse': mse, 'rmse': float(np.sqrt(mse)),
            'mae': float(np.mean(np.abs(residual))),
            'r2': float(1 - np.sum(residual ** 2) / total) if total > 0 else np.nan,
            'mean_residual_actual_minus_predicted': float(residual.mean()),
            'median_abs_residual': float(np.median(np.abs(residual))),
            'p90_abs_residual': float(np.quantile(np.abs(residual), .9)),
            'negative_predictions': int(frame.predicted.lt(0).sum())}


def run_residual_analysis(root=ROOT):
    root = Path(root)
    config, comparison, all_predictions, winner = load_checked_predictions(root)
    frame = all_predictions.loc[all_predictions.model_id.eq(winner)].copy()
    tables = root / 'outputs/tables'
    figures = root / 'outputs/figures'
    rows = []
    for columns in [['city'], ['room_type'], ['day_type'], ['city', 'room_type']]:
        for group, part in frame.groupby(columns, observed=True, sort=True):
            group = group if isinstance(group, tuple) else (group,)
            rows.append({'grouping': '+'.join(columns), **dict(zip(columns, group)), **metrics(part)})
    groups = pd.DataFrame(rows)
    groups.to_csv(tables / 'b_residual_group_metrics.csv', index=False, encoding='utf-8-sig')
    cases = frame.nlargest(10, 'abs_residual')[config['trace_keys'] +
        ['city', 'day_type', 'room_type', 'person_capacity', 'bedrooms', 'dist',
         'actual', 'predicted', 'residual', 'abs_residual', 'model_id', 'protocol_id']]
    cases.to_csv(tables / 'b_residual_cases.csv', index=False, encoding='utf-8-sig')
    order = frame.sort_values('squared_residual', ascending=False)
    total_sse = float(order.squared_residual.sum())
    tail = []
    for percent in [1, 5, 10, 100]:
        count = int(np.ceil(len(frame) * percent / 100))
        tail.append({'largest_error_percent': percent, 'n': count,
                     'share_total_sse': float(order.head(count).squared_residual.sum() / total_sse)})
    pd.DataFrame(tail).to_csv(tables / 'b_residual_error_concentration.csv', index=False, encoding='utf-8-sig')
    summary = {'protocol_id': config['protocol_id'], 'selected_model': winner,
               'selection_rule': 'Existing T10 selection by CV MSE; no refit or holdout tuning',
               **metrics(frame), 'top_1_percent_share_sse': tail[0]['share_total_sse']}
    (root / 'reports/b_residual_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(figures / name, dpi=150, bbox_inches='tight')
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].scatter(frame.predicted, frame.residual, s=8, alpha=.25, color='#147a93', rasterized=True)
    axes[0].axhline(0, color='#c44c39', lw=1)
    axes[0].set(xlabel='Fitted value (realSum)', ylabel='Residual = actual - predicted', title=f'{winner}: residuals, all {len(frame):,} holdout rows')
    axes[1].scatter(frame.actual, frame.predicted, s=8, alpha=.25, color='#147a93', rasterized=True)
    low = min(frame.actual.min(), frame.predicted.min())
    high = max(frame.actual.max(), frame.predicted.max())
    axes[1].plot([low, high], [low, high], color='#c44c39', lw=1)
    axes[1].set(xlabel='Actual (realSum)', ylabel='Predicted (realSum)', title='Actual versus predicted; no rows removed')
    save(fig, 'b_08_residual_and_actual_predicted.png')
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, grouping in zip(axes, ['city', 'room_type']):
        part = groups.loc[groups.grouping.eq(grouping)].sort_values('rmse')
        labels = [f'{r[grouping]} (n={int(r["n"])})' for _, r in part.iterrows()]
        ax.barh(labels, part.rmse, color='#147a93')
        ax.set(xlabel='RMSE (realSum)', title=f'{winner}: error by {grouping}, observed test groups')
    save(fig, 'b_09_residual_group_rmse.png')
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(np.arange(1, len(order) + 1) / len(order) * 100,
            order.squared_residual.cumsum() / total_sse * 100, color='#147a93')
    ax.set(xlabel='Rows ordered from largest squared error (%)', ylabel='Cumulative share of SSE (%)',
           title=f'{winner}: concentration of holdout squared error', xlim=(0, 100), ylim=(0, 100))
    ax.grid(alpha=.2)
    save(fig, 'b_10_residual_error_concentration.png')
    write_findings(root, summary, groups, cases, comparison)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary, groups, cases


def write_findings(root, summary, groups, cases, comparison):
    city = groups.loc[groups.grouping.eq('city')].sort_values('rmse', ascending=False).iloc[0]
    baseline = comparison.loc[comparison.model_id.eq('M0')].iloc[0]
    selected = comparison.loc[comparison.model_id.eq(summary['selected_model'])].iloc[0]
    improvement = (baseline.test_mse - selected.test_mse) / baseline.test_mse * 100
    text = f'''# T11 — phần dư, lỗi nhóm và trường hợp sai số lớn

Mô hình {summary['selected_model']} đã chốt ở T10 bằng CV; phân tích này chỉ mô tả holdout, không đổi biến, bậc, alpha, split hay xử lý giá dựa trên test. Đã đối chiếu toàn bộ dự đoán năm mô hình với CSV gốc qua source_file/source_row, giá thực tế, phần dư và bốn metric T10.

## Kết quả chính

Trên {summary['n']:,} dòng test, RMSE = {summary['rmse']:.2f}, MAE = {summary['mae']:.2f}, R² = {summary['r2']:.4f}. MSE giảm {improvement:.2f}% so với baseline M0 trên cùng test. Kết quả thể hiện cải thiện so với dự đoán trung bình nhưng mức giải thích biến thiên còn thấp; không bảo đảm chất lượng định giá ngoài bộ dữ liệu.

Median sai số tuyệt đối = {summary['median_abs_residual']:.2f}; phân vị 90% = {summary['p90_abs_residual']:.2f}. Trung bình actual−predicted = {summary['mean_residual_actual_minus_predicted']:.2f}: số dương là dự đoán thấp hơn giá quan sát trung bình, số âm là cao hơn. Giá ở đây dùng nguyên realSum; EUR theo README, kỳ giá chưa được xác minh, không đổi sang giá/đêm.

Nhóm 1% dòng có lỗi bình phương lớn nhất chiếm {summary['top_1_percent_share_sse']:.2%} tổng SSE. Điều này mô tả độ tập trung sai số; không được loại các dòng này để báo metric đẹp hơn. Có {summary['negative_predictions']} dự đoán âm; giữ nguyên để phản ánh hạn chế mô hình, không cắt về 0 sau khi nhìn test.

Trong các city quan sát ở test, {city['city']} có RMSE lớn nhất ({city['rmse']:.2f}, n={int(city['n'])}). So sánh này chịu ảnh hưởng thang giá, phân phối và cơ cấu mẫu; không chứng minh thành phố đó có chất lượng dữ liệu kém. Bảng lỗi room_type/day_type/city×room_type luôn kèm n; nhóm ít mẫu có thể biến động lớn.

## Hình và trường hợp truy vết

Hình b_08 thể hiện tất cả các điểm test, đường residual=0 và đường actual=predicted; không cắt đuôi. Hình b_09 so sánh RMSE theo nhóm kèm số mẫu. Hình b_10 thể hiện mức tập trung SSE. Các hình là mô tả; chưa có kiểm định chính thức để khẳng định phân phối chuẩn hoặc phương sai phần dư không đổi.

Bảng b_residual_cases.csv chứa 10 dòng có sai số tuyệt đối lớn nhất kèm file/dòng nguồn, city, room, sức chứa, bedrooms, dist, actual và predicted. source_row là khóa truy vết đã tạo khi nạp CSV, không phải listing ID hay mặc định số dòng Excel. Sai số lớn không chứng minh gian lận, giá sai, nhà sang trọng hoặc cùng listing.

## Đoạn kết luận dùng cho T13

Đồ án phân tích 51.707 quan sát Airbnb từ 20 tệp của 10 thành phố, mô tả phân phối giá và so sánh các nhóm bằng thống kê, Pearson và ANOVA với giới hạn giả định rõ ràng. Năm mô hình hồi quy được so sánh bằng cùng 5-fold CV trong 41.365 mẫu train; đa thức bậc 3 được chọn theo MSE CV thấp nhất. Trên holdout 10.342 mẫu, mô hình đạt RMSE {summary['rmse']:.2f}, MAE {summary['mae']:.2f}, R² {summary['r2']:.4f}, giảm MSE {improvement:.2f}% so với baseline. Phân tích phần dư cho thấy sai số tập trung ở một phần nhỏ quan sát và khác nhau theo nhóm. Kết quả còn hạn chế do giá lệch mạnh, thiếu metadata về kỳ giá và listing ID, cùng khả năng lặp tọa độ giữa train/test; đây là đánh giá trên bộ dữ liệu cung cấp, không phải bằng chứng nhân quả hay xác thực ngoài mẫu thu thập.
'''
    (Path(root) / 'reports/b_residual_findings.md').write_text(text, encoding='utf-8')


if __name__ == '__main__':
    run_residual_analysis()
