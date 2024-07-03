let registerForm = document.getElementById("formRegister");

registerForm.addEventListener("submit", (e) => {
    e.preventDefault();

    let fileInput = document.getElementById("picture");
    let pictureFile = fileInput.files[0];

    if (!pictureFile) {
        // Set a default picture
        let defaultPictureUrl = "../admin/assets/img/avatars/default.png";
        fetch(defaultPictureUrl)
            .then((response) => response.blob())
            .then((blob) => handleFileReadCompletion(blob))
            .catch((error) => {
                console.error("Failed to load the default picture:", error);
            });
    } else {
        let reader = new FileReader();
        reader.onloadend = handleFileReadCompletion;
        reader.readAsArrayBuffer(pictureFile);
    }
});

function handleFileReadCompletion(event) {
    let pictureBytes;

    if (event instanceof Blob) {
        let reader = new FileReader();
        reader.onloadend = function () {
            pictureBytes = new Uint8Array(reader.result);
            handleFileRead(pictureBytes);
        };
        reader.readAsArrayBuffer(event);
    } else {
        let reader = event.target;
        if (reader.readyState === FileReader.DONE) {
            pictureBytes = new Uint8Array(reader.result);
            handleFileRead(pictureBytes);
        } else {
            console.error("Failed to read the picture file.");
        }
    }
}



function handleFileRead(pictureBytes) {
    let first_name = document.getElementById("FirstName").value;
    let last_name = document.getElementById("LastName").value;
    let PhoneNumber = document.getElementById("PhoneNumber").value;
    let Birthdate = document.getElementById("BirthDate").value;
    let username = document.getElementById("username").value;
    let user_email = document.getElementById("email").value;
    let user_password = document.getElementById("password").value;
    let user_c_password = document.getElementById("c_password").value;
    let user_country_id = document.getElementById("country").value;
    let user_Address = document.getElementById("Address").value;

    // Check if any input is empty
    if (
        first_name.trim() === "" ||
        last_name.trim() === "" ||
        PhoneNumber.trim() === "" ||
        Birthdate.trim() === "" ||
        username.trim() === "" ||
        user_email.trim() === "" ||
        user_password.trim() === "" ||
        user_country_id.trim() === "" ||
        user_Address.trim() === ""
    ) {
        alert("Please fill in all fields");
        return false; // Prevent form submission
    }

    // Check if passwords match
    if (user_password !== user_c_password) {
        alert("Passwords do not match");
        return false; // Prevent form submission
    }

    // Convert pictureBytes to base64-encoded string
    function convertBytesToBase64(pictureBytes) {
        var CHUNK_SIZE = 65536; // Chunk size (64 KB)

        var base64Parts = [];
        for (var i = 0; i < pictureBytes.length; i += CHUNK_SIZE) {
            var chunk = pictureBytes.subarray(i, i + CHUNK_SIZE);
            base64Parts.push(String.fromCharCode.apply(null, chunk));
        }

        return btoa(base64Parts.join(''));
    }

    // Usage in your code
    let pictureBase64 = convertBytesToBase64(pictureBytes);

    // Create an object with the request body
    const requestBody = {
        picture: pictureBase64,
        first_name: first_name,
        last_name: last_name,
        email: user_email,
        phone_number: PhoneNumber,
        username: username,
        password: user_password,
        birthdate: Birthdate,
        Address: user_Address,
        nationality: parseInt(user_country_id),
    };

    fetch("http://127.0.0.1:8000/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
    })
        .then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error(response.status);
            }
        })
        .then((responseData) => {
            // Redirect to login page
            window.location.href = "../admin/login.html";
        })
        .catch((error) => {
            // Request failed, handle error
            console.error("Registration request failed:", error);
        });
}
