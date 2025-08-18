document.addEventListener('DOMContentLoaded', function () {
    const csrftoken = getCookie('csrftoken')
    const btns = document.querySelectorAll('button.add-to-cart, #add-to-cart-btn')

    btns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault()

            const form = this.closest('form')
            const product_id = this.dataset.productId
            let quantity = 1
            let addURL

            if (form) {
                const inputQuantity = form.querySelector('input[type="name"]')
                if (inputQuantity) {
                    const inputQuantityValue = parseInt(inputQuantity.value)
                    quantity = inputQuantityValue
                }

                addURL = form.action
            } else {
                addURL = this.dataset.url
            }

            addToCart(addURL, product_id, quantity, csrftoken)
        })
    });
})


function addToCart(url, id, qty, csrftoken) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'product_id': id,
            'quantity': qty
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
                console.log(data.message)
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

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}
















// document.addEventListener('DOMContentLoaded', function() {
//     const btns = document.querySelectorAll('button.add-to-cart, #add-to-cart-btn');

//     btns.forEach(btn => {
//         btn.addEventListener('click', function(e) {
//             e.preventDefault()

//             const product_id = this.dataset.productId;
//             console.log(product_id)
//             const url = this.dataset.url;

//             const csrftoken = getCookie('csrftoken');

//             fetch(url, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-CSRFToken': csrftoken
//                 },
//                 body: JSON.stringify({
//                     'product_id': product_id,
//                 })
//             })
//             .then(response => {
//                 if (!response.ok) {
//                     throw new Error(`${response.status}: ${response.statusText}`)
//                 }
//                 return response.json()
//             })
//             .then(data => {
//                 if (data.success) {
//                     updateCartCount(data.cart_count)
//                     console.log(data.message)
//                 } else {
//                     console.log('fail')
//                 }
//             })
//             .catch(error => {
//                 console.log(error.message)
//             })
//         });
//     });
// });

// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             // Does this cookie string begin with the name we want?
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }

// function updateCartCount(count){
//     const cartCount = document.querySelector('#cart-count')
//     cartCount.textContent = count
// }