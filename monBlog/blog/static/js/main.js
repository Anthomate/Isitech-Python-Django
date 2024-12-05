document.addEventListener('DOMContentLoaded', function() {
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
                } else {
                    alert('Erreur: ' + (data.error || 'action non réussie.'));
                }
            });
        });
    });
});
