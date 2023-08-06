function elimNoti(idNoti){
    document.getElementById("noti" + idNoti).style.display = "None";
    location.href = "/elimNoti/" + idNoti;
}