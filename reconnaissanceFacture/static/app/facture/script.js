const form = document.querySelector(".upload-form")
fileInput = document.querySelector(".file-input")
progressArea = document.querySelector(".progress-area")
uploadedArea = document.querySelector(".uploaded-area")
btn = document.querySelector(".btn-outline-info")
showBtn = document.querySelector(".showBtn")
form.addEventListener("click", () =>{
  fileInput.click()
});
fileInput.onchange = ({target})=>{
  let file = target.files[0]
  if(file){
    btn.click()
  }
}