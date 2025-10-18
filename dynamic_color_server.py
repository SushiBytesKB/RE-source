import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv


load_dotenv()
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception as e:
    print(f"Could not configure Gemini API: {e}")

# set prompt
system_prompt = "You are an AI that generates color palettes for a website based on an environmental impact score which will be the Emissions reduced score. The score is given as a number between 0 and 100, where: 0 = catastrophic for the environment 100 = extremely sustainable You must output exactly 8 hexcode colors in this order: Header 1 Header 2 Text Main body background color (use this format: 'linear-gradient(45deg, #60a5fa, #hexcode of color)') Card element background color (use thisFormat: 'linear-gradient(45deg, #60a5fa, #hexcode of color)') Card element header color Input text field color Buttons Guidelines: Lower scores (0–30) → dark, alarming, polluted tones, husky, burnt (can be other than red) Middle scores (31–70) → neutral, foggy, or transitional palettes, not evoking strong feelings High scores (71–100) → bright, calm, nature-inspired, happy All colors must include hexcode values, where the alpha channel also reflects intensity or transparency emotionally (e.g., lower alpha for gloomier moods). The palette must be visually harmonious as a full set. The color palette must feel moody, harmonic, and emotionally coherent, reflecting the environmental impact of the result. The colors must impact the viewers feelings. Output only the hexcode color arrays in this exact structure — no explanations, no labels, no line breaks Like this #hexcode, #hexcode, #hexcode, #hexcode, #hexcode, #hexcode, #hexcode, #hexcode";


# 3. initialize model
model = genai.GenerativeModel(
    'gemini-2.5-pro', 
    system_instruction=system_prompt
)

# setup server
app = Flask(__name__)

#  API endpoint
@app.route('/api/generate', methods=['POST'])
def generate_palette():
    try:
        # Get the variable (prompt) from the frontend
        data = request.get_json()
        score = data.get('score')

        if score is None:
            return jsonify({"error": "Score is required"}), 400

        user_prompt = f"Generate a palette for an environmental score of {score}."
        
        response = model.generate_content(user_prompt)
        
        # Return the AI's raw text response
        return jsonify({"palette": response.text.strip()})

    except Exception as e:
        print(f"Error during color generation: {e}")
        return jsonify({"error": "Failed to generate color palette"}), 500

# Run the server
if __name__ == '__main__':
    # Running on port 5002 to avoid conflicts
    port = 5002
    print(f"Dynamic Color AI Server is running at http://127.0.0.1:{port}")
    app.run(port=port, debug=False)