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
        const newCommentForm = commentsSection.nextElementSibling;

        fetch(`/get-comments/${noteId}`)
            .then(response => response.json())
            .then(comments => {
                commentsSection.innerHTML = '';

                if (comments.length > 0) {
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

                    commentsSection.style.display = 'block';
                } else {
                    commentsSection.style.display = 'none';
                }

                newCommentForm.style.display = 'block';

                postDiv.dataset.commentsLoaded = 'true';
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
                        <img class="comment-avatar" src="/uploads/avatars/${comment.profile_picture}">
                        <div class="comment-body">
                            <h5 class="comment-username">${comment.username}</h5>
                            <p class="comment-date">${comment.timestamp}</p>
                            <p class="comment-content">${comment.content}</p>
                        </div>
                    `;
                    if (commentsSection.children.length > 0) {
                        commentsSection.appendChild(document.createElement('hr'));
                        commentsSection.appendChild(commentDiv);
                    } else {
                        commentsSection.innerHTML = '';
                        commentsSection.appendChild(commentDiv);
                        commentsSection.style.display = 'block';
                    }
                    commentInput.value = '';
                } else {
                    alert('Ошибка при добавлении комментария: ' + comment.error);
                }
            })
            .catch(error => console.error('Ошибка:', error));
    }

    function toggleComments(event) {
        const button = event.currentTarget;
        const postDiv = button.closest('.note');
        const commentsSection = postDiv.nextElementSibling;
        const newCommentForm = commentsSection.nextElementSibling;
        const noteId = button.dataset.noteId;

        if (commentsSection.style.display === 'block' || newCommentForm.style.display === 'block') {
            commentsSection.style.display = 'none';
            newCommentForm.style.display = 'none';
        } else {
            if (postDiv.dataset.commentsLoaded === 'true') {
                commentsSection.style.display = commentsSection.innerHTML ? 'block' : 'none';
                newCommentForm.style.display = 'block';
            } else {
                loadComments(postDiv, noteId);
            }
        }
    }

    function showAddedComment(event) {
        event.preventDefault();
        const button = event.currentTarget;
        const newCommentFormDiv = button.closest('.new-comment-form');
        const commentInput = newCommentFormDiv.querySelector('.new-comment-input');
        const commentsSection = newCommentFormDiv.previousElementSibling;
        const noteId = button.dataset.noteId;

        addComment(commentsSection, noteId, commentInput);
    }

    document.querySelectorAll('.toggle-comments-btn').forEach(button => {
        button.addEventListener('click', toggleComments);
    });

    document.querySelectorAll('.submit-comment-btn').forEach(button => {
        button.addEventListener('click', showAddedComment);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.start-timer-btn');

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const durationText = button.getAttribute('data-duration');
            const timerDisplay = button.nextElementSibling;

            let duration = parseDuration(durationText);
            startTimer(duration, timerDisplay, button);
        });
    });

    function parseDuration(durationText) {
        let duration = 0;
        const parts = durationText.split(' ');

        if (parts.length === 2) {
            const value = parseInt(parts[0]);
            const unit = parts[1].toLowerCase();

            if (['секунда', 'секунды', 'секунд'].some(u => unit.includes(u))) {
                duration = value;
            } else if (['минута', 'минуты', 'минут'].some(u => unit.includes(u))) {
                duration = value * 60;
            } else if (['час', 'часа', 'часов'].some(u => unit.includes(u))) {
                duration = value * 3600;
            }
        }
        return duration;
    }

    function getCorrectForm(number, forms) {
        if (number % 10 === 1 && number % 100 !== 11) {
            return forms[0];
        } else if ([2, 3, 4].includes(number % 10) && ![12, 13, 14].includes(number % 100)) {
            return forms[1];
        } else {
            return forms[2];
        }
    }

    function startTimer(duration, display, button) {
        let timer = duration;
        const interval = setInterval(() => {
            const minutes = Math.floor(timer / 60);
            const seconds = timer % 60;

            const minuteForms = ['минута', 'минуты', 'минут'];
            const secondForms = ['секунда', 'секунды', 'секунд'];

            const minuteText = getCorrectForm(minutes, minuteForms);
            const secondText = getCorrectForm(seconds, secondForms);

            button.innerHTML = `<img src="/static/images/play_button.svg" alt="Перезапустить таймер" />`;
            display.textContent = `${minutes} ${minuteText} ${seconds} ${secondText}`;

            if (--timer < 0) {
                clearInterval(interval);
                display.textContent = 'Время истекло';
                button.innerHTML = `<img src="/static/images/replay_button.svg" alt="Перезапустить таймер" />`;
                button.onclick = () => {
                    let duration = parseDuration(button.getAttribute('data-duration'));
                    startTimer(duration, display, button);
                };
            }
        }, 1000);
    }
});