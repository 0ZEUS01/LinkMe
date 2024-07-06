function getFormattedDate(dateString) {
    const date = new Date(dateString);
    const month = date.toLocaleString('default', { month: 'short' });
    const day = date.getDate();
    return `${month} <span>${day}</span>`;
}

// Extract conference ID from URL query parameter
const urlParams = new URLSearchParams(window.location.search);
const conferenceId = urlParams.get('conferenceId');

function getConferenceIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
}
// Fetch conference details based on conferenceId
fetch(`http://127.0.0.1:8000/get_ConferenceDetails?conferenceId=${conferenceId}`)
    .then(response => response.json())
    .then(data => {
        const conference = data.conference;

        // Populate conference details on the page
        document.getElementById('conferenceDate').innerHTML = getFormattedDate(conference.start_date);
        document.getElementById('conferenceImage').src = conference.image_url;
        document.getElementById('conferenceTitle').innerHTML = conference.title;
        document.getElementById('conferenceLocation').innerHTML = `Location: ${conference.country_name}`;
        document.getElementById('conferenceDescription').innerHTML = conference.description;
        document.getElementById('conferenceSchedule').innerHTML = `Monday - Friday<br>${conference.start_date} - ${conference.end_date}`;
        document.getElementById('conferenceLocationDetails').innerHTML = conference.location;
    })
    .catch(error => {
        console.error('Error:', error);
    });