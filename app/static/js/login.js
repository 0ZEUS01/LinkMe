let loginForm = document.getElementById("formLogin");

loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let usernameOrEmail = document.getElementById("usernameOrEmail").value;
    let user_password = document.getElementById("password").value;

    // Check if any input is empty
    if (usernameOrEmail.trim() === "" || user_password.trim() === "") {
        alert("Please fill in all fields");
        return false; // Prevent form submission
    }

    // Create an object with the request body
    const requestBody = {
        usernameOrEmail: usernameOrEmail,
        password: user_password,
    };

    fetch("http://127.0.0.1:8000/login", {
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
                throw new Error("Invalid email, username, or password");
            }
        })
        .then((responseData) => {
            localStorage.setItem("access_token", responseData.access_token);
            localStorage.setItem("birthdate", responseData.birthdate);
            localStorage.setItem("username", responseData.username);
            localStorage.setItem("email", responseData.email);
            localStorage.setItem("first_name", responseData.first_name);
            localStorage.setItem("last_name", responseData.last_name);
            localStorage.setItem("nationality", responseData.nationality);
            localStorage.setItem("Role", responseData.Role);
            localStorage.setItem("token_type", responseData.token_type);
            localStorage.setItem("user_id", responseData.user_id);
            localStorage.setItem("Address", responseData.Address);
            localStorage.setItem("phone_number", responseData.phone_number);
            localStorage.setItem("picture", responseData.picture);
            localStorage.setItem("isAdmin", responseData.isAdmin);

            setTimeout(() => {
                const roles = responseData.Role;
                if (roles.includes("ParticipantAndSearcherAndOrganizerAndProtractor")) {
                    window.location.href = "../choices/All.html";
                } else if (roles.includes("ParticipantAndSearcherAndProtractor")) {
                    window.location.href = "../choices/Participant_Searcher_Protractor.html";
                } else if (roles.includes("ParticipantAndSearcherAndOrganizer")) {
                    window.location.href = "../choices/Participant_Searcher_Organizer.html";
                } else if (roles.includes("ParticipantAndOrganizerAndProtractor")) {
                    window.location.href = "../choices/Participant_Protractor_Organizer.html";
                } else if (roles.includes("AndSearcherAndOrganizerAndProtractor")) {
                    window.location.href = "../choices/Searcher_Protractor_Organizer.html";
                } else if (roles.includes("ParticipantAndSearcher")) {
                    window.location.href = "../choices/Participant_Searcher.html";
                } else if (roles.includes("ParticipantAndProtractor")) {
                    window.location.href = "../choices/Participant_Protractor.html";
                } else if (roles.includes("ParticipantAndOrganizer") && roles.includes("Organizer")) {
                    window.location.href = "../choices/Participant_Organizer.html";
                } else if (roles.includes("AndSearcherAndOrganizer") && roles.includes("Organizer")) {
                    window.location.href = "../landing/Searcher_Organizer.html";
                } else if (roles.includes("AndSearcherAndProtractor")) {
                    window.location.href = "../landing/Searcher_Protractor.html";
                } else if (roles.includes("AndOrganizerAndProtractor")) {
                    window.location.href = "../landing/Organizer_Protractor.html";
                } else if (roles.includes("AndProtractor")) {
                    window.location.href = "../landing/index_protractor.html";
                } else if (roles.includes("Participant")) {
                    window.location.href = "../landing/index_participant.html";
                } else if (roles.includes("AndSearcher")) {
                    window.location.href = "../landing/index_searcher.html";
                } else if (roles.includes("AndOrganizer")) {
                    window.location.href = "../landing/index_organizer.html";
                } else {
                    window.location.href = "../landing/index_guest.html";
                }

            }, 100);
        })
        .catch((error) => {
            console.log("Error:", error);
            alert(error.message);
        });
});