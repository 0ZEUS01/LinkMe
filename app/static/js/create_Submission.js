let formCreateArticle = document.getElementById("formCreateArticle");
let uploadInput = document.getElementById("upload");
let changeName = document.getElementById("changeName");
const selectedConference = JSON.parse(localStorage.getItem("selectedConference"));
document.querySelector("#title").innerHTML = selectedConference.title;

formCreateArticle.addEventListener("submit", async (e) => {
    e.preventDefault();
    let articleTitle = document.getElementById("article_title").value;
    let articleContent = uploadInput.files[0];

    // Check if any input is empty
    if (articleTitle.trim() === "" || !articleContent) {
        alert("Please enter an article title and upload an article file.");
        return false; // Prevent form submission
    }

    // Retrieve the user ID and conference ID from local storage
    let userId = localStorage.getItem("user_id");
    let conferenceId = selectedConference.conference_id;

    let reader = new FileReader();
    reader.onloadend = async function () {
        let base64Content = reader.result.split(",")[1]; // Extract the base64 content

        // Create the request body
        const requestBody = {
            article_title: articleTitle,
            article_content: base64Content,
            searcher_id: parseInt(userId), // Convert to integer
            submission_date: "string", // Placeholder value
            conference_id: parseInt(conferenceId), // Convert to integer
            article_id: 0, // Placeholder value
            report_id: 0, // Placeholder value
        };

        try {
            let response = await fetch(`http://127.0.0.1:8000/create_submissions/${userId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(requestBody),
            });

            if (response.ok) {
                let data = await response.json();
                console.log(data);
                alert("The article has been posted.");
                window.location.href = "../admin/searcher_articles.html";
            } else {
                throw new Error(response.status);
            }
        } catch (error) {
            console.error("Article and submission creation request failed:", error);
        }
    };

    reader.readAsDataURL(articleContent); // Read the file as data URL
});

uploadInput.addEventListener("change", function () {
    var fileName = this.files[0] ? this.files[0].name : "No file selected";
    changeName.textContent = fileName;
});
