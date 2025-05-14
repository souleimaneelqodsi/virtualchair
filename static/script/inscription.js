/*document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signupForm');
    const message = document.getElementById('message');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const data = {
        username: form.username.value,
        email: form.email.value,
        password: form.password.value,
      };

      try {
        const response = await fetch('http://localhost:5000/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
          message.style.color = 'green';
          message.textContent = 'Inscription réussie ! Vous pouvez maintenant vous connecter.';
          form.reset();
        } else {
          message.style.color = 'red';
          message.textContent = result.message || 'Erreur lors de l’inscription.';
        }
      } catch (err) {
        message.style.color = 'red';
        message.textContent = 'Une erreur est survenue. Veuillez réessayer.';
        console.error(err);
      }
    });
  });
  */

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
