const selectElement = document.getElementById('country');

const fetchCountries = async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/country");
        if (response.ok) {
            const data = await response.json();
            updateOptions(data.country, );
        } else {
            console.error('Failed to fetch countries:', response.status);
        }
    } catch (error) {
        console.error('An error occurred:', error);
    }
};

const updateOptions = (countries) => {
    selectElement.innerHTML = ''; // Clear existing options

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select Your Country';
    selectElement.appendChild(defaultOption);

    if (Array.isArray(countries)) {
        countries.forEach((country) => {
            const option = document.createElement('option');
            option.value = country.country_id;
            option.textContent = country.country_name;
            selectElement.appendChild(option);
        });
    } else {
        const loadingOption = document.createElement('option');
        loadingOption.textContent = 'Loading countries...';
        selectElement.appendChild(loadingOption);
    }
};

fetchCountries();