// Get password input and strength message element
let password = document.getElementById("password");
let strength = document.getElementById("strength");

// Function to toggle password visibility
function togglePassword() {
    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}

// Check password strength as user types
password.addEventListener("keyup", function() {
    let value = password.value;

    let strongPattern = /^(?=.*[A-Z])(?=.*[0-9])(?=.{8,})/;
    let mediumPattern = /^(?=.*[0-9])(?=.{6,})/;

    if (strongPattern.test(value)) {
        strength.textContent = "Strong Password";
        strength.style.color = "green";
    } else if (mediumPattern.test(value)) {
        strength.textContent = "Medium Password";
        strength.style.color = "orange";
    } else {
        strength.textContent = "Weak Password";
        strength.style.color = "red";
    }
});

