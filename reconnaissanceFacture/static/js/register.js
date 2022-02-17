const usernameField = document.querySelector('#usernameField')
const invalidUsername = document.querySelector('.invalid-username')
const emailField = document.querySelector('#emailField')
const passwordField = document.querySelector('#passwordField')
const invalidEmail = document.querySelector('.invalid-email')
const usernameSuccess = document.querySelector('.username-success')
const submitBtn = document.querySelector('.submit-btn')


emailField.addEventListener('keyup', (e) => {
  console.log('77777',77777)
  const emailVal= e.target.value
  emailField.classList.remove('is-invalid')
  invalidEmail.style.display = "none";


  if (emailVal.length > 0) {
      fetch("/authentication/validate-email", {
        body: JSON.stringify({ email: emailVal }),
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
     console.log('data', data)
     if(data.email_error)
     {
      submitBtn.disabled=true
      emailField.classList.add('is-invalid')
      invalidEmail.style.display = "block";
      invalidEmail.innerHTML= `<p>${data.email_error}</p>`
     } else{submitBtn.removeAttribute("disabled")}
  })
}
})


usernameField.addEventListener('keyup', (e) => {
    console.log('77777',77777)
    const usernameVal= e.target.value
    usernameSuccess.style.display = 'block'
    usernameSuccess.textContent = `Checking ${usernameVal}`

    usernameField.classList.remove('is-invalid')
    invalidUsername.style.display = "none";


    if (usernameVal.length > 0) {
        fetch("/authentication/validate-username", {
          body: JSON.stringify({ username: usernameVal }),
          method: "POST",
        })
          .then((res) => res.json())
          .then((data) => {
       console.log('data', data)
       usernameSuccess.style.display = 'none'
       if(data.username_error)
       {
        submitBtn.disabled=true
        usernameField.classList.add('is-invalid')
        invalidUsername.style.display = "block";
        invalidUsername.innerHTML= `<p>${data.username_error}</p>`
       }else{submitBtn.removeAttribute("disabled")}
    })
}
     
})