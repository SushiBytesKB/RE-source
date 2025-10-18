import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import numpy as np

MODEL_PATH = 'ai_model.joblib'
PRESETS_PATH = 'llmPreset.csv'
MATERIALS_DATA_PATH = 'trainingDataset.csv' 

try:
    MODEL = joblib.load(MODEL_PATH)
    LLM_PRESETS = pd.read_csv(PRESETS_PATH)
    MATERIALS_LIBRARY = pd.read_csv(MATERIALS_DATA_PATH).drop_duplicates(subset=['material_thermal_conductivity']).reset_index(drop=True)
    # This map ensures material names are correctly assigned
    material_names_map = {
        50: 'Standard Steel', 180: 'Aluminum-6061 Alloy', 385: 'Copper C110', 600: 'Graphene-Infused Polymer',
        2200: 'Synthetic Diamond Substrate', 150: 'Copper Foam Matrix', 0.6: 'Phase-Change Material (PCM)',
        0.02: 'Silica Aerogel Composite', 1500: 'Pyrolytic Graphite Sheet'
    }
    MATERIALS_LIBRARY['material_name'] = MATERIALS_LIBRARY['material_thermal_conductivity'].map(material_names_map)
    print("[SUCCESS] All models and data files loaded.")
except FileNotFoundError as e:
    print(f"\n[FATAL ERROR] A required file was not found: {e.filename}. Please run the dataset and training scripts.")
    MODEL = None
    
app = Flask(__name__)
CORS(app) 

@app.route('/predict', methods=['POST'])
def handle_prediction_request():
    if MODEL is None:
        return jsonify({"error": "Model is not loaded. Please check server logs."}), 500

    # 1. Get data from the website's request
    data = request.get_json()
    llm_name = data.get('llm_name')
    user_constraints = data.get('user_constraints')

    # 2. Find the baseline stats for the selected LLM
    try:
        baseline_series = LLM_PRESETS[LLM_PRESETS['llm_name'] == llm_name]
        if baseline_series.empty:
            return jsonify({"error": f"LLM preset '{llm_name}' not found."}), 400
        baseline = baseline_series.iloc[0]
    except Exception as e:
        return jsonify({"error": f"Error processing LLM presets: {e}"}), 500

    # 3. Simulate and evaluate every material in the library
    all_results = []
    for _, material in MATERIALS_LIBRARY.iterrows():
        # Prepare input for the AI model
        input_df = pd.DataFrame([{
            'material_thermal_conductivity': material['material_thermal_conductivity'],
            'material_cost_per_kg': material['material_cost_per_kg'],
            'material_density': material['material_density'],
            'llm_current_cooling_type': baseline['llm_current_cooling_type'],
            'llm_ambient_temperature': baseline['llm_ambient_temperature'],
            'llm_thermal_output': baseline['llm_thermal_output']
        }])
        
        # Get raw prediction from the AI model
        prediction = MODEL.predict(input_df)[0]
        pue_100, gain_100 = prediction[0], prediction[1]
        
        # 4. Apply business logic to convert raw predictions to final metrics
        replacement_percentage = user_constraints.get('replacement_percentage', 100)
        
        energy_savings_100 = (baseline['baseline_pue'] - pue_100) / baseline['baseline_pue']
        final_emissions_reduction = energy_savings_100 * (replacement_percentage / 100.0)
        
        upfront_capex_100 = material['material_cost_per_kg'] * (baseline['llm_thermal_output'] * 0.1)
        scaled_capex = upfront_capex_100 * (replacement_percentage / 100.0)
        final_cost_impact = (scaled_capex / baseline['llm_current_maintenance_cost']) * 100
        
        final_performance_gain = gain_100 * (replacement_percentage / 100.0)

        all_results.append({
            'name': material['material_name'], 
            'cost_impact': final_cost_impact,
            'emissions_reduction': final_emissions_reduction * 100, 
            'performance_gain': final_performance_gain
        })

    # 5. Filter and sort the results based on user constraints
    budget_cap = user_constraints.get('budget_cap', 100)
    emissions_min = user_constraints.get('emissions_min', 0)
    suitable_materials = [res for res in all_results if res['cost_impact'] <= budget_cap and res['emissions_reduction'] >= emissions_min]
    
    # This loop fixes the float32 JSON error
    for material in suitable_materials:
        for key, value in material.items():
            if isinstance(value, (np.float32, np.float64)):
                material[key] = float(value)
            
    suitable_materials.sort(key=lambda x: x['emissions_reduction'], reverse=True)
    
    # 6. Send the final, clean list back to the website
    return jsonify({'suitable_materials': suitable_materials})

if __name__ == '__main__':
    if MODEL is not None:
        port = 5001
        print(f"Prediction Server is running at http://127.0.0.1:{port}")
        app.run(port=port, debug=False)

