document.querySelectorAll('.favorite-button').forEach(button => {
    button.onclick = function () {
        const noteId = this.dataset.noteId;
        const isFavorited = this.dataset.favorited === 'true';
        const favoriteCountSpan = document.getElementById('favorite-count-' + noteId);
        let currentFavorites = parseInt(favoriteCountSpan.textContent);
        const img = this.querySelector('img');

        fetch('/favorite', {
            method: 'POST',
            body: JSON.stringify({
                note_id: noteId
            }),
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'favorite added') {
                    this.dataset.favorited = 'true';
                    img.src = 'static/images/favorite_hover.svg'; // Обновляем изображение на "в избранном"
                    favoriteCountSpan.textContent = currentFavorites + 1;
                } else if (data.status === 'favorite removed') {
                    this.dataset.favorited = 'false';
                    img.src = 'static/images/favorite_idle.svg'; // Обновляем изображение на "не в избранном"
                    favoriteCountSpan.textContent = currentFavorites - 1;
                }
            });
    };
});

document.querySelectorAll('.like-button').forEach(button => {
    button.onclick = function () {
        const noteId = this.dataset.noteId;
        const isLiked = this.dataset.liked === 'true';
        const likeCountSpan = document.getElementById('like-count-' + noteId);
        let currentLikes = parseInt(likeCountSpan.textContent);
        const img = this.querySelector('img');

        fetch('/like', {
            method: 'POST',
            body: JSON.stringify({
                note_id: noteId
            }),
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'like added') {
                    this.dataset.liked = 'true';
                    img.src = 'static/images/like_hover.svg'
                    likeCountSpan.textContent = currentLikes + 1;
                } else if (data.status === 'like removed') {
                    this.dataset.liked = 'false';
                    img.src = 'static/images/like_idle.svg'
                    likeCountSpan.textContent = currentLikes - 1;
                }
            });
    };
});



document.addEventListener('DOMContentLoaded', function () {
    function loadComments(postDiv, noteId) {
        const commentsSection = postDiv.nextElementSibling;

        fetch(`/get-comments/${noteId}`)
            .then(response => response.json())
            .then(comments => {
                commentsSection.innerHTML = '';

                comments.forEach((comment, index) => {
                    const commentDiv = document.createElement('div');
                    commentDiv.className = 'comment';
                    let innerHTML = `
                        <img class="comment-avatar" src="/uploads/avatars/${comment.avatar}">
                        <div class="comment-body">
                            <h5 class="comment-username">${comment.username}</h5>
                            <p class="comment-date">${comment.timestamp}</p>
                            <p class="comment-content">${comment.content}</p>
                    `;

                    if (index !== comments.length - 1) {
                        innerHTML += '<hr>';
                    }

                    innerHTML += `</div>`;
                    commentDiv.innerHTML = innerHTML;
                    commentsSection.appendChild(commentDiv);
                });
            });
    }

    function addComment(commentsSection, noteId, commentInput) {
        fetch('/add-comment', {
            method: 'POST',
            body: JSON.stringify({
                note_id: noteId,
                content: commentInput.value
            }),
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then(comment => {
                if (comment.status === 'success') {
                    const commentDiv = document.createElement('div');
                    commentDiv.className = 'comment';
                    commentDiv.innerHTML = `
                        <hr>
                        <img class="comment-avatar" src="/uploads/avatars/${comment.profile_picture}">
                        <div class="comment-body">
                            <h5 class="comment-username">${comment.username}</h5>
                            <p class="comment-date">${comment.timestamp}</p>
                            <p class="comment-content">${comment.content}</p>
                        </div>
                    `;
                    commentsSection.appendChild(commentDiv);
                    commentInput.value = '';
                } else {
                    alert('Ошибка при добавлении комментария: ' + comment.error);
                }
            })
            .catch(error => console.error('Ошибка:', error));
    }


    function toggleComments(event) {
        const postDiv = event.target.closest('.note');
        const commentsSection = postDiv.nextElementSibling;
        const newCommentForm = commentsSection.nextElementSibling;
        const noteId = this.dataset.noteId;

        const isCommentsShown = commentsSection.style.display === 'block';
        commentsSection.style.display = isCommentsShown ? 'none' : 'block';
        newCommentForm.style.display = isCommentsShown ? 'none' : 'block';

        loadComments(postDiv, noteId);
    }

    function showAddedComment(event) {
        event.preventDefault();
        const newCommentFormDiv = event.target.closest('.new-comment-form')
        const commentInput = newCommentFormDiv.querySelector('.new-comment-input')
        const commentsSection = newCommentFormDiv.previousElementSibling;
        const noteId = this.dataset.noteId;

        addComment(commentsSection, noteId, commentInput)
    }

    document.querySelectorAll('.toggle-comments-btn').forEach(button => {
        button.addEventListener('click', toggleComments);
    });

    document.querySelectorAll('.submit-comment-btn').forEach(button => {
        button.addEventListener('click', showAddedComment)
    })
});
