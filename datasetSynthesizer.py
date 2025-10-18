import pandas as pd
import numpy as np

def synthesize_training_dataset(num_samples_per_material=1000, output_filename='trainingDataset.csv'):
    materials_library = [
        {'material_name': 'Standard Steel', 'thermal_conductivity': 50, 'cost_per_kg': 1, 'density': 7850},
        {'material_name': 'Aluminum-6061 Alloy', 'thermal_conductivity': 180, 'cost_per_kg': 3.5, 'density': 2700},
        {'material_name': 'Copper C110', 'thermal_conductivity': 385, 'cost_per_kg': 9, 'density': 8940},
        {'material_name': 'Graphene-Infused Polymer', 'thermal_conductivity': 600, 'cost_per_kg': 80, 'density': 1200},
        {'material_name': 'Synthetic Diamond Substrate', 'thermal_conductivity': 2200, 'cost_per_kg': 500, 'density': 3510},
        {'material_name': 'Copper Foam Matrix', 'thermal_conductivity': 150, 'cost_per_kg': 25, 'density': 900},
        {'material_name': 'Phase-Change Material (PCM)', 'thermal_conductivity': 0.6, 'cost_per_kg': 15, 'density': 1500},
        {'material_name': 'Silica Aerogel Composite', 'thermal_conductivity': 0.02, 'cost_per_kg': 20, 'density': 150},
        {'material_name': 'Pyrolytic Graphite Sheet', 'thermal_conductivity': 1500, 'cost_per_kg': 120, 'density': 2200}
    ]

    all_experiments = []

    for material in materials_library:
        for _ in range(num_samples_per_material):
            llm_thermal_output = np.random.uniform(350, 750)
            cooling_system_type = np.random.randint(0, 3)
            ambient_temperature = np.random.uniform(18, 32)
            
            # Additional Material Properties for Specific Materials lol (trying to make synthesis as accurate as possible)
            effective_conductivity = material['thermal_conductivity']
            if material['material_name'] == 'Copper Foam Matrix' and cooling_system_type > 0:
                effective_conductivity *= (1 + cooling_system_type * 1.5)
            pcm_gain_bonus = 0
            if material['material_name'] == 'Phase-Change Material (PCM)' and llm_thermal_output > 650:
                 pcm_gain_bonus = 5 * np.random.uniform(0.8, 1.2)

            # The confusing part: i add pue baseline and other stuff usually from llm presets because dataset is labelled
            log_conductivity = np.log1p(effective_conductivity)
            baseline_pue = 1.8

            # created labelled data as accurately as possible (according to physics bruh)
            cooling_multiplier = [1.0, 1.8, 2.5][cooling_system_type]
            thermal_efficiency_score = log_conductivity * cooling_multiplier
            pue_reduction = (thermal_efficiency_score / 30) * np.random.uniform(0.9, 1.1)
            predicted_pue = max(1.05, min(baseline_pue - pue_reduction, 1.8))
            throttling_reduction_score = (thermal_efficiency_score * 2) / (llm_thermal_output / 100)
            predicted_throughput_gain = pcm_gain_bonus + max(0, min(throttling_reduction_score, 25.0))

            all_experiments.append({
                'material_thermal_conductivity': material['thermal_conductivity'], 'material_cost_per_kg': material['cost_per_kg'],
                'material_density': material['density'], 'llm_current_cooling_type': cooling_system_type,
                'llm_ambient_temperature': ambient_temperature, 'llm_thermal_output': llm_thermal_output,
                'predicted_pue': round(predicted_pue, 4),
                'predicted_throughput_gain': round(predicted_throughput_gain, 4)
            })

    df = pd.DataFrame(all_experiments)
    df.to_csv(output_filename, index=False)

if __name__ == '__main__':
    synthesize_training_dataset()