let formeditconference = document.getElementById("formEditArticle");

formeditconference.addEventListener("submit", async (e) => {
    e.preventDefault();
    let articleTitle = document.getElementById("article_title").value;
    let uploadInput = document.getElementById("upload");

    // Check if any input is empty
    if (articleTitle.trim() === "") {
        alert("Please fill in all fields");
        return false;
    }

    // Retrieve the article ID from local storage
    var articleId = localStorage.getItem('articleId');

    // Create a FormData object to send the form data
    var formData = new FormData();
    formData.append('article_id', parseInt(articleId));
    formData.append('article_title', articleTitle);

    // Check if a new file was uploaded by the user
    if (uploadInput.files[0]) {
        // Read the file content and convert it to Base64
        var reader = new FileReader();
        reader.onload = async function (e) {
            var base64Content = e.target.result.split(",")[1]; // Extract the Base64 content
            formData.append('article_content', base64Content);

            try {
                const response = await fetch("http://127.0.0.1:8000/update_submissions1", {
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
                window.alert("Article updated successfully");
                // Refresh the page or update the relevant UI elements
                location.reload();
            } catch (error) {
                console.error("Article update request failed:", error.message);
            }

        };
        reader.readAsDataURL(uploadInput.files[0]);
    } else {
        try {
            const response = await fetch("http://127.0.0.1:8000/update_submissions2", {
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
            window.alert("Article updated successfully");
            // Refresh the page or update the relevant UI elements
            location.reload();
        } catch (error) {
            console.error("Article update request failed:", error);
        }
    }
});
