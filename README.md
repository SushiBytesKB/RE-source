RE-source: AI-Powered Material Discovery Engine

RE-source is a modern, data-driven web application designed to optimize material selection for engineering and manufacturing projects. Instead of relying on traditional catalogs, this engine uses a machine learning model to instantly recommend the best materials based on three critical business metrics.

Project Goal

To provide actionable, data-backed material recommendations that help users:

Reduce Cost Impact 

Lower Emissions 

Maximize Performance Gain 

How It Works

The application follows a simple, yet powerful three-step process:

Input: The user provides target values for Cost Impact, Emissions Reduction, and Performance Gain via the web interface.

Prediction: The Flask backend routes the user's inputs to a pre-trained XGBoost Regressor Model which analyzes potential materials in real-time.

Output: The application displays the material recommendations that best fit the user's constraints.

Libraries used:
pandas, xgboost, sklearn, joblib, flask, numpy
