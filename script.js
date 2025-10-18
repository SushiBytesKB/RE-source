 fetch('colors.json')
      .then(response => response.json())
      .then(colors => {
        // Set CSS variables on the root element
        for (const key in colors) {
          document.documentElement.style.setProperty(`--${key}`, colors[key]);
        }
      })
      .catch(error => console.error('Error fetching colors:', error));