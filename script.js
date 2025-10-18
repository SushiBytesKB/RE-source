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
               root.style.setProperty(`--${key}`, colors[key]);
           }
       })
       .catch(error => console.error('Error fetching or applying:', error));


function collectInput() {
    
    const inputBudget = document.getElementById('BudgetCap'); 
    const inputEmissions = document.getElementById('ExpectedEmissions');
    // document.getElementById('output').textContent = "Testing" + inputBudget;
    if(inputBudget === "" || inputBudget === null)
    {
         document.getElementById('output').textContent = "Testing";
    }

    const myBox = document.getElementById('myBox');
    myBox.classList.remove('hidden-box');

// if (budgetElement === null || emissionsElement === null) {
//     document.getElementById('output').textContent = "Something not correct...";
//     console.error("Input element missing.");
// }
// else {
   
//     const inputBudget = budgetElement.value;
//     const inputEmissions = emissionsElement.value;


//     if (inputBudget === "" || inputEmissions === "") { 
//          document.getElementById('output').textContent = "Please enter values in both fields.";
//          return; 
//     }

//     const myBox = document.getElementById('myBox');
//     myBox.classList.remove('hidden-box');
// }

}
