import pandas as pd
import xgboost as xgb
from sklearn.multioutput import MultiOutputRegressor
import joblib

def train_and_save_model(dataset_path='trainingDataset.csv', model_output_path='ai_model.joblib'):
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"Error: Dataset file not found at '{dataset_path}'.")
        return

    features = [
        'material_thermal_conductivity', 'material_cost_per_kg', 'material_density',
        'llm_current_cooling_type', 'llm_ambient_temperature', 'llm_thermal_output'
    ]
    targets = ['predicted_pue', 'predicted_throughput_gain']
    
    X = df[features]
    y = df[targets]
    
    model = MultiOutputRegressor(xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42))
    model.fit(X, y)
    
    joblib.dump(model, model_output_path)

if __name__ == '__main__':
    train_and_save_model()