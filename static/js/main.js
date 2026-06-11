// Like functionality via AJAX
function toggleLike(btn, postId) {
    fetch(`/post/${postId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const iconContainer = btn.querySelector('i');
        const countContainer = document.getElementById(`likesCount-${postId}`);
        
        if (data.status === 'liked') {
            iconContainer.classList.remove('fa-regular');
            iconContainer.classList.add('fa-solid', 'text-danger', 'animate-like-pulse');
            setTimeout(() => iconContainer.classList.remove('animate-like-pulse'), 300);
        } else {
            iconContainer.classList.remove('fa-solid', 'text-danger');
            iconContainer.classList.add('fa-regular');
        }
        
        if (countContainer) {
            countContainer.textContent = data.likes_count;
        }
    })
    .catch(error => console.error('Error toggling like:', error));
}

// Double-tap to like with big heart animation
function triggerLike(postId) {
    const bigHeart = document.getElementById(`bigHeart-${postId}`);
    const likeIcon = document.getElementById(`likeIcon-${postId}`);
    
    // Show big heart animation
    bigHeart.classList.remove('d-none');
    bigHeart.classList.remove('animate-heart-burst');
    
    // Trigger reflow to restart animation
    void bigHeart.offsetWidth;
    
    bigHeart.classList.add('animate-heart-burst');
    
    // Hide after animation
    setTimeout(() => {
        bigHeart.classList.add('d-none');
        bigHeart.classList.remove('animate-heart-burst');
    }, 1200);
    
    // Only API trigger like if it's not already liked visually
    if (likeIcon && likeIcon.classList.contains('fa-regular')) {
        const btn = likeIcon.parentElement;
        toggleLike(btn, postId);
    }
}

// Follow toggle via AJAX
function toggleFollow(username, btn) {
    const isFollowing = btn.textContent.trim() === 'Following';
    const numFollowersEl = document.getElementById('followerCount');
    const numFollowersMobileEl = document.getElementById('followerCountMobile');
    
    const endpoint = isFollowing ? `/unfollow/${username}` : `/follow/${username}`;
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        if (data.status === 'followed') {
            btn.textContent = 'Following';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-light', 'border');
        } else {
            btn.textContent = 'Follow';
            btn.classList.remove('btn-light', 'border');
            btn.classList.add('btn-primary');
        }
        
        if (numFollowersEl && data.follower_count !== undefined) {
            numFollowersEl.textContent = data.follower_count;
        }
        if (numFollowersMobileEl && data.follower_count !== undefined) {
            numFollowersMobileEl.textContent = data.follower_count;
        }
    })
    .catch(error => console.error('Error toggling follow:', error));
}

// Image Preview for New Post Modal and Edit Profile
function previewImage(inputEl, previewElId, containerElId) {
    if (inputEl.files && inputEl.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewElId);
            if(preview) preview.src = e.target.result;
            
            const container = document.getElementById(containerElId);
            if(container) container.classList.remove('d-none');
        }
        reader.readAsDataURL(inputEl.files[0]);
    }
}

function previewPostImage(input) {
    previewImage(input, 'imagePreview', 'imagePreviewContainer');
}

// Comment input interaction
document.addEventListener('DOMContentLoaded', () => {
    const commentInputs = document.querySelectorAll('.comment-input');
    commentInputs.forEach(input => {
        input.addEventListener('input', function() {
            const btn = this.nextElementSibling;
            if (this.value.trim().length > 0) {
                btn.style.opacity = '1';
                btn.removeAttribute('disabled');
            } else {
                btn.style.opacity = '0.5';
                btn.setAttribute('disabled', 'true');
            }
        });
    });
});
