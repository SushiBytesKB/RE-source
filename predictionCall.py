import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

MODEL_PATH = 'ai_model.joblib'
PRESETS_PATH = 'llmPreset.csv'
MATERIALS_PATH = 'trainingDataset.csv'

if os.path.exists(MODEL_PATH):
    MODEL = joblib.load(MODEL_PATH)
else:
    print(f"Error: Model file not found at '{MODEL_PATH}'.")
    MODEL = None

try:
    LLM_PRESETS = pd.read_csv(PRESETS_PATH)
    MATERIALS_DF = pd.read_csv(MATERIALS_PATH).drop_duplicates(subset=['material_thermal_conductivity']).reset_index(drop=True)
    # We need to identify the names of the elements that are not in the dataset
    material_names_map = {180: 'Aluminum-6061 Alloy', 385: 'Copper C110', 600: 'Graphene-Infused Polymer', 1500: 'Pyrolytic Graphite Sheet', 150: 'Copper Foam Matrix'}
    MATERIALS_DF['material_name'] = MATERIALS_DF['material_thermal_conductivity'].map(material_names_map).fillna('Unknown Material')
except FileNotFoundError as e:
    print(f"Error: Data file not found: {e}. Please ensure all CSV files and the model file are present.")
    LLM_PRESETS = None
    MATERIALS_DF = None


MODEL_PATH = 'ai_model.joblib'
PRESETS_PATH = 'llmPreset.csv'
MATERIALS_DATA_PATH = 'trainingDataset.csv' 

try:
    MODEL = joblib.load(MODEL_PATH)
    LLM_PRESETS = pd.read_csv(PRESETS_PATH)
    MATERIALS_LIBRARY = pd.read_csv(MATERIALS_DATA_PATH).drop_duplicates(subset=['material_thermal_conductivity']).reset_index(drop=True)
    # gotta get the names of the elements cuz it aint in the training dataset
    material_names_map = {
        50: 'Standard Steel', 180: 'Aluminum-6061 Alloy', 385: 'Copper C110',
        600: 'Graphene-Infused Polymer', 2200: 'Synthetic Diamond Substrate',
        150: 'Copper Foam Matrix', 0.6: 'Phase-Change Material (PCM)',
        0.02: 'Silica Aerogel Composite', 1500: 'Pyrolytic Graphite Sheet'
    }
    MATERIALS_LIBRARY['material_name'] = MATERIALS_LIBRARY['material_thermal_conductivity'].map(material_names_map)

except FileNotFoundError as e:
    print(f"\nA required file was not found: {e.filename}")
    MODEL = None 
    
app = Flask(__name__)
CORS(app) 

@app.route('/predict', methods=['POST'])
def handle_prediction_request():
    if MODEL is None:
        return jsonify({"error": "Server is not initialized correctly. Check server logs."}), 500

    # 1. Get the JSON data sent from the website
    data = request.get_json()
    llm_name = data.get('llm_name')
    user_constraints = data.get('user_constraints')

    if not all([llm_name, user_constraints]):
        return jsonify({"error": "Missing 'llm_name' or 'user_constraints' in request."}), 400

    # 2. Look up the correct LLM baseline from the loaded presets
    baseline_series = LLM_PRESETS[LLM_PRESETS['llm_name'] == llm_name]
    if baseline_series.empty:
        return jsonify({"error": f"LLM preset for '{llm_name}' not found."}), 404
    baseline = baseline_series.iloc[0]

    # 3. Simulate and predict outcomes for every material in the library
    all_results = []
    for _, material in MATERIALS_LIBRARY.iterrows():
        # Prepare the input data for the model in the exact format it was trained on
        input_df = pd.DataFrame([{'material_thermal_conductivity': material['material_thermal_conductivity'], 'material_cost_per_kg': material['material_cost_per_kg'],
            'material_density': material['material_density'], 'llm_current_cooling_type': baseline['llm_current_cooling_type'],
            'llm_ambient_temperature': baseline['llm_ambient_temperature'], 'llm_thermal_output': baseline['llm_thermal_output']}])
        
        # Get the raw physics prediction from the pre-trained model
        prediction = MODEL.predict(input_df)[0]
        predicted_pue_100, predicted_gain_100 = prediction[0], prediction[1]

        # 4. Apply the business logic to convert physics predictions into user-facing metrics
        replacement_percentage = user_constraints.get('replacement_percentage', 100)
        
        # Calculate emissions reduction based on PUE improvement
        energy_savings_100 = (baseline['baseline_pue'] - predicted_pue_100) / baseline['baseline_pue']
        final_emissions_reduction = energy_savings_100 * (replacement_percentage / 100.0)
        
        # Calculate the upfront cost impact as a percentage of the annual energy budget
        upfront_capex_100 = material['material_cost_per_kg'] * (baseline['llm_thermal_output'] * 0.1) # Cost scaling factor
        scaled_capex = upfront_capex_100 * (replacement_percentage / 100.0)
        final_cost_impact = (scaled_capex / baseline['llm_current_maintenance_cost']) * 100
        
        # Scale the performance gain
        final_performance_gain = predicted_gain_100 * (replacement_percentage / 100.0)

        all_results.append({
            'name': material['material_name'], 
            'cost_impact': final_cost_impact,
            'emissions_reduction': final_emissions_reduction * 100, 
            'performance_gain': final_performance_gain
        })

    # 5. Filter the results based on the user's constraints
    budget_cap = user_constraints.get('budget_cap', 100)
    emissions_min = user_constraints.get('emissions_min', 0)
    
    suitable_materials = [
        res for res in all_results 
        if res['cost_impact'] <= budget_cap and res['emissions_reduction'] >= emissions_min
    ]
    
    # 6. Sort the final list by the most emissions reduction
    suitable_materials.sort(key=lambda x: x['emissions_reduction'], reverse=True)
    
    # 7. Send the final, clean list back to the website
    return jsonify({'suitable_materials': suitable_materials})

if __name__ == '__main__':
    if MODEL is not None:
        print("Server is running and ready for requests at http://127.0.0.1:5000")
        app.run(port=5001, debug=False)
    else:
        print("Server startup failed due to missing files. Please resolve the errors above.")
