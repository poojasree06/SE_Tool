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

const dragArea = document.querySelector(".drag-area");
const dragText = document.querySelector(".header");

let button = document.querySelector(".button");
let input = document.querySelector("input");

let file;

button.onclick = () => {
  input.click();
};

input.addEventListener("change", function () {
  file = this.files[0];
  dragArea.classList.add("active");
  displayFile();
});

dragArea.addEventListener("dragover", (event) => {
  event.preventDefault();
  dragText.textContent = "Release to upload";
  dragArea.classList.add("active");
});

dragArea.addEventListener("dragleave", () => {
  dragText.textContent = "Drag & Drop";
});

dragArea.addEventListener("drop", (event) => {
  event.preventDefault();

  file = event.dataTransfer.files[0];
  //console.log(file);
  displayFile();
});

function displayFile() {
  let fileType = file.type;
  //console.log(fileType);

  let validExtensions = ["text/x-python"];

  if (validExtensions.includes(fileType)) {
    let fileReader = new FileReader();

    fileReader.onload = () => {
      let fileURL = fileReader.result;
      //console.log(fileURL);
      // let tag = <Image>;
      // dragArea.innerHTML = tag;
    };
    fileReader.readAsDataURL(file);
  } else {
    alert("This file is not supported");
    dragArea.classList.remove("active");
  }
}
