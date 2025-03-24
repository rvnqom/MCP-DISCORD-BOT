document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector("#login-form");
    const registerForm = document.querySelector("#register-form");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const email = document.querySelector("#email").value;
            const password = document.querySelector("#password").value;

            console.log("🔹 Sending login request...");
            console.log("📤 Login Data:", { email, password });

            const response = await fetch("http://localhost:5500/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();
            console.log("✅ Login Response:", data);

            if (response.ok) {
                alert("Login successful!");
                window.location.href = "dashboard.html";
            } else {
                alert("Error: " + data.message);
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const name = document.querySelector("#name").value;
            const email = document.querySelector("#email").value;
            const password = document.querySelector("#password").value;

            console.log("🔹 Sending register request...");
            console.log("📤 Register Data:", { name, email, password });

            const response = await fetch("http://localhost:5500/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, password }),
            });

            console.log("📩 Register Request Sent");

            const data = await response.json();
            console.log("✅ Register Response:", data);

            if (response.ok) {
                alert("Registration successful!");
                window.location.href = "login.html";
            } else {
                alert("Error: " + data.message);
            }
        });
    }
});
