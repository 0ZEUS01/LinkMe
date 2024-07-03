let changeName = document.getElementById("changeName");
let uploadInput = document.getElementById("upload");
let ArticleInConference = document.getElementById("modalCenterTitle");

$(document).ready(function () {
    $.ajax({
        url: "http://127.0.0.1:8000/get_Articles/" + localStorage.getItem('user_id'),
        type: "GET",
        success: function (response) {
            // Handle the successful response

            // Get the table body element
            var table = $("#Article_table tbody");

            // Add new data to the table
            var articles = response.article;

            // Function to display articles based on the filtered list
            function displayArticles(articles) {
                table.empty(); // Clear the table

                for (var i = 0; i < articles.length; i++) {
                    var art = articles[i];
                    var row = $("<tr>");

                    row.append($("<td class='conference-title'>").text(art.title));
                    row.append($("<td>").text(art.article_title));

                    // Create a link for the article title that triggers the download
                    var articleTitleLink = $("<a>")
                        .text(art.article_title)
                        .attr("href", "data:application/octet-stream;base64," + art.article_content)
                        .attr("download", art.article_title + getFileExtension(art.article_content));

                    // Append the article title link to the table cell
                    row.append($("<td>").append(articleTitleLink));

                    var stateCell = $("<td>");
                    if (art.decision === 'UNREVIEWED') {
                        var badge = $("<span class='badge bg-label-info me-1'>").text(art.decision);
                        stateCell.append(badge);
                    } else if (art.decision === 'APPROVED') {
                        var badge = $("<span class='badge bg-label-success me-1'>").text(art.decision);
                        stateCell.append(badge);
                    } else if (art.decision === 'REFUSED') {
                        var badge = $("<span class='badge bg-label-danger me-1'>").text(art.decision);
                        stateCell.append(badge);
                    } else {
                        var badge = $("<span class='badge bg-label-secondary me-1'>").text("Sent");
                        stateCell.append(badge);
                    }
                    row.append(stateCell);

                    var editLink = $('<a class="dropdown-item edit-link" data-bs-toggle="modal" data-bs-target="#editart"><i class="bx bx-edit-alt me-1"></i> Edit</a>');
                    editLink.data('article', art); // Store the article data in the link's data attribute

                    var deleteLink = $('<a class="dropdown-item delete-link" href="#"><i class="bx bx-trash me-1"></i> Delete</a>');
                    deleteLink.data('articleId', art.article_id); // Store the article ID in the link's data attribute

                    var dropdownCell = $('<td><div class="dropdown"><button type="button" class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="bx bx-dots-vertical-rounded"></i></button><div class="dropdown-menu"></div></div></td>');
                    dropdownCell.find('.dropdown-menu').append(editLink, deleteLink);

                    row.append(dropdownCell);
                    table.append(row);
                }
            }
            function getFileExtension(base64Data) {
                // Default file extension
                var defaultExtension = ".pdf";

                // Check if the base64 data is defined and non-empty
                if (base64Data && base64Data.trim().length > 0) {
                    try {
                        return defaultExtension;
                    } catch (error) {
                        console.error("Error while extracting file extension:", error);
                    }
                }

                return defaultExtension;
            }
            // Event delegation for the delete link
            $(document).on('click', '.delete-link', function (e) {
                var articleId = $(this).data('articleId');
                if (confirm("Are you sure you want to delete this Article?")) {
                    // Perform the delete operation
                    deleteArticle(articleId);
                }
            });

            function deleteArticle(articleId) {
                // Send the delete request to the API
                $.ajax({
                    url: "http://127.0.0.1:8000/delete_submissions/" + articleId,
                    type: "DELETE",
                    success: function (response) {
                        // Handle the successful response
                        alert("Article deleted successfully");
                        // Refresh the page
                        location.reload();
                    },
                    error: function (xhr, status, error) {
                        // Handle the error response
                        console.error("Article deletion request failed:", error);
                    },
                });
            }

            $(document).on('click', '.edit-link', function (e) {
                var articleData = $(this).data('article');
                var conferenceTitle = $(this).closest('tr').find('.conference-title').text();

                // Set the conference title in the header
                ArticleInConference.textContent = "This article is for "+conferenceTitle+ " conference";

                // Set the article title in the input field
                $('#article_title').val(articleData.article_title);

                // Store the article ID in a variable
                var articleId = articleData.article_id;
                // Attach the article ID to the form element for later use
                $('#formCreateArticle').data('articleId', articleId);
                localStorage.setItem('articleId', articleData.article_id);
                // Reset the upload input and changeName label
                uploadInput.value = "";
                changeName.textContent = "Upload your Article";
            });
            // Event handler for the search bar input
            $('#searchBar').on('input', function () {
                var searchQuery = $(this).val().toLowerCase();
                var filteredArticles = filterArticles(searchQuery);
                displayArticles(filteredArticles);
            });

            // Function to filter articles based on the search query
            function filterArticles(searchQuery) {
                return articles.filter(function (article) {
                    var title = article.article_title.toLowerCase();
                    return title.includes(searchQuery);
                });
            }

            displayArticles(articles); // Call the function to display articles
        },
        error: function (error) {
            // Handle the error
            console.error("Error:", error);
        }
    });
});

uploadInput.addEventListener("change", function () {
    var fileName = this.files[0] ? this.files[0].name : "No file selected";
    changeName.textContent = fileName;
});
