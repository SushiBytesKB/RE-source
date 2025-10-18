fetch("colors.json")
  .then((response) => response.json())
  .then((colors) => {
    const root = document.documentElement;
    for (const key in colors) {
      root.style.setProperty(`--${key}`, colors[key]);
    }
  })
  .catch((error) => console.error("Error fetching colors:", error));

let resultsChart = null;

async function getPredictions() {
  const llmModel = document.getElementById("llmModel").value;
  const budgetCap = parseFloat(document.getElementById("budgetCap").value);
  const emissionsMin = parseFloat(
    document.getElementById("emissionsMin").value
  );
  const replacementPercentage = parseFloat(
    document.getElementById("replacementPercentage").value
  );

  const resultsBox = document.getElementById("resultsBox");
  const resultsList = document.getElementById("resultsList");
  const chartCard = document.getElementById("chartCard");
  const submitBtn = document.getElementById("submitBtn");

  if (isNaN(budgetCap) || isNaN(emissionsMin) || isNaN(replacementPercentage)) {
    resultsList.innerHTML =
      "<h3>Error</h3><p>Please enter valid numbers in all fields.</p>";
    chartCard.style.display = "none";
    resultsBox.classList.remove("hidden-box");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Analyzing...";
  resultsList.innerHTML =
    "<h3>Communicating with the AI model...</h3><p>This may take a moment.</p>";
  chartCard.style.display = "none";
  resultsBox.classList.remove("hidden-box");

  const requestBody = {
    llm_name: llmModel,
    user_constraints: {
      budget_cap: budgetCap,
      emissions_min: emissionsMin,
      replacement_percentage: replacementPercentage,
    },
  };

  try {
    const response = await fetch("http://127.0.0.1:5001/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.error || `HTTP error! Status: ${response.status}`
      );
    }

    const data = await response.json();
    displayResults(data.suitable_materials);
  } catch (error) {
    console.error("Error fetching predictions:", error);
    resultsList.innerHTML = `<h3>An Error Occurred</h3><p>Could not connect to the prediction server. Please ensure the 'predictionCall.py' script is running correctly.</p><p class="error-details">Details: ${error.message}</p>`;
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Analyze Materials";
  }
}

function displayResults(materials) {
  const resultsList = document.getElementById("resultsList");
  const chartCard = document.getElementById("chartCard");

  if (!materials || materials.length === 0) {
    resultsList.innerHTML =
      "<h3>No Suitable Materials Found</h3><p>No materials in our library meet your specific budget and emissions criteria. Try relaxing your constraints.</p>";
    chartCard.style.display = "none";
    if (resultsChart) {
      resultsChart.destroy();
    }
    return;
  }

  let html = "<h3>Recommended Materials (Ranked)</h3><ul>";
  materials.forEach((material) => {
    html += `
            <li>
                <strong>${material.name}</strong>
                <ul>
                    <li class="emissions">Emissions Reduction: <strong>${material.emissions_reduction.toFixed(
                      2
                    )}%</strong></li>
                    <li class="cost">Upfront Cost Impact: <strong>+${material.cost_impact.toFixed(
                      2
                    )}%</strong></li>
                    <li class="performance">Performance Gain: <strong>+${material.performance_gain.toFixed(
                      2
                    )}%</strong></li>
                </ul>
            </li>`;
  });
  html += "</ul>";
  resultsList.innerHTML = html;

  chartCard.style.display = "block";
  renderChart(materials);
}

function renderChart(materials) {
  const ctx = document.getElementById("resultsChart").getContext("2d");

  if (resultsChart) {
    resultsChart.destroy();
  }

  resultsChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: materials.map((m) => m.name),
      datasets: [
        {
          label: "Emissions Reduction (%)",
          data: materials.map((m) => m.emissions_reduction),
          backgroundColor: "rgba(54, 162, 235, 0.7)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
          yAxisID: "y",
        },
        {
          label: "Upfront Cost Impact (%)",
          data: materials.map((m) => m.cost_impact),
          backgroundColor: "rgba(255, 99, 132, 0.7)",
          borderColor: "rgba(255, 99, 132, 1)",
          borderWidth: 1,
          yAxisID: "y1",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: "Cost vs. Emissions Reduction" },
        tooltip: { mode: "index", intersect: false },
      },
      scales: {
        x: { stacked: false },
        y: {
          type: "linear",
          display: true,
          position: "left",
          title: { display: true, text: "Emissions Reduction (%)" },
        },
        y1: {
          type: "linear",
          display: true,
          position: "right",
          title: { display: true, text: "Cost Impact (%)" },
          grid: { drawOnChartArea: false },
        },
      },
    },
  });
}
