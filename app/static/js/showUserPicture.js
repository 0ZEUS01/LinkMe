function convertBase64ToBytes(base64String) {
    var raw = atob(base64String);
    var bytes = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) {
        bytes[i] = raw.charCodeAt(i);
    }
    return bytes;
}

// Retrieve the base64-encoded image from local storage
var base64Image = localStorage.getItem('picture');

// Convert base64 to bytes
var pictureBytes = convertBase64ToBytes(base64Image);

// Convert bytes to Blob
var blob = new Blob([pictureBytes], { type: 'image/jpeg' });

// Create object URLs for the Blob
var imageUrl = URL.createObjectURL(blob);

// Update the image sources
var profilePictureImg = document.getElementById('profilePicture');
var profilePictureDropdownImg = document.getElementById('profilePictureDropdown');

profilePictureImg.src = imageUrl;
profilePictureDropdownImg.src = imageUrl;

