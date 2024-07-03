$(document).ready(function () {
    // Retrieve user_id from local storage
    var user_id = localStorage.getItem("user_id");

    // Retrieve reports data from the API
    $.ajax({
        url: "http://127.0.0.1:8000/show_Reports/" + user_id,
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
                                var badge = $("<span class='badge bg-label-secondary me-1'>").text("Sent");
                                stateCell.append(badge);
                            }
                            row.append(stateCell);

                            // Edit dropdown button
                            var editLink = $('<a class="dropdown-item edit-link" data-bs-toggle="modal" data-bs-target="#editRep"><i class="bx bx-edit-alt me-1"></i> Edit</a>');
                            editLink.data('report_id', report.report_id); // Store the report ID in the link's data attribute
                            editLink.on("click", function () {
                                var reportId = $(this).data('report_id');
                                localStorage.setItem("edit_report_id", reportId);
                            });

                            var deleteLink = $('<a class="dropdown-item delete-link" href="javascript:void(0)"><i class="bx bx-trash me-1"></i> Delete</a>');
                            deleteLink.data('report_id', report.report_id); // Store the report ID in the link's data attribute

                            var dropdownCell = $('<td><div class="dropdown"><button type="button" class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="bx bx-dots-vertical-rounded"></i></button><div class="dropdown-menu"></div></div></td>');
                            dropdownCell.find('.dropdown-menu').append(editLink, deleteLink);

                            row.append(dropdownCell);
                            table.append(row);
                        }
                    } else {
                        // Display a message or take appropriate action when no reports are available
                        table.append($("<tr>").append($("<td colspan='5'>").text("No reports available.")));
                    }
                }

                displayReports(filteredReports);

                $(document).on('click', '.delete-link', function (e) {
                    var reportId = parseInt($(this).data('report_id'));
                    if (confirm("Are you sure you want to delete this Report?")) {
                        // Perform the delete operation
                        deleteReport(reportId);
                    }
                });

                function deleteReport(reportId) {
                    // Send the delete request to the API
                    $.ajax({
                        url: "http://127.0.0.1:8000/delete_report/" + reportId,
                        type: "DELETE",
                        success: function (response) {
                            // Handle the successful response
                            alert("Report deleted successfully");
                            // Refresh the page
                            location.reload();
                        },
                        error: function (xhr, status, error) {
                            // Handle the error response
                            console.error("Report deletion request failed:", error);
                        },
                    });
                }
            }
        },
    });
});
