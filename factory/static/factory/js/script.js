// Wait until the page is fully loaded
document.addEventListener("DOMContentLoaded", function () {
  
  // Get the login form element
  const form = document.getElementById("loginForm");

  // When the form is submitted
  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the form from refreshing the page

    // Get the values entered by user
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // Check if both fields are filled
    if (email && password) {
      // This is a placeholder alert (actual backend will come later)
      alert("Login successful!\n");
    } else {
      alert("Please enter both email and password.");
    }
  });

});
