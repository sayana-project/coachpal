document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("chat-form");
    const chatBox = document.getElementById("chat-box");

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const message = document.getElementById("message").value;

        chatBox.innerHTML += `<p><strong>Vous :</strong> ${message}</p>`;
        document.getElementById("message").value = "";

        fetch("/coachbot/chat/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML += `<p><strong>Coach IA :</strong> ${data.reply}</p>`;
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});