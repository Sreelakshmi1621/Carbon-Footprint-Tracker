document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("factoryPasswordForm");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // prevent real form submission

        const inputs = form.querySelectorAll("input");
        const currentPassword = inputs[0].value.trim();
        const newPassword = inputs[1].value.trim();
        const confirmPassword = inputs[2].value.trim();

        // --- Check if all fields are filled ---
        if (!currentPassword || !newPassword || !confirmPassword) {
            alert("⚠️ All fields are required!");
            return;
        }

        // --- Password strength validation ---
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        if (!passwordRegex.test(newPassword)) {
            alert("❌ New password must be at least 8 characters long and include:\n- Uppercase letter\n- Lowercase letter\n- Number\n- Special character");
            return;
        }

        // --- Confirm password matches ---
        if (newPassword !== confirmPassword) {
            alert("❌ New Password and Confirm Password do not match!");
            return;
        }

        // --- Optional: check current password (mock) ---
        // For real backend, current password validation should occur there
        if (currentPassword === newPassword) {
            alert("⚠️ New password cannot be the same as the current password!");
            return;
        }

        // --- Mock success message ---
        alert("✅ Password changed successfully!");
        form.reset();
    });
});
