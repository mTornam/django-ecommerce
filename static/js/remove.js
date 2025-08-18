document.addEventListener('DOMContentLoaded', function () {
    const csrftoken = getCookie('csrftoken')
    // remove from cart

    const removeBtns = document.querySelectorAll('.remove-btn')

    removeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
           const removeUrl = this.dataset.url
           const product_id = this.dataset.productId 
           const btn = this

           removeFromCart(csrftoken, removeUrl, product_id, btn)
        })
    });
})

function removeFromCart(csrftoken, url, id, btn) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'product_id': id,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`${response.status}: ${response.statusText}`)
        }
        return response.json()
    })
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count)
            updateCartList(btn, data.cart_total)
            console.log(data)
        } else {
            console.log('failed')
        }
    })
    .catch(error => {
        console.log(error.message)
    })
}

function updateCartCount(count) {
    const cartCount = document.querySelector('#cart-count')
    cartCount.textContent = count
}

function updateCartList(btn, total) {
    const tr = btn.closest('tr')
    const cartTotal = document.querySelector('#cart-total')
    
    if (!(total > 0)) {
        location.reload()
        return
    } 
    tr.remove()
    cartTotal.textContent = total
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}