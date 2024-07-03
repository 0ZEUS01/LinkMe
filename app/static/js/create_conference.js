let formCreateConference = document.getElementById("formCreateConference");

formCreateConference.addEventListener("submit", async (e) => {
    e.preventDefault();
    let title = document.getElementById("title").value;
    let address = document.getElementById("Address").value;

    let start_in = document.getElementById("start_in").value;
    let ends_in = document.getElementById("ends_in").value;

    let MinPNb = document.getElementById("MinPNb").value;
    let MaxPNb = document.getElementById("MaxPNb").value;
    let MinPNbN = parseInt(document.getElementById("MinPNb").value);
    let MaxPNbN =parseInt(document.getElementById("MaxPNb").value);
    let country_id = document.getElementById("country").value;

    // Check if any input is empty
    if (
        title.trim() === "" ||
        address.trim() === "" ||
        start_in.trim() === "" ||
        ends_in.trim() === "" ||
        MinPNb.trim() === "" ||
        MaxPNb.trim() === "" ||
        country_id.trim() === ""
    ) {
        alert("Please fill in all fields");
        return false; // Prevent form submission
    }

    if (start_in > ends_in) {
        alert("The starting date must be before the ending date of the conference");
        return false; // Prevent form submission
    }
    if (MinPNbN > MaxPNbN) {
        alert("The minimum participant number must be smaller than maximum participant number");
        return false; // Prevent form submission
    }
    let organizerId = localStorage.getItem("user_id");
    // Create an object with the request body
    const requestBody = {
        title: title,
        address: address,
        start_date: start_in,
        end_date: ends_in,
        min_participants: parseInt(MinPNb),
        max_participants: parseInt(MaxPNb),
        country: parseInt(country_id),
        state: parseInt(3), 
        organizer_id: parseInt(organizerId),
    };

    fetch("http://127.0.0.1:8000/create_conference", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
    })
        .then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error(response.status);
            }
        })
        .then((responseData) => {
            console.log(responseData); // Log the response data for debugging
            // Redirect to login page
            window.location.href = "../admin/conferences_management.html";
        })
        .catch((error) => {
            console.error("Conference creation request failed:", error);
        });

})