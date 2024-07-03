document.addEventListener('DOMContentLoaded', () => {
    const selectElement = document.getElementById('state');

    const fetchStates = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/state");
            if (response.ok) {
                const data = await response.json();
                updateOptions(data.state);
            } else {
                console.error('Failed to fetch states:', response.status);
            }
        } catch (error) {
            console.error('An error occurred:', error);
        }
    };

    const updateOptions = (states) => {
        selectElement.innerHTML = ''; // Clear existing options

        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select Your state';
        selectElement.appendChild(defaultOption);

        if (states && states.length > 0) {
            states.forEach((state) => {
                const option = document.createElement('option');
                option.value = state.state_conference_id;
                option.textContent = state.state_conference_name;

                selectElement.appendChild(option);
            });
        } else {
            const noStatesOption = document.createElement('option');
            noStatesOption.textContent = 'No states found';
            selectElement.appendChild(noStatesOption);
        }
    };

    fetchStates();
});
