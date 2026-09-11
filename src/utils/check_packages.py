import importlib
pkgs=['sklearn','lightgbm','joblib']
for p in pkgs:
    try:
        importlib.import_module(p)
        print(p+' ok')
    except Exception as e:
        print(p+' ERROR', e)
