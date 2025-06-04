function dataValidation() {
    var email = document.getElementById("email").value;
   
    if (email == "") {
        //alert("Email field cannot be empty");
        document.getElementById('$profileFlag').hidden = false;
    }
}   