document.addEventListener('DOMContentLoaded', function () {
    const selectedArticleId = parseInt(localStorage.getItem('selectedArticleId'));
    let uploadInput = document.getElementById("upload");
    let changeName = document.getElementById("changeName");
    let formCreateReport = document.getElementById("formCreateReport");

    if (selectedArticleId) {
        fetchArticleDetails(selectedArticleId);
    } else {
        console.log('No selectedArticleId found in local storage');
    }

    function fetchArticleDetails(selectedArticleId) {
        fetch('http://127.0.0.1:8000/show_Articles')
            .then(response => response.json())
            .then(data => {
                console.log('Fetched articles:', data.article);

                const articles = data.article;
                const articleDetails = articles.find(article => article.article_id === selectedArticleId);
                console.log('articleDetails:', articleDetails);

                if (articleDetails) {
                    document.querySelector('#articletitle').innerHTML = articleDetails.article_title;

                    const titleElement = document.querySelector('#relatedTo');
                    titleElement.textContent = articleDetails.conference_title;

                    document.querySelector('#article').innerHTML = "for " + articleDetails.article_title;
                } else {
                    console.log('No matching article found for selectedArticleId:', selectedArticleId);
                }
            })
            .catch(error => {
                console.error('Error fetching article details:', error);
            });
    }

    formCreateReport.addEventListener("submit", async (e) => {
        e.preventDefault(); // Prevent the form from submitting in the default way
        let userId = localStorage.getItem("user_id");

        const reportContent = uploadInput.files[0];

        const reader = new FileReader();
        reader.onloadend = async function () {
            const base64Content = reader.result.split(",")[1];

            const report = {
                report_id: 0,
                report_content: base64Content,
                article_id: selectedArticleId
            };

            try {
                const response = await fetch(`http://127.0.0.1:8000/create_report/${userId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(report),
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log(data);
                    alert("The report has been posted.");
                    window.location.href = "../admin/protractor_history.html";
                } else {
                    throw new Error(response.status);
                }
            } catch (error) {
                console.error("Report creation request failed:", error);
                alert("Failed to create the report. Please try again.");
            }
        };

        reader.readAsDataURL(reportContent); // Read the file as data URL
    });

    uploadInput.addEventListener("change", function () {
        var fileName = this.files[0] ? this.files[0].name : "No file selected";
        changeName.textContent = fileName;
    });
});
