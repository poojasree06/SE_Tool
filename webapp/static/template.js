// const dropArea = document.querySelector(".drop_box"),
//   button = dropArea.querySelector("button"),
//   dragText = dropArea.querySelector("header"),
//   input = dropArea.querySelector("input");
// let file;
// var filename;

// button.onclick = () => {
//   input.click();
// };

// input.addEventListener("change", function (e) {
//   var fileName = e.target.files[0].name;
//   let filedata = `
//     <form action="" method="post">
//     <div class="form">
//     <h4>${fileName}</h4>
//     <input type="email" placeholder="Enter email upload file">
//     <button class="btn">Upload</button>
//     </div>
//     </form>`;
//   dropArea.innerHTML = filedata;
// });




// const dropArea = document.querySelector(".drop_box"),
//   button = dropArea.querySelector("button"),
//   dragText = dropArea.querySelector("header"),
//   input = dropArea.querySelector("input");
// let file;
// var filename;

// button.onclick = () => {
//   input.click();
// };
var input = document.getElementById( 'file-upload' );
var infoArea = document.getElementById( 'file-upload-filename' );
console.log(input)
console.log(infoArea)

input.addEventListener( 'change', showFileName );

function showFileName( event ) {
  
  // the change event gives us the input it occurred in 
  var input = event.srcElement;
  
  // the input has an array of files in the `files` property, each one has a name that you can use. We're just using the name here.
  var fileName = input.files[0].name;
  
  // use fileName however fits your app best, i.e. add it into a div
  infoArea.textContent = 'Uploaded File : ' + fileName;
}
