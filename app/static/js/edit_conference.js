let formeditconference = document.getElementById("formeditconference");

formeditconference.addEventListener("submit", async (e) => {
    e.preventDefault();
    let title = document.getElementById("title").value;
    let address = document.getElementById("Address").value;

    let start_in = document.getElementById("start_in").value;
    let ends_in = document.getElementById("ends_in").value;

    let MinPNb = document.getElementById("MinPNb").value;
    let MaxPNb = document.getElementById("MaxPNb").value;
    let country_id = document.getElementById("countryy").value;
    let state_conference_id = document.getElementById("statee").value;

    // Check if any input is empty
    if (
        title.trim() === "" ||
        address.trim() === "" ||
        start_in.trim() === "" ||
        ends_in.trim() === "" ||
        MinPNb.trim() === "" ||
        MaxPNb.trim() === "" ||
        country_id.trim() === "" ||
        state_conference_id.trim() === ""
    ) {
        alert("Please fill in all fields");
        return false;
    }

    if (start_in > ends_in) {
        alert("The starting date must be before the ending date of the conference");
        return false;
    }
    if (parseInt(MinPNb) > parseInt(MaxPNb)) {
        alert("The minimum participant number must be smaller than the maximum participant number");
        return false;
    }

    let organizerId = localStorage.getItem("user_id");
    let conferenceData = JSON.parse(localStorage.getItem("conferenceData"));
    let conferenceId = conferenceData.conference_id;

    // Create an object with the request body
    const requestBody = {
        title: title,
        address: address,
        start_date: start_in,
        end_date: ends_in,
        min_participants: parseInt(MinPNb),
        max_participants: parseInt(MaxPNb),
        country: parseInt(country_id),
        conference_id: parseInt(conferenceId),
        state_conference_id: parseInt(state_conference_id),
        organizer_id: parseInt(organizerId),
    };


    try {
        const response = await fetch("http://127.0.0.1:8000/edit_conference", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
        });
    
        if (response.ok) {
            const responseData = await response.json();
            console.log(responseData); // Log the response data for debugging
            // Show success alert
            window.alert("Conference modified successfully");
            // Redirect to login page
            window.location.href = "../admin/conferences_management.html";
        } else {
            throw new Error(response.status);
        }
    } catch (error) {
        console.error("Conference modification request failed:", error);
    }
    
}); 