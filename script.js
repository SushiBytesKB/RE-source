fetch('colors.json')
       .then(response => {
           if (!response.ok) {
               throw new Error(`HTTP error! status: ${response.status}`);
           }
           return response.json();
       })
       .then(colors => {
           const root = document.documentElement;
           for (const key in colors) {
               // Set each key as a CSS variable: --key: value
               root.style.setProperty(`--${key}`, colors[key]);
           }
       })
       .catch(error => console.error('Error fetching or applying colors:', error));

function collectInput() {
    
    const inputBudget = document.getElementById('BudgetCap'); 
    const inputEmissions = document.getElementById('ExpectedEmissions');
    //need the third value
    // document.getElementById('output').textContent = "Submitted";

    const myBox = document.getElementById('myBox');

    myBox.classList.remove('hidden-box');
    
}