"""
Train GBM baseline for regression (predict Market_High) and classification (WithinRange).
Produces simple rolling evaluation and saves model and metrics.
Supports LightGBM with automated fallback to scikit-learn HistGradientBoosting.
"""
import os
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, accuracy_score, precision_score, recall_score, f1_score
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import MODELS_DIR, PROCESSED_DATA_DIR, find_file
except ImportError:
    from config import MODELS_DIR, PROCESSED_DATA_DIR, find_file

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
    HAS_LIGHTGBM = False

INFILE = str(find_file('merged_predictions_1year.csv'))

print('Loading', INFILE)
df = pd.read_csv(INFILE, parse_dates=['Date'])
df = df.sort_values('Date')

# drop rows with missing market values
df = df.dropna(subset=['Market_High', 'Market_Low'])

# classification target: whether both market high and low are inside predicted range
df['WithinHigh'] = (df['Market_High'] <= df['Resistance']).astype(int)
df['WithinLow'] = (df['Market_Low'] >= df['Support']).astype(int)
df['WithinRange'] = ((df['WithinHigh'] == 1) & (df['WithinLow'] == 1)).astype(int)

# basic features
df['DayOfWeek'] = df['Date'].dt.dayofweek
src_dummies = pd.get_dummies(df['Source'], prefix='src')
X_num = df[['Support', 'Resistance', 'RangeWidth', 'RangeMid', 'DayOfWeek']]
X = pd.concat([X_num.reset_index(drop=True), src_dummies.reset_index(drop=True)], axis=1)

y_reg = df['Market_High']
y_clf = df['WithinRange']

# TimeSeriesSplit evaluation
ts = TimeSeriesSplit(n_splits=5)
rmse_scores = []
clf_acc = []
clf_prec = []
clf_rec = []
clf_f1 = []
fold = 0
models = {}

for train_idx, val_idx in ts.split(X):
    fold += 1
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y_reg.iloc[train_idx], y_reg.iloc[val_idx]

    if HAS_LIGHTGBM:
        dtrain = lgb.Dataset(X_train, label=y_train)
        dval = lgb.Dataset(X_val, label=y_val, reference=dtrain)
        params = {'objective': 'regression', 'metric': 'rmse', 'verbosity': -1}
        model = lgb.train(params, dtrain, num_boost_round=1000, valid_sets=[dtrain, dval], callbacks=[lgb.early_stopping(50, verbose=False)])
        preds = model.predict(X_val, num_iteration=model.best_iteration)
        
        clf = lgb.LGBMClassifier(n_estimators=200, verbosity=-1)
        clf.fit(X_train, y_clf.iloc[train_idx])
        preds_clf = clf.predict(X_val)
    else:
        reg = HistGradientBoostingRegressor(max_iter=200, random_state=42)
        reg.fit(X_train, y_train)
        preds = reg.predict(X_val)
        model = reg

        clf = HistGradientBoostingClassifier(max_iter=200, random_state=42)
        clf.fit(X_train, y_clf.iloc[train_idx])
        preds_clf = clf.predict(X_val)

    rmse = np.sqrt(mean_squared_error(y_val, preds))
    rmse_scores.append(rmse)
    print(f'Fold {fold} Regression RMSE: {rmse:.4f}')
    models[f'gbr_fold{fold}'] = model

    acc = accuracy_score(y_clf.iloc[val_idx], preds_clf)
    prec = precision_score(y_clf.iloc[val_idx], preds_clf, zero_division=0)
    rec = recall_score(y_clf.iloc[val_idx], preds_clf, zero_division=0)
    f1 = f1_score(y_clf.iloc[val_idx], preds_clf, zero_division=0)
    clf_acc.append(acc)
    clf_prec.append(prec)
    clf_rec.append(rec)
    clf_f1.append(f1)
    print(f'Fold {fold} Classifier Acc: {acc:.4f} Prec: {prec:.4f} Rec: {rec:.4f} F1: {f1:.4f}')
    models[f'clf_fold{fold}'] = clf

# Save models and metrics
model_path = os.path.join(MODELS_DIR, 'models_lgb_folds.joblib')
joblib.dump(models, model_path)
metrics = {
    'rmse_mean': float(np.mean(rmse_scores)),
    'rmse_std': float(np.std(rmse_scores)),
    'clf_acc_mean': float(np.mean(clf_acc)),
    'clf_prec_mean': float(np.mean(clf_prec)),
    'clf_rec_mean': float(np.mean(clf_rec)),
    'clf_f1_mean': float(np.mean(clf_f1))
}

metrics_path = os.path.join(MODELS_DIR, 'training_metrics.json')
with open(metrics_path, 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2)

print('Training complete. Metrics saved to', metrics_path)
print(metrics)
