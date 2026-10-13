"""Giao thức T07: dữ liệu nguyên giá, cùng holdout/folds, preprocessing trong fold.

Tập biến được ấn định theo ý nghĩa trước CV. Bảng Pearson/ANOVA mô tả không
được dùng làm bộ lọc tự động. A dùng module này cho T08 để so sánh với T09.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import KFold, train_test_split, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / 'config/experiment_config.json'
DATA_PATH = ROOT / 'data/processed/airbnb_combined.csv'
MANIFEST_PATH = ROOT / 'data/processed/split_manifest.csv'
NUMERIC = ['person_capacity', 'bedrooms', 'dist', 'metro_dist',
           'cleanliness_rating', 'guest_satisfaction_overall']
CATEGORICAL = ['city', 'day_type', 'room_type']
BOOLEAN = ['host_is_superhost']
POLYNOMIAL = ['person_capacity', 'bedrooms', 'dist']
EXCLUDED = ['realSum', 'Unnamed: 0', 'source_file', 'source_row',
            'room_shared', 'room_private', 'multi', 'biz', 'attr_index',
            'attr_index_norm', 'rest_index', 'rest_index_norm', 'lng', 'lat',
            'log_price_temp', 'price_tier', 'dist_bin']


def sha256(path):
    # Git có thể đổi LF/CRLF giữa hai máy; giữ hash ổn định với cùng nội dung CSV.
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def load_data(root=ROOT):
    """Đọc CSV sạch; không dùng dataframe đã thêm target-derived trong notebook A."""
    df = pd.read_csv(Path(root) / 'data/processed/airbnb_combined.csv')
    if df.shape != (51707, 24):
        raise ValueError('Sai snapshot 51707 x 24; cần review lại trước đổi protocol')
    if df[['source_file', 'source_row']].duplicated().any():
        raise ValueError('Mã truy vết không duy nhất')
    if df.isna().any().any() or not np.isfinite(df.select_dtypes(include='number')).all().all():
        raise ValueError('Dữ liệu khuyết/không hữu hạn chưa được xử lý')
    if not df.realSum.gt(0).all():
        raise ValueError('Giá không dương')
    for col in BOOLEAN:
        if not df[col].isin([True, False]).all():
            raise ValueError('Cờ boolean không hợp lệ: ' + col)
    return df


def prepare_protocol(df, root=ROOT):
    """Tạo manifest/config xác định, không chọn split dựa giá hoặc kết quả mô hình."""
    root = Path(root)
    path = root / 'data/processed/airbnb_combined.csv'
    train_idx, test_idx = train_test_split(np.arange(len(df)), test_size=.2, random_state=0)
    # Đưa train về thứ tự CSV rồi gán fold; mọi notebook đọc cùng thứ tự này.
    train_idx = np.sort(train_idx)
    manifest = df[['source_file', 'source_row']].copy()
    manifest['split'] = 'test'
    manifest.loc[train_idx, 'split'] = 'train'
    manifest['cv_fold'] = -1  # test không tham gia CV
    for fold, (_, valid_pos) in enumerate(KFold(5, shuffle=True, random_state=0).split(train_idx)):
        manifest.loc[train_idx[valid_pos], 'cv_fold'] = fold
    config = {
        'protocol_id': 'ie313_raw_v1_seed0_cv5',
        'created_on': '2026-10-12',
        'data_file': 'data/processed/airbnb_combined.csv',
        'data_sha256': sha256(path),
        'data_hash_method': 'sha256 of CSV bytes after CRLF-to-LF normalization',
        'n_rows': len(df), 'n_columns': df.shape[1],
        'target': 'realSum', 'target_transform': 'none',
        'price_unit': 'EUR theo README; kỳ giá chưa xác minh metadata gốc',
        'trace_keys': ['source_file', 'source_row'],
        'predictors': {'numeric': NUMERIC, 'categorical': CATEGORICAL, 'boolean': BOOLEAN},
        'excluded_predictors': EXCLUDED,
        'predictor_policy': 'Fixed semantic allowlist; no target-based automatic feature selection',
        'slr_feature': 'person_capacity',
        'slr_reason': 'Giả thuyết quy mô sức chứa; ấn định trước so sánh CV, không lọc theo r/p toàn bộ',
        'polynomial_features': POLYNOMIAL,
        'polynomial_degrees': [2, 3],
        'ridge_alphas': [.001, .01, .1, 1., 10., 100., 1000.],
        'split': {'test_size': .2, 'seed': 0, 'n_train': len(train_idx), 'n_test': len(test_idx),
                  'manifest': 'data/processed/split_manifest.csv'},
        'cv': {'n_splits': 5, 'shuffle': True, 'seed': 0,
               'fold_column': 'cv_fold', 'test_fold_value': -1},
        'selection_metric': 'cv_mse_mean',
        'encoding': {'drop': 'first', 'handle_unknown': 'ignore', 'dense': True},
        'outliers': 'No clipping/removal; original realSum for all models and holdout',
        'test_policy': 'Do not tune/predict/evaluate test until A T08 and B T09 are compared and model locked',
        'limits': ['EDA describes the full supplied dataset; not confirmatory causal evidence',
                   'Repeated coordinates may occur on both sides; no verified listing ID',
                   'multi/biz/index definitions unverified; omitted from core models',
                   'Protocol implemented by B; A must review/use exact manifest before T08']}
    cp = root / 'config/experiment_config.json'
    mp = root / 'data/processed/split_manifest.csv'
    cp.parent.mkdir(parents=True, exist_ok=True)
    mp.parent.mkdir(parents=True, exist_ok=True)
    # Không tự thay protocol khi A đã có manifest khác.
    if cp.exists() and json.loads(cp.read_text(encoding='utf-8')) != config:
        raise ValueError('Config đã khác: cần đối chiếu với A, không ghi đè')
    if mp.exists():
        pd.testing.assert_frame_equal(pd.read_csv(mp), manifest, check_dtype=False)
    cp.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest.to_csv(mp, index=False, encoding='utf-8-sig')
    return config, manifest


def load_protocol(root=ROOT):
    root = Path(root)
    config = json.loads((root / 'config/experiment_config.json').read_text(encoding='utf-8'))
    df = load_data(root)
    if sha256(root / config['data_file']) != config['data_sha256']:
        raise ValueError('Data hash đã đổi; không dùng split/model cũ')
    manifest = pd.read_csv(root / config['split']['manifest'])
    pd.testing.assert_frame_equal(df[config['trace_keys']], manifest[config['trace_keys']], check_dtype=False)
    if set(manifest.split) != {'train', 'test'}:
        raise ValueError('Sai nhãn split')
    train = df.loc[manifest.split.eq('train')].reset_index(drop=True)
    test = df.loc[manifest.split.eq('test')].reset_index(drop=True)
    train_folds = manifest.loc[manifest.split.eq('train'), 'cv_fold'].to_numpy()
    cv = [(np.flatnonzero(train_folds != fold), np.flatnonzero(train_folds == fold)) for fold in range(5)]
    if len(train) != config['split']['n_train'] or len(test) != config['split']['n_test']:
        raise ValueError('Sai số mẫu split')
    if not manifest.loc[manifest.split.eq('test'), 'cv_fold'].eq(-1).all():
        raise ValueError('Test đã bị đưa vào CV')
    return config, train, test, cv


def predictor_names(config):
    p = config['predictors']
    return p['numeric'] + p['categorical'] + p['boolean']


def build_pipeline(model_id, config, degree=None, alpha=None):
    """A dùng M0/M1/M2, B dùng M3/M4; tất cả fit preprocessing trong CV."""
    numeric = config['predictors']['numeric']
    if model_id == 'M0':
        return Pipeline([('model', DummyRegressor(strategy='mean'))])
    if model_id == 'M1':
        pre = ColumnTransformer([('slr', 'passthrough', [config['slr_feature']])], remainder='drop')
        return Pipeline([('preprocess', pre), ('model', LinearRegression())])
    parts = []
    if model_id == 'M3':
        poly = config['polynomial_features']
        parts.append(('polynomial', Pipeline([
            ('expand', PolynomialFeatures(degree=degree, include_bias=False)),
            ('scale', StandardScaler())]), poly))
        numeric = [c for c in numeric if c not in poly]
    parts += [('numeric', StandardScaler(), numeric),
              ('categorical', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False),
               config['predictors']['categorical']),
              ('boolean', 'passthrough', config['predictors']['boolean'])]
    pre = ColumnTransformer(parts, remainder='drop')
    estimator = Ridge(alpha=alpha) if model_id == 'M4' else LinearRegression()
    return Pipeline([('preprocess', pre), ('model', estimator)])


def evaluate_cv(pipeline, train, cv, config, model_id, variant):
    """Không nhận test; RMSE trung bình fold khác căn của MSE trung bình fold."""
    scores = cross_validate(pipeline, train[predictor_names(config)], train[config['target']], cv=cv,
                            scoring={'mse': 'neg_mean_squared_error', 'mae': 'neg_mean_absolute_error',
                                     'r2': 'r2'}, return_train_score=True, n_jobs=1, error_score='raise')
    rows = []
    for fold in range(len(cv)):
        row = {'model_id': model_id, 'variant': variant, 'fold': fold,
               'n_fold_train': len(cv[fold][0]), 'n_fold_validation': len(cv[fold][1]),
               'protocol_id': config['protocol_id']}
        for part, prefix in [('test', 'validation'), ('train', 'train')]:
            row[prefix + '_mse'] = -scores[part + '_mse'][fold]
            row[prefix + '_rmse'] = np.sqrt(row[prefix + '_mse'])
            row[prefix + '_mae'] = -scores[part + '_mae'][fold]
            row[prefix + '_r2'] = scores[part + '_r2'][fold]
        rows.append(row)
    folds = pd.DataFrame(rows)
    summary = {'model_id': model_id, 'variant': variant, 'protocol_id': config['protocol_id'],
               'n_train': len(train), 'n_folds': len(cv)}
    for part, prefix in [('validation', 'cv'), ('train', 'fold_train')]:
        for metric in ['mse', 'rmse', 'mae', 'r2']:
            summary[prefix + '_' + metric + '_mean'] = folds[part + '_' + metric].mean()
            summary[prefix + '_' + metric + '_std'] = folds[part + '_' + metric].std(ddof=1)
    return summary, folds
