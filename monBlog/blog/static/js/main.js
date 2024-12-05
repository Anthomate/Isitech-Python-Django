document.addEventListener('DOMContentLoaded', function() {
    const toastContainer = document.getElementById('toast-container');

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.classList.add('toast', type, 'show');
        toast.textContent = message;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toastContainer.removeChild(toast);
            }, 300);
        }, 2000);
    }

    const djangoMessages = document.querySelector('body').getAttribute('data-messages');
    if (djangoMessages) {
        const messages = JSON.parse(djangoMessages);
        messages.forEach(msg => {
            showToast(msg.message, msg.tags);
        });
    }

    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = button.getAttribute('data-post-id');
            fetch(`/toggle-favorite/${postId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const icon = button.querySelector('.favorite-icon');
                    icon.classList.toggle('filled', data.is_favorited);
                    icon.classList.toggle('empty', !data.is_favorited);

                    showToast(
                        data.is_favorited
                            ? 'Article ajouté aux favoris'
                            : 'Article retiré des favoris',
                        'success'
                    );
                } else {
                    showToast('Erreur: ' + (data.error || 'action non réussie.'), 'error');
                }
            })
            .catch(error => {
                showToast('Erreur de réseau. Veuillez réessayer.', 'error');
            });
        });
    });
});