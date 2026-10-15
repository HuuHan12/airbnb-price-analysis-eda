"""Build-time split reconstruction; emitted directly into the final notebook."""
PORTABLE_IO = {13: '# Giữ nguyên thuật toán, thứ tự dòng và seed 0; tái tạo trong bộ nhớ.\n'
     'expected_train, expected_test = train_test_split(np.arange(len(df)), test_size=.2, random_state=0)\n'
     'expected_train = np.sort(expected_train)\n'
     "manifest = df[config['trace_keys']].copy()\n"
     "manifest['split'], manifest['cv_fold'] = 'test', -1\n"
     "manifest.loc[expected_train, 'split'] = 'train'\n"
     'for fold, (_, valid_pos) in enumerate(KFold(5, shuffle=True, random_state=0).split(expected_train)):\n'
     "    manifest.loc[expected_train[valid_pos], 'cv_fold'] = fold\n"
     'manifest_hash = hashlib.sha256(manifest.to_csv(index=False, '
     "lineterminator='\\n').encode('utf-8')).hexdigest()\n"
     "assert manifest_hash == '5b2144d1e338e1cb12389ba4bcd26888dd46eb93b8e8c28942f3bef1c9e101fb', "
     "'Split/fold khác bản đã chốt'\n"
     "assert np.array_equal(np.flatnonzero(manifest.split.eq('train')), expected_train)\n"
     "assert np.array_equal(np.flatnonzero(manifest.split.eq('test')), np.sort(expected_test))\n"
     "assert manifest.loc[manifest.split.eq('test'), 'cv_fold'].eq(-1).all()\n"
     "train = df.loc[manifest.split.eq('train')].reset_index(drop=True)\n"
     "test = df.loc[manifest.split.eq('test')].reset_index(drop=True)\n"
     "train_folds = manifest.loc[manifest.split.eq('train'), 'cv_fold'].to_numpy()\n"
     'cv = [(np.flatnonzero(train_folds != fold), np.flatnonzero(train_folds == fold)) for fold in '
     'range(5)]\n'
     'for fold, (fit_idx, valid_idx) in enumerate(KFold(5, shuffle=True, random_state=0).split(train)):\n'
     '    assert np.array_equal(cv[fold][0], fit_idx) and np.array_equal(cv[fold][1], valid_idx)\n'
     'assert len(train) == 41365 and len(test) == 10342\n'
     'assert set(train_folds) == set(range(5))\n'
     "display(pd.DataFrame([{'fold': f, 'fit': len(a), 'validation': len(b)} for f, (a,b) in "
     'enumerate(cv)]))'}
