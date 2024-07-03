$(document).ready(function () {

    // Retrieve reports data from the API
    $.ajax({
        url: "http://127.0.0.1:8000/show_Approved_Reports/",
        type: "GET",
        success: function (response) {
            // Handle the successful response

            // Get the table body element
            var table = $("#report_table tbody");

            // Check if the "report" key exists in the response
            if ("report" in response) {
                var reports = response.report;
                var filteredReports = reports; // Initialize filtered reports with all reports

                function base64ToBytes(base64String) {
                    var byteCharacters = atob(base64String);
                    var byteNumbers = new Array(byteCharacters.length);
                    for (var i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    return new Uint8Array(byteNumbers);
                }

                function getFileExtension(filename) {
                    return filename.split('.').pop();
                }

                function getMimeType(extension) {
                    switch (extension.toLowerCase()) {
                        case 'pdf':
                            return 'application/pdf';
                        case 'doc':
                        case 'docx':
                            return 'application/msword';
                        default:
                            return 'application/pdf';
                    }
                }

                function displayReports(reports) {
                    table.empty();
                    if (Array.isArray(reports) && reports.length > 0) {
                        for (var i = 0; i < reports.length; i++) {
                            var report = reports[i];
                            var row = $("<tr>");

                            row.append($("<td>").append($("<a>").attr("href", "#").text(report.protractor_first_name + " " + report.protractor_last_name).on("click", function () {
                                var fileExtension = getFileExtension(report.protractor_first_name + " " + report.protractor_last_name);
                                var mimeType = getMimeType(fileExtension);

                                var byteArray = base64ToBytes(report.report_content);
                                var blob = new Blob([byteArray], { type: mimeType });
                                var url = URL.createObjectURL(blob);

                                var link = document.createElement("a");
                                link.href = url;
                                link.download = "reportBy_" + report.protractor_first_name + "_" + report.protractor_last_name + "." + "pdf"; // Use a shorter identifier for the downloaded file
                                link.click();
                            })));

                            row.append($("<td>").append($("<a>").attr("href", "#").text(report.article_title).on("click", function () {
                                var fileExtension = getFileExtension(report.article_title);
                                var mimeType = getMimeType(fileExtension);

                                var byteArray = base64ToBytes(report.article_content);
                                var blob = new Blob([byteArray], { type: mimeType });
                                var url = URL.createObjectURL(blob);

                                var link = document.createElement("a");
                                link.href = url;
                                link.download = "article_" + report.article_title + "." + "pdf"; // Use a shorter identifier for the downloaded file
                                link.click();
                            })));

                            row.append($("<td>").text(report.conference_title));

                            var stateCell = $("<td>");

                            if (report.decision === 'UNREVIEWED') {
                                var badge = $("<span class='badge bg-label-warning me-1'>").text(report.decision);
                                stateCell.append(badge);
                            } else if (report.decision === 'APPROVED') {
                                var badge = $("<span class='badge bg-label-success me-1'>").text(report.decision);
                                stateCell.append(badge);
                            } else if (report.decision === 'REFUSED') {
                                var badge = $("<span class='badge bg-label-danger me-1'>").text(report.decision);
                                stateCell.append(badge);
                            } else {
                                var badge = $("<span class='badge bg-label-secondary me-1'>").text("Not reviewed yet");
                                stateCell.append(badge);
                            }
                            row.append(stateCell);

                            // Edit dropdown button
                            var decisionLink = $('<a class="dropdown-item edit-link" id="decision_Link" data-bs-toggle="modal" data-bs-target="#editDec"><i class="bx bx-edit-alt me-1"></i> Give the decision</a>');
                            decisionLink.data('report_id', report.report_id); // Store the report ID in the link's data attribute
                            decisionLink.data('article_id', report.article_id); // Store the article ID in the link's data attribute
                            decisionLink.on("click", function () {
                                var reportId = $(this).data('report_id');
                                var articleId = $(this).data('article_id');
                                console.log("Article ID:", articleId);

                                localStorage.setItem("edit_report_id", reportId);
                                localStorage.setItem("article_id", articleId);
                                console.log("Article ID:", articleId);
                            });


                            var dropdownCell = $('<td><div class="dropdown"><button type="button" class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="bx bx-dots-vertical-rounded"></i></button><div class="dropdown-menu"></div></div></td>');
                            dropdownCell.find('.dropdown-menu').append(decisionLink);

                            row.append(dropdownCell);
                            table.append(row);
                        }
                    } else {
                        // Display a message or take appropriate action when no reports are available
                        table.append($("<tr>").append($("<td colspan='5'>").text("No reports available.")));
                    }
                }

                displayReports(filteredReports);

                $("#report_table").on("click", ".edit-link", function () {
                    var reportId = $(this).data('report_id');
                    var articleId = $(this).data('article_id');
                    console.log("Article ID:", articleId);

                    localStorage.setItem("edit_report_id", reportId);
                    localStorage.setItem("article_id", articleId);
                    console.log("Article ID:", articleId);
                });
            }
        },
    });
});

const selectElementDecision = document.getElementById('decision');

const fetchDecisions = async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/decision");
        if (response.ok) {
            const data = await response.json();
            updateOptionsDecision(data.decision);
        } else {
            console.error('Failed to fetch decisions:', response.status);
        }
    } catch (error) {
        console.error('An error occurred:', error);
    }
};
const updateOptionsDecision = (decisions) => {
    selectElementDecision.innerHTML = '';

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select Your decision';
    selectElementDecision.appendChild(defaultOption);

    if (decisions && decisions.length > 0) {
        decisions.forEach((decision) => {
            const option = document.createElement('option');
            option.value = decision.decision_id;
            option.textContent = decision.decision;
            selectElementDecision.appendChild(option);
        });
    } else {
        const noDecisionsOption = document.createElement('option');
        noDecisionsOption.textContent = 'No decision found';
        selectElementDecision.appendChild(noDecisionsOption);
    }
};

fetchDecisions(); 
