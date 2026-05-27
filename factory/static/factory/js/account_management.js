// File: account_management.js

document.addEventListener("DOMContentLoaded", () => {
  // Get buttons
  const requestClosureBtn = document.getElementById("requestClosure");
  const deactivateAccountBtn = document.getElementById("deactivateAccount");
  const addAnotherFactoryBtn = document.getElementById("addAnotherFactory");


  // Request Closure Button Click
// Request Closure Button Click
requestClosureBtn.addEventListener("click", () => {
  const confirmClosure = confirm(
    "Are you sure you want to request closure of your factory account?"
  );
  if (confirmClosure) {
    // Send POST request to backend
    fetch("/request-closure/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/json"
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "success") {
        alert("✅ " + data.message);
      } else {
        alert("❌ Something went wrong.");
      }
    })
    .catch(error => console.error("Error:", error));
  }
});

// Function to get CSRF token (needed for Django POST)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

// Deactivate Account Button Click
deactivateAccountBtn.addEventListener("click", () => {
  const confirmDeactivate = confirm(
    "Are you sure you want to temporarily deactivate your account?"
  );
  if (confirmDeactivate) {
    // Send POST request to backend
    fetch("/deactivate-account/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/json"
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "success") {
        alert("✅ " + data.message);
        // Redirect to homepage/login after logout
        window.location.href = "/";
      } else {
        alert("❌ Something went wrong.");
      }
    })
    .catch(error => console.error("Error:", error));
  }
});
  // Add Another Factory Button Click
addAnotherFactoryBtn.addEventListener("click", () => {
    window.location.href = "/add_factoryprofile/"; // Django URL path to the view
});
  });

