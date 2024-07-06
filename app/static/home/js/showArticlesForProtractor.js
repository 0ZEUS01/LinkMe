document.addEventListener('DOMContentLoaded', function () {
  let selectedArticleId = null;

  const articleContainer = document.getElementById('ShowArticles');
  const articlesSection = document.getElementById('Articles');
  const articledetailsSection = document.getElementById('Articledetails');

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
                <a href="#" class="article-link" data-article-id="${article.article_id}">
                  <img src="assets/images/noo.jpg" alt="">
                </a>
              </div>
              <div class="down-content">
                <div class="date">
                  <h6>${getFormattedDate(article.start_date)}</h6>
                </div>
                <a href="#" class="article-link" data-article-id="${article.article_id}">
                  <h4>${article.article_title}</h4>
                </a>
                <p><b>This article is related to:</b> ${article.conference_title}</p>
                <p><b>It will be in:</b> ${article.country_name}</p>
                <p><b>Author:</b> ${article.first_name} ${article.last_name}</p>
              </div>
            </div>
          `;

          articleDiv.addEventListener('click', () => {
            selectedArticleId = article.article_id; // Store the selected article ID
            fetchArticleDetails(selectedArticleId);
            articlesSection.style.display = 'none';
            articledetailsSection.style.display = 'block';
          });

          articleContainer.appendChild(articleDiv);
        });
      });
  }

  function fetchArticleDetails(articleId) {
    fetch('http://127.0.0.1:8000/show_Articles')
      .then(response => response.json())
      .then(data => {
        const articles = data.article;
        const articleDetails = articles.find(article => article.article_id === articleId);
        console.log(articleDetails)
        document.querySelector('#conferenceDate').innerHTML = getFormattedDate(articleDetails.start_date);

        const titleElement = articledetailsSection.querySelector('#Title');
        titleElement.textContent = articleDetails.article_title;

        document.querySelector('#conferenceTitle').innerHTML = "This article is related to the conference: " + articleDetails.conference_title;

        let conferenceDescriptionElement = document.querySelector('#conferenceDescription');
        const decodedContent = atob(articleDetails.article_content);
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
        downloadLink.download = articleDetails.article_title + '.pdf';

        // Append the download link to the conference description element
        downloadLink.innerHTML = 'Download Article';
        conferenceDescriptionElement.innerHTML = '';
        conferenceDescriptionElement.appendChild(downloadLink);

        const conferenceLocationDetailsElement = articledetailsSection.querySelector('#conferenceLocationDetails');
        conferenceLocationDetailsElement.innerHTML = articleDetails.address + ", " + articleDetails.country_name;
      });
  }

  fetchArticles();

  const postReportLink = document.getElementById('postReportLink');
  postReportLink.addEventListener('click', function (event) {
    event.preventDefault();
    localStorage.setItem('selectedArticleId', selectedArticleId);
    window.location.href = '../admin/create_report.html';
  });
});
