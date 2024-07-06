const articleContainer = document.getElementById('ShowArticles');
const articlesSection = document.getElementById('Articles');
const articleDetailsSection = document.getElementById('Articledetails');

function getFormattedDate(dateString) {
    const date = new Date(dateString);
    const month = date.toLocaleString('default', { month: 'short' });
    const day = date.getDate();
    return `${month} <span>${day}</span>`;
}

function fetchArticles() {
    fetch('http://127.0.0.1:8000/show_Articles')
        .then(response => response.json())
        .then(data => {
            const articles = data.article;

            articles.forEach(article => {
                const articleDiv = document.createElement('div');
                articleDiv.className = 'col-lg-4 templatemo-item-col all soon';
                articleDiv.innerHTML = `
          <div class="meeting-item">
            <div class="thumb">
              <a href="#" class="article-link">
                <img src="assets/images/noo.jpg" alt="">
              </a>
            </div>
            <div class="down-content">
              <div class="date">
                <h6>${getFormattedDate(article.start_date)}</h6>
              </div>
              <a href="#" class="article-link">
                <h4>${article.article_title}</h4>
              </a>
              <p><b>This article is related to:</b> ${article.conference_title}</p>
              <p><b>It will be in:</b> ${article.country_name}</p>
              <p><b>Author:</b> ${article.first_name} ${article.last_name}</p>
            </div>
          </div>
        `;

                articleContainer.appendChild(articleDiv);
            });

            // Add click event listener to each article link
            const articleLinks = document.querySelectorAll('.article-link');
            articleLinks.forEach((articleLink, index) => {
                articleLink.addEventListener('click', (event) => {
                    event.preventDefault();

                    // Get the selected article details
                    const selectedArticle = articles[index];

                    // Update the content of the article details section
                    document.querySelector('#conferenceDate').innerHTML = getFormattedDate(selectedArticle.start_date);
                    document.querySelector('#ArticleImage').src = 'assets/images/noo.jpg'; // Replace with the appropriate property from the API response
                    document.querySelector('#Title').innerHTML = selectedArticle.article_title;
                    document.querySelector('#conferenceLocation').innerHTML = `This article is related to the conference: ${selectedArticle.conference_title}`;
                    document.querySelector('#conferenceLocationDetails').innerHTML = selectedArticle.address;
                    const conferenceDescriptionElement = document.querySelector('#conferenceDescription');

                    // Decode the Base64 content to bytes
                    const decodedContent = atob(selectedArticle.article_content);
                    const contentBytes = new Uint8Array(decodedContent.length);
                    for (let i = 0; i < decodedContent.length; i++) {
                        contentBytes[i] = decodedContent.charCodeAt(i);
                    }

                    // Create a Blob from the bytes
                    const blob = new Blob([contentBytes], { type: 'application/pdf' });

                    // Generate a download URL for the Blob
                    const downloadUrl = URL.createObjectURL(blob);

                    // Set the download link attributes
                    const downloadLink = document.createElement('a');
                    downloadLink.href = downloadUrl;
                    downloadLink.download = selectedArticle.article_title + '.pdf';

                    // Append the download link to the conference description element
                    downloadLink.innerHTML = 'Download Article';
                    conferenceDescriptionElement.innerHTML = '';
                    conferenceDescriptionElement.appendChild(downloadLink);

                    // Hide the articles section and show the article details section
                    articlesSection.style.display = 'none';
                    articleDetailsSection.style.display = 'block';
                });
            });
        })
        .catch(error => {
            console.error('Error fetching articles:', error);
        });
}

fetchArticles();

// Add click event listener to the "Back To Home" link in the article details section
const backToHomeLink = document.querySelector('#Articledetails .main-button-red a');
backToHomeLink.addEventListener('click', (event) => {
    event.preventDefault();

    // Show the articles section and hide the article details section
    articlesSection.style.display = 'block';
    articleDetailsSection.style.display = 'none';
});
