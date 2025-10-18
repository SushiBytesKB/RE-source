 fetch('colors.json')
      .then(response => response.json())
      .then(colors => {
        for (const key in colors) {
          document.documentElement.style.setProperty(`--${key}`, colors[key]);
        }
      })
      .catch(error => console.error('Error fetching colors:', error));
    

function collectInput() {
    
    const inputBudget = document.getElementById('BudgetCap'); 
    const inputEmissions = document.getElementById('ExpectedEmissions');
    //need the third value
    // document.getElementById('output').textContent = "Submitted";

    const myBox = document.getElementById('myBox');

    myBox.classList.remove('hidden-box');
    
}