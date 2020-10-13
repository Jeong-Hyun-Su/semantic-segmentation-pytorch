const uploadBtn = document.querySelector('.upload-btn');
const inputImg = document.querySelector('#input-img');

function formSend() {
    let formData = new FormData();

    // Image, Version 선택
    const image = document.getElementById('image').files[0];

    formData.append("img", image);
    
    fetch(
        '/segmentation',
        {
            method: 'POST',
            body: formData,
        }
    )
    .then(response => {
        if ( response.status == 200){
            return response
        }
        else{
            throw Error("segmentation error")
        }
    })
    .then(response => response.blob())
    .then(blob => URL.createObjectURL(blob))
    .then(imageURL => {
        document.getElementById("result").setAttribute("src", imageURL);
    })
    .catch(e =>{
    })
}