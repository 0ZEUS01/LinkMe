let formeditconference = document.getElementById("formEditReport");

formeditconference.addEventListener("submit", async (e) => {
    e.preventDefault();
    let uploadInput = document.getElementById("upload");

    // Retrieve the article ID from local storage
    var reportId = localStorage.getItem('edit_report_id');

    // Create a FormData object to send the form data
    var formData = new FormData();
    formData.append('report_id', parseInt(reportId));

    // Read the file content and convert it to Base64
    var reader = new FileReader();
    reader.onload = async function (e) {
        var base64Content = e.target.result.split(",")[1]; // Extract the Base64 content
        formData.append('report_content', base64Content);

        try {
            const response = await fetch("http://127.0.0.1:8000/edit_report", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(Object.fromEntries(formData)),
            });

            if (!response.ok) {
                const responseData = await response.json();
                throw new Error(responseData.detail[0].msg); // Throw an error with the specific error message from the server
            }

            const responseData = await response.json();
            console.log(responseData); // Log the response data for debugging
            // Show success alert
            window.alert("Report updated successfully");
            // Refresh the page or update the relevant UI elements
            location.reload();
        } catch (error) {
            console.error("Report update request failed:", error.message);
        }

    };
    reader.readAsDataURL(uploadInput.files[0]);
});
