"""T05/T06 và T09 của B. Các output có số liệu thật, không sửa sản phẩm A."""
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr, f_oneway

from .experiment import (ROOT, load_data, prepare_protocol, load_protocol,
                         predictor_names, build_pipeline, evaluate_cv)

LIMIT = ('Mô tả liên hệ, không nhân quả; giá lệch phải/nhóm mất cân đối, '
         'độc lập mẫu chưa xác minh do tọa độ lặp; p nhỏ không đo độ lớn tác động.')


def save_table(df, name, root=ROOT):
    path = Path(root) / 'outputs/tables' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    return path


def save_figure(fig, name, root=ROOT):
    path = Path(root) / 'outputs/figures' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def price_summary(df, columns):
    table = df.groupby(columns, observed=True)['realSum'].agg(
        n='size', mean='mean', median='median', std='std',
        q1=lambda s: s.quantile(.25), q3=lambda s: s.quantile(.75)).reset_index()
    if len(columns) > 1:
        grid = pd.MultiIndex.from_product([sorted(df[c].unique()) for c in columns], names=columns)
        table = table.set_index(columns).reindex(grid).reset_index()
        table['n'] = table.n.fillna(0).astype(int)
    table['iqr'] = table.q3 - table.q1
    table['grouping'] = '+'.join(columns)
    table['availability'] = np.where(table.n.eq(0), 'no_observations', 'observed')
    return table


def build_eda_tables(df, root=ROOT):
    """Q1/Q2: bao gồm nhóm trống nhưng không gán giá 0 cho nhóm không có mẫu."""
    sets = [['city'], ['room_type'], ['city', 'day_type'], ['city', 'room_type'],
            ['city', 'room_type', 'day_type']]
    tables = [price_summary(df, cols) for cols in sets]
    summaries = pd.concat(tables, ignore_index=True)
    for _, g in summaries.groupby('grouping'):
        assert g.n.sum() == len(df)
        assert g.loc[g.n.eq(0), 'median'].isna().all()
    sampling = tables[-1].copy()
    sampling['share_of_city_day'] = sampling.n / sampling.groupby(['city', 'day_type']).n.transform('sum')
    pairs = sampling.pivot(index=['city', 'room_type'], columns='day_type', values=['n', 'mean', 'median'])
    pairs.columns = [metric + '_' + day for metric, day in pairs.columns]
    pairs = pairs.reset_index()
    pairs['median_difference_weekends_minus_weekdays'] = pairs.median_weekends - pairs.median_weekdays
    pairs['interpretation'] = 'Chênh hai nhóm quan sát; không ghép cặp cùng listing'
    # So sánh gộp city/day riêng, để thấy khác cơ cấu loại phòng.
    city_day = tables[2]
    city_pairs = city_day.pivot(index='city', columns='day_type', values=['n', 'mean', 'median'])
    city_pairs.columns = [metric + '_' + day for metric, day in city_pairs.columns]
    city_pairs = city_pairs.reset_index()
    city_pairs['median_difference_weekends_minus_weekdays'] = city_pairs.median_weekends - city_pairs.median_weekdays
    save_table(summaries, 'eda_group_summary.csv', root)
    save_table(sampling, 'eda_sampling_counts.csv', root)
    save_table(pairs, 'eda_day_comparison_by_room.csv', root)
    save_table(city_pairs, 'eda_day_comparison_by_city.csv', root)
    return summaries, sampling, city_pairs


def p_fields(p):
    """SciPy có thể underflow p thành 0; không diễn giải là xác suất bằng 0."""
    underflow = p == 0.0
    return {'p_value': np.nan if underflow else p,
            'p_display': 'underflow_float64; not exact zero' if underflow else f'{p:.4e}',
            'p_underflow': underflow, 'p_lt_0_05': bool(p < .05)}


def build_evidence(df, train, config, root=ROOT):
    numeric = ['person_capacity', 'bedrooms', 'dist', 'metro_dist', 'cleanliness_rating',
               'guest_satisfaction_overall', 'attr_index', 'attr_index_norm',
               'rest_index', 'rest_index_norm', 'lng', 'lat']
    allowed = set(predictor_names(config))
    pearson_rows, anova_rows, group_rows = [], [], []
    for scope, data in [('full_descriptive', df), ('train_descriptive', train)]:
        # Bảng train chỉ là diễn giải kiểm tra; allowlist không được lọc bằng r/p này.
        contexts = [('all_cities', data)] + list(data.groupby('city', sort=True))
        for context, group in contexts:
            for feature in numeric:
                x, y = group[feature], group.realSum
                valid = x.notna() & y.notna()
                if valid.sum() < 3 or x[valid].nunique() < 2:
                    r, p = np.nan, np.nan
                else:
                    r, p = pearsonr(x[valid].to_numpy(), y[valid].to_numpy())
                row = {'scope': scope, 'context': context, 'feature': feature, 'n': int(valid.sum()),
                       'method': 'Pearson', 'r': r, 'abs_r_ge_0_3': bool(abs(r) >= .3),
                       'used_in_core_model': feature in allowed, 'limitations': LIMIT}
                row.update(p_fields(p)); pearson_rows.append(row)
        for feature, context, group in [('city', 'all_cities', data),
                                         ('room_type', 'all_cities', data)] + [
                                         ('room_type', city, g) for city, g in data.groupby('city')]:
            groups = [(label, g.realSum.to_numpy()) for label, g in group.groupby(feature, observed=True)]
            arrays = [a for _, a in groups]
            variances = [np.var(a, ddof=1) for a in arrays if len(a) > 1]
            if len(arrays) >= 2 and all(len(a) >= 2 for a in arrays):
                f, p = f_oneway(*arrays)
            else:
                f, p = np.nan, np.nan
            row = {'scope': scope, 'context': context, 'feature': feature, 'method': 'One-way ANOVA',
                   'n': len(group), 'n_groups': len(groups), 'min_group_n': min(map(len, arrays)),
                   'f': f, 'variance_ratio_max_min': max(variances)/min(variances) if variances and min(variances)>0 else np.nan,
                   'used_in_core_model': feature in allowed, 'limitations': LIMIT}
            row.update(p_fields(p)); anova_rows.append(row)
            for label, a in groups:
                group_rows.append({'scope': scope, 'context': context, 'feature': feature,
                                   'group': label, 'n': len(a), 'mean': np.mean(a), 'median': np.median(a),
                                   'std': np.std(a, ddof=1) if len(a)>1 else np.nan})
    pearson = pd.DataFrame(pearson_rows)
    anova = pd.DataFrame(anova_rows)
    evidence = pd.concat([pearson, anova], ignore_index=True)
    evidence['decision'] = np.where(evidence.used_in_core_model, 'semantic_core_candidate', 'descriptive_only_excluded_core')
    evidence['decision_basis'] = 'Allowlist định trước theo ý nghĩa/metadata; r/p/F là mô tả, không tự động chọn theo y'
    save_table(pearson, 'pearson_price_evidence.csv', root)
    save_table(anova, 'anova_price_evidence.csv', root)
    save_table(pd.DataFrame(group_rows), 'anova_group_details.csv', root)
    save_table(evidence, 'feature_evidence.csv', root)
    corr = df[numeric + ['realSum']].corr()
    save_table(corr.reset_index(names='feature'), 'eda_correlation_matrix.csv', root)
    return pearson, anova, corr


def plot_eda(df, summaries, sampling, pearson, corr, root=ROOT):
    """Chỉ các hình trả lời Q1–Q4; không tạo dashboard ngoài phạm vi."""
    sns.set_theme(style='whitegrid', font='DejaVu Sans')
    city = summaries[summaries.grouping.eq('city')].sort_values('n')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(city.city, city.n, color='#315776')
    for i, n in enumerate(city.n): ax.text(n+60, i, f'{n:,}', va='center', fontsize=9)
    ax.set(xlim=(0, city.n.max()*1.15), xlabel='Số quan sát', title=f'Cơ cấu mẫu theo thành phố (n={len(df):,})')
    save_figure(fig, 'b_01_counts_by_city.png', root)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x='room_type', y='realSum', hue='room_type', legend=False,
                palette='Blues', ax=ax, showfliers=True)
    ax.set_yscale('log')
    ax.set(xlabel='Loại phòng', ylabel='realSum (EUR theo README), trục log',
           title='Giá theo loại phòng; giữ đầy đủ giá và điểm ngoại lệ')
    room_counts = df.room_type.value_counts()
    fig.text(.02,.01, 'n: '+', '.join(f'{c}={n:,}' for c,n in room_counts.items()), fontsize=9)
    save_figure(fig, 'b_02_price_by_room_type.png', root)
    city_day = summaries[summaries.grouping.eq('city+day_type')]
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(data=city_day, x='city', y='median', hue='day_type', errorbar=None,
                palette=['#315776','#C98535'], ax=ax)
    ax.tick_params(axis='x', rotation=35)
    ax.set(xlabel='Thành phố', ylabel='Trung vị realSum (EUR theo README)',
           title=f'Trung vị hai nhóm ngày theo city (n={len(df):,}); không phải cùng listing')
    save_figure(fig, 'b_03_city_day_median.png', root)
    city_room = summaries[summaries.grouping.eq('city+room_type')]
    med = city_room.pivot(index='city', columns='room_type', values='median')
    counts = city_room.pivot(index='city', columns='room_type', values='n')
    labels = med.map(lambda x: '' if pd.isna(x) else f'{x:.1f}')
    for c in labels:
        labels[c] = [f'{price}\nn={int(n):,}' if price else 'không có mẫu'
                     for price,n in zip(labels[c], counts[c])]
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.heatmap(med, mask=med.isna(), annot=labels, fmt='', cmap='YlGnBu', linewidths=.5, ax=ax,
                cbar_kws={'label':'Trung vị giá (EUR theo README)'})
    ax.set(xlabel='Loại phòng', ylabel='Thành phố', title='City × loại phòng: trung vị và số mẫu trong cùng ô')
    save_figure(fig, 'b_04_city_room_median_count.png', root)
    matrix = corr.loc[['person_capacity','bedrooms','dist','metro_dist','cleanliness_rating',
                       'guest_satisfaction_overall','realSum'],
                      ['person_capacity','bedrooms','dist','metro_dist','cleanliness_rating',
                       'guest_satisfaction_overall','realSum']]
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(matrix, vmin=-1,vmax=1,center=0,annot=True,fmt='.2f',cmap='RdBu_r',ax=ax)
    ax.set_title(f'Pearson biến số lõi và giá (n={len(df):,}); chỉ mô tả toàn bộ')
    save_figure(fig, 'b_05_core_correlation.png', root)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax, city_name in zip(axes, ['amsterdam','lisbon','london']):
        g=df[df.city.eq(city_name)]
        # Dùng đủ mẫu; alpha nhỏ để thấy vùng tập trung, không cap target.
        ax.scatter(g.person_capacity,g.realSum,s=8,alpha=.15,color='#315776')
        ax.set_yscale('log')
        r=pearson.loc[pearson.scope.eq('full_descriptive') & pearson.context.eq(city_name)
                      & pearson.feature.eq('person_capacity'),'r'].iloc[0]
        ax.set(title=f'{city_name}: n={len(g):,}, r={r:.3f}',xlabel='person_capacity')
    axes[0].set_ylabel('Giá realSum (EUR theo README), trục log')
    fig.suptitle('Liên hệ sức chứa–giá trong city; r tính trên giá gốc, không phải log',y=1.02)
    save_figure(fig, 'b_06_capacity_price_within_city.png', root)
    fig, ax = plt.subplots(figsize=(12,5))
    share=sampling.pivot(index=['city','day_type'],columns='room_type',values='share_of_city_day')
    share.plot.bar(stacked=True,ax=ax,color=['#315776','#C98535','#6F927D'],width=.8)
    ax.set(xlabel='City, nhóm ngày',ylabel='Tỷ lệ mẫu',title=f'Cơ cấu loại phòng của hai nhóm ngày trong mỗi city (n={len(df):,})')
    ax.legend(title='room_type',loc='upper left',bbox_to_anchor=(1,1))
    save_figure(fig, 'b_07_room_composition_by_day.png', root)


def write_eda_findings(df, summaries, city_pairs, pearson, anova, root=ROOT):
    city=summaries[summaries.grouping.eq('city')].set_index('city')
    room=summaries[summaries.grouping.eq('room_type')].set_index('room_type')
    global_capacity=pearson[(pearson.scope=='full_descriptive') & (pearson.context=='all_cities') & (pearson.feature=='person_capacity')].iloc[0]
    room_test=anova[(anova.scope=='full_descriptive') & (anova.context=='all_cities') & (anova.feature=='room_type')].iloc[0]
    maxdiff=city_pairs.loc[city_pairs.median_difference_weekends_minus_weekdays.abs().idxmax()]
    counts=df.room_type.value_counts()
    text=f'''# Phát hiện T05–T06 của B

Ngày chạy: 12/10/2026. Các bảng `full_descriptive` mô tả toàn bộ 51.707 quan sát; bảng `train_descriptive` chỉ train. Đây không phải kết quả test mô hình, không dùng bảng mô tả để tự động lọc predictor.

## Q1: giá và cơ cấu mẫu

- Mean giá {df.realSum.mean():.2f}, median {df.realSum.median():.2f}, std {df.realSum.std():.2f}, skew {df.realSum.skew():.2f}; đơn vị EUR/kỳ giá theo README, chưa xác minh metadata gốc. Mean cao hơn median; không dùng mean một mình để nói giá điển hình.
- Median Amsterdam {city.loc['amsterdam','median']:.2f}, Athens {city.loc['athens','median']:.2f}. Khác mặt bằng giá theo nhóm quan sát; không kết luận city gây chênh giá hoặc dữ liệu đại diện toàn thị trường.
- Entire home/apt: n={counts['Entire home/apt']:,}, median {room.loc['Entire home/apt','median']:.2f}; Private room: n={counts['Private room']:,}, median {room.loc['Private room','median']:.2f}; Shared room: n={counts['Shared room']:,}, median {room.loc['Shared room','median']:.2f}. Shared chỉ {counts['Shared room']/len(df)*100:.3f}%: đọc n từng ô trước so sánh.
- Cờ IQR và lý do giữ giá gốc dùng phần A đã review; chưa chứng minh giá cao là luxury/biệt thự. Hình B giữ đủ giá, dùng trục log có chú thích.

## Q2: hai nhóm ngày

- Chênh median gộp theo city lớn nhất về trị tuyệt đối tại {maxdiff['city']}: weekdays {maxdiff['median_weekdays']:.2f} (n={int(maxdiff['n_weekdays']):,}), weekends {maxdiff['median_weekends']:.2f} (n={int(maxdiff['n_weekends']):,}), chênh {maxdiff['median_difference_weekends_minus_weekdays']:.2f}.
- Đây là so sánh hai tập quan sát, không ghép cặp cùng phòng. Đối chiếu `eda_day_comparison_by_room.csv` và biểu đồ cơ cấu loại phòng để tách sự khác cơ cấu; không nói “cùng phòng tăng giá cuối tuần”.
- Bảng nhóm tạo đủ tổ hợp: count=0 cho tổ hợp không có mẫu, giá giữ NaN; không điền giá 0. `eda_sampling_counts.csv` lưu tỷ lệ theo city/day và n.

## Q3: Pearson

- r sức chứa–giá toàn bộ {global_capacity['r']:.3f}, n={int(global_capacity['n']):,}; r tuyến tính gộp nhỏ không phủ nhận liên hệ trong city. Xem bảng r/p/n từng city và scatter; dữ liệu tọa độ lặp làm độc lập mẫu chưa xác minh.
- Kế hoạch môn dùng ngưỡng khoảng 0,3 để tham khảo bài giá xe; không dùng ngưỡng này loại toàn bộ yếu tố Airbnb. Allowlist mô hình cố định theo ý nghĩa; các biến index/tọa độ vẫn được mô tả nhưng chưa đưa vào core do metadata/diễn giải.

## Q4: ANOVA

- ANOVA giá theo room_type toàn bộ: F={room_test['f']:.3f}, p={room_test['p_display']}, min nhóm n={int(room_test['min_group_n'])}; tỷ số phương sai nhóm lớn nhất/nhỏ nhất {room_test['variance_ratio_max_min']:.2f}. Báo F/p đi cùng mean/median/n, không gọi p nhỏ là tác động lớn hay mọi cặp khác nhau.
- Giả định độc lập, phương sai và dạng phần dư không được đảm bảo: giá lệch phải, nhóm mất cân đối, tọa độ lặp. Đây là áp dụng kỹ thuật môn với giới hạn, không kết luận nhân quả/định giá đúng.
- p dưới độ biểu diễn float64: bảng để giá trị numeric trống với `p_underflow=True`, nhãn underflow; không khẳng định xác suất đúng bằng 0. Giữ thống kê F/r và n để đọc kết quả.

## Đầu ra và sử dụng

`eda_group_summary.csv`, `eda_sampling_counts.csv`, hai bảng chênh ngày, `pearson_price_evidence.csv`, `anova_price_evidence.csv`, `anova_group_details.csv`, `feature_evidence.csv`; 7 hình có tiền tố `b_`. Một dòng mỗi phép xét có scope/context để tránh nhầm EDA toàn bộ với kết quả trên train.

Các hình/bảng được tạo bằng Python. AI hỗ trợ code và bản thảo trong lượt này; nhóm cần kiểm tra, hiểu và khai báo công cụ thực tế khi viết đoạn minh bạch. Phần nhận xét này chỉ dùng số tính từ data, không sao chép kết quả mô hình ngoài.
'''
    reports=Path(root)/'reports';reports.mkdir(exist_ok=True)
    (reports/'eda_findings.md').write_text(text,encoding='utf-8')


def run_eda(root=ROOT):
    df=load_data(root)
    config,manifest=prepare_protocol(df,root)
    _,train,_,_=load_protocol(root)
    summaries,sampling,city_pairs=build_eda_tables(df,root)
    pearson,anova,corr=build_evidence(df,train,config,root)
    plot_eda(df,summaries,sampling,pearson,corr,root)
    write_eda_findings(df,summaries,city_pairs,pearson,anova,root)
    return {'data':df,'config':config,'manifest':manifest,'summary':summaries,
            'sampling':sampling,'pearson':pearson,'anova':anova}


def run_b_models(root=ROOT):
    """T09 chỉ train/CV; chưa chọn thắng chung hoặc dự đoán holdout."""
    config,train,_test,cv=load_protocol(root)
    specs=[('M3',f'degree_{degree}',{'degree':degree}) for degree in config['polynomial_degrees']]
    specs += [('M4',f'alpha_{alpha:g}',{'alpha':alpha}) for alpha in config['ridge_alphas']]
    summaries,folds=[],[]
    for model_id,variant,params in specs:
        model=build_pipeline(model_id,config,**params)
        summary,detail=evaluate_cv(model,train,cv,config,model_id,variant)
        summary.update(params);summaries.append(summary);folds.append(detail)
        print(model_id,variant,'CV MSE',round(summary['cv_mse_mean'],2),flush=True)
    summary=pd.DataFrame(summaries)
    summary['selected_within_family']=False
    selected=[]
    model_dir=Path(root)/'models';model_dir.mkdir(exist_ok=True)
    for model_id in ['M3','M4']:
        idx=summary.loc[summary.model_id.eq(model_id),'cv_mse_mean'].idxmin()
        summary.loc[idx,'selected_within_family']=True
        row=summary.loc[idx]
        params={'degree':int(row.degree)} if model_id=='M3' else {'alpha':float(row.alpha)}
        model=build_pipeline(model_id,config,**params)
        model.fit(train[predictor_names(config)],train[config['target']])
        joblib.dump(model,model_dir/f'{model_id}_B_train_only.joblib')
        selected.append({'model_id':model_id,'variant':row.variant,'params':params,
                         'cv_mse_mean':float(row.cv_mse_mean), 'trained_on':'train only',
                         'test_evaluated':False, 'protocol_id':config['protocol_id']})
    save_table(summary,'b_models_cv_summary.csv',root)
    save_table(pd.concat(folds,ignore_index=True),'b_models_cv_folds.csv',root)
    (Path(root)/'config/b_selected_models.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
    text='# T09: đa thức và Ridge của B\n\nĐã chạy train/CV, không đánh giá hoặc dự đoán test. So sánh cùng config, manifest và folds trong T07.\n\n'
    for row in selected:
        text+=f"- {row['model_id']}: chọn {row['variant']} theo CV MSE trung bình {row['cv_mse_mean']:.2f}, fit lại chỉ train để lưu model.\n"
    text+='\nChưa tuyên bố mô hình thắng chung: phải nhận M0/M1/M2 của A và chốt bằng CV trước T10. Mean RMSE của folds khác sqrt(mean MSE); CSV lưu rõ từng fold và mean/std.\n'
    text+='\nAllowlist cố định theo metadata trước CV; không lọc predictor theo target. Bậc 2/3 chỉ trên capacity, bedrooms, dist; các nhóm city/day/room và phần numeric còn lại dùng cùng biểu diễn nền. Ridge dùng dãy alpha đã có trong kế hoạch.\n'
    (Path(root)/'reports/b_model_findings.md').write_text(text,encoding='utf-8')
    return summary
