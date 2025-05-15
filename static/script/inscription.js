

//chargement dynamique d'une page dans index.html
function loadPage(url) {
    fetch(url)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Page non trouvée");
            }
            return response.text();
        })
        .then((html) => {
            // Vérifie si l'élément existe
            const appContent = document.getElementById("app-content");
            if (appContent) {
                appContent.innerHTML = html;
            } else {
                console.error(
                    "Erreur : l'élément 'app-content' n'a pas été trouvé.",
                );
            }
        })
        .catch((error) => {
            const appContent = document.getElementById("app-content"); // It's good practice to get the element again or ensure it's available
            if (appContent) {
                appContent.innerHTML =
                    "<p>Erreur de chargement de la page.</p>";
            }
            console.error("Erreur de chargement de la page:", error);
        });
}


//inscription d'un nouveau utilisateur

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signupform");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
      const response = await fetch("http://localhost:5000/users/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, email, password }),
      });

      if (response.status === 201) {
        const data = await response.json();

        // Stocker uniquement les champs demandés dans le localStorage
        const userData = {
          id: data.id,
          username: data.username,
          email: data.email,
        };
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("isConnected", "true");

        alert("Inscription réussie !");
        // Redirection ou autre action ici
      } else if (response.status === 400) {
        const error = await response.json();
        alert("Erreur 400 : " + (error.message || "Données invalides."));
      } else if (response.status === 405) {
        alert("Erreur 405 : Méthode non autorisée.");
      } else {
        alert("Erreur inconnue : " + response.status);
      }
    } catch (error) {
      console.error("Erreur lors de la requête :", error);
      alert("Erreur réseau ou serveur.");
    }
  });
});



