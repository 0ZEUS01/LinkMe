// Fetch conferences from the endpoint
fetch('http://127.0.0.1:8000/get_Scheduledconferences')
    .then(response => response.json())
    .then(data => {
        const conferences = data.conference;

        // Function to format the date as "MMM DD"
        function getFormattedDate(dateString) {
            const date = new Date(dateString);
            const month = date.toLocaleString('default', { month: 'short' });
            const day = date.getDate();
            return `${month} <span>${day}</span>`;
        }
        function getMonth(dateString) {
            const date = new Date(dateString);
            const month = date.toLocaleString('default', { month: 'long' });
            return `${month}`;
        }
        function getDay(dateString) {
            const date = new Date(dateString);
            const day = date.getDate();
            return `${day}`;
        }
        function getYear(dateString) {
            const date = new Date(dateString);
            const year = date.getFullYear();
            return `${year}`;
        }
        // Create div elements for each conference
        conferences.forEach(conference => {
            const conferenceDiv = document.createElement('div');
            conferenceDiv.className = 'col-lg-4 templatemo-item-col all soon';
            conferenceDiv.innerHTML = `
        <div class="meeting-item">
            <div class="thumb">
            <a href="#" id="linkToShowConfModal1" data-bs-toggle="modal" data-bs-target="#showConf">
            <img src="assets/images/meeting-01.jpg" alt="">
            </a>
            </div>
            <div class="down-content">
            <div class="date">
                <h6>${getFormattedDate(conference.start_date)}</h6>
            </div>
            <a href="#" id="linkToShowConfModal2" data-bs-toggle="modal" data-bs-target="#showConf">
                <h4>${conference.title}</h4>
            </a>
            <p>This conference will be organized in ${conference.country_name}</p>
            </div>
        </div>
        `;

            // Add event listener to each conference div
            // Add event listener to each conference div
                conferenceDiv.addEventListener('click', () => {
                    // Hide the meetings section
                    const meetingsSection = document.querySelector('#meetings');
                    meetingsSection.style.display = 'none';

                    // Show the meetingsdetails section
                    const meetingsDetailsSection = document.querySelector('#meetingsdetails');
                    meetingsDetailsSection.style.display = 'block';

                    // Update the content of the meetingsdetails section with conference information
                    document.querySelector('#conferenceDate').innerHTML = getFormattedDate(conference.start_date);
                    // document.querySelector('#conferenceImage').src = conference.image_url; // Replace with the appropriate property from the API response
                    document.querySelector('#conferenceTitle').innerHTML = conference.title;
                    document.querySelector('#conferenceLocation').innerHTML = `This conference will be organized in ${conference.country_name}`;
                    document.querySelector('#conferenceDescription').innerHTML = `${conference.title} conference will start in ${getDay(conference.start_date)} ${getMonth(conference.start_date)} ${getYear(conference.start_date)} and ends in ${getDay(conference.end_date)} ${getMonth(conference.end_date)} ${getYear(conference.end_date)} the minimum expected participants to participate is ${conference.min_participants} and the maximum expected is ${conference.max_participants}`
                    document.querySelector('#conferenceLocationDetails').innerHTML = `${conference.Address}, ${conference.country_name}`; // Replace with the appropriate property from the API response

                    // Store conference details in local storage
                    localStorage.setItem('selectedConference', JSON.stringify(conference));
                });


                // Append the conference div to the parent container
                const parentDiv = document.querySelector('#ShowConferenses');
                parentDiv.appendChild(conferenceDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
