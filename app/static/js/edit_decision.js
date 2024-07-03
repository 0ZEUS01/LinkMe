document.addEventListener("DOMContentLoaded", () => {
    let formeditdecision = document.getElementById("formeditdecision");

    formeditdecision.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Check if any input is empty
        let articleId = localStorage.getItem("article_id");
        let decision_id = document.getElementById("decision").value;
        // Retrieve the organizer ID from local storage
        let organizer_id = localStorage.getItem("user_id");
        
        // Create an object with the request body
        const requestBody = {
            decision_id: parseInt(decision_id),
            organizer_id: parseInt(organizer_id),
        };

        try {
            const response = await fetch(`http://127.0.0.1:8000/edit_Article_decision/${articleId}`, {
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
                window.alert("Decision modified successfully");

                // Reload the page
                window.location.reload();
            } else {
                throw new Error(response.status);
            }
        } catch (error) {
            console.error("Decision modification request failed:", error);
        }
    });
});
