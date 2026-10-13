"""Kiểm tra bàn giao có ý nghĩa: cùng mẫu/folds, không leakage, số liệu đúng.

Chạy từ root: python scripts/verify_b_handoff.py
Không chỉnh raw, target, các bảng A hoặc holdout. Kết quả lưu reports/b_verification.json.
"""
import sys,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from scipy.stats import pearsonr, f_oneway

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.experiment import load_data, load_protocol, predictor_names, build_pipeline

def verify(checked_on=None):
    checks=[]
    def ok(label,condition):
        if not condition: raise AssertionError(label)
        checks.append(label)
    config,train,test,cv=load_protocol()
    df=load_data()
    manifest=pd.read_csv(ROOT/config['split']['manifest'])
    exp_train,exp_test=train_test_split(np.arange(len(df)),test_size=.2,random_state=0)
    ok('Holdout exactly matches seed0/test_size=.2; no reselect by target',
       set(exp_train)==set(np.flatnonzero(manifest.split.eq('train')))
       and set(exp_test)==set(np.flatnonzero(manifest.split.eq('test'))))
    ok('Train/test trace keys disjoint and exhaustive',
       len(train)==41365 and len(test)==10342 and not manifest[['source_file','source_row']].duplicated().any())
    valid_all=np.concatenate([valid for _,valid in cv])
    ok('CV validation covers each train row once, excludes holdout',
       np.array_equal(np.sort(valid_all),np.arange(len(train)))
       and all(len(np.intersect1d(t,v))==0 for t,v in cv)
       and manifest.loc[manifest.split.eq('test'),'cv_fold'].eq(-1).all())
    preds=predictor_names(config)
    ok('Predictors exclude every trace/target-derived and unknown-metadata column',
       len(preds)==len(set(preds)) and not set(preds).intersection(config['excluded_predictors']))
    original=pd.read_csv(ROOT/'data/processed/airbnb_combined.csv')
    ok('No target transformation/clipping: values and all rows intact',original.equals(df))
    group=pd.read_csv(ROOT/'outputs/tables/eda_group_summary.csv')
    ok('Each grouping count reconciles to 51707',group.groupby('grouping').n.sum().eq(51707).all())
    ok('No-observation groups retain missing price, not zero',group.loc[group.n.eq(0),'median'].isna().all())
    for name in ['amsterdam','athens','london']:
        actual=df[df.city.eq(name)].realSum.median()
        saved=group[(group.grouping=='city')&(group.city==name)]['median'].iloc[0]
        ok('Independent median agrees for '+name,bool(np.isclose(actual,saved)))
    pearson=pd.read_csv(ROOT/'outputs/tables/pearson_price_evidence.csv')
    r=pearson[(pearson.scope=='full_descriptive')&(pearson.context=='all_cities')&(pearson.feature=='person_capacity')].r.iloc[0]
    ok('Independent NumPy Pearson agrees',bool(np.isclose(r,np.corrcoef(df.person_capacity,df.realSum)[0,1])))
    anova=pd.read_csv(ROOT/'outputs/tables/anova_price_evidence.csv')
    expected=f_oneway(*[g.realSum.to_numpy() for _,g in df.groupby('room_type')]).statistic
    saved=anova[(anova.scope=='full_descriptive')&(anova.context=='all_cities')&(anova.feature=='room_type')].f.iloc[0]
    ok('Independent ANOVA groups/F agree',bool(np.isclose(saved,expected)))
    ok('Underflow p explicitly marked and not published as exact zero',
       pearson.loc[pearson.p_underflow,'p_value'].isna().all()
       and anova.loc[anova.p_underflow,'p_value'].isna().all())
    # Kiểm nhánh M2 A sẽ dùng: scaler chỉ fit trên một train fold.
    fold_train,fold_valid=cv[0]
    pipeline=build_pipeline('M2',config)
    pipeline.fit(train.iloc[fold_train][preds],train.iloc[fold_train].realSum)
    scaler=pipeline.named_steps['preprocess'].named_transformers_['numeric']
    ok('Numeric scaler fit on CV training fold only',
       np.allclose(scaler.mean_,train.iloc[fold_train][config['predictors']['numeric']].mean().to_numpy()))
    x=train.iloc[fold_valid[:25]].copy()
    prediction=pipeline.predict(x)
    x['price_tier']=x.realSum; x['log_price_temp']=x.realSum*100; x['source_row']=-999
    ok('Column allowlist drops target-derived/trace extras',np.allclose(prediction,pipeline.predict(x)))
    unknown=x.copy();unknown['city']='new_city_not_in_training'
    ok('Unseen category transforms without failure',np.isfinite(pipeline.predict(unknown)).all())
    summary=pd.read_csv(ROOT/'outputs/tables/b_models_cv_summary.csv')
    folds=pd.read_csv(ROOT/'outputs/tables/b_models_cv_folds.csv')
    ok('B ran 9 configs x5 folds, selected 1 per family',
       len(summary)==9 and len(folds)==45 and summary.selected_within_family.sum()==2)
    ok('Metric identities preserved per fold',
       np.allclose(folds.validation_rmse**2,folds.validation_mse))
    ok('CV summaries agree with mean fold metrics',all(
       np.isclose(row.cv_mse_mean,folds[(folds.model_id==row.model_id)&(folds.variant==row.variant)].validation_mse.mean())
       for row in summary.itertuples()))
    ok('No test metrics in B summary',not any('test' in c for c in summary.columns))
    for model_id in ['M3','M4']:
        model=joblib.load(ROOT/f'models/{model_id}_B_train_only.joblib')
        ok(model_id+' saved train-only model usable',np.isfinite(model.predict(train.iloc[:10][preds])).all())
    for name in ['02_exploratory_data_analysis.ipynb','03b_polynomial_ridge.ipynb']:
        nb=json.loads((ROOT/'notebooks'/name).read_text(encoding='utf-8'))
        cells=[c for c in nb['cells'] if c['cell_type']=='code']
        ok(name+' executed completely without stored errors',all(c.get('execution_count') is not None
           and not any(o['output_type']=='error' for o in c.get('outputs',[])) for c in cells))
    result={'checked_on':checked_on,'passed':True,'checks':checks,'n_checks':len(checks),
            'n_train':len(train),'n_test':len(test),'test_model_metrics_computed':False}
    (ROOT/'reports/b_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    import argparse
    from datetime import date
    parser=argparse.ArgumentParser()
    parser.add_argument('--checked-on',help='Ngày kiểm tra YYYY-MM-DD; để trống thì không tự ghi ngày')
    args=parser.parse_args()
    if args.checked_on: date.fromisoformat(args.checked_on)
    verify(args.checked_on)
