const btnMenu= document.querySelector("#btnmenu");
const menu= document.querySelector("#menu");
btnMenu.addEventListener("click", function(){
  menu.classList.toggle("mostrar");
});

const subMenuBtn = document.querySelectorAll(".submenu-btn");
for (let i=0; i<subMenuBtn.length; i++){
  subMenuBtn[i]. addEventListener("click", function(){
      if (window.innerWidth < 992) {
        const subMenu= this.nextElementSibling;
        const height = subMenu.scrollHeight;
        
        if(subMenu.classList.contains("desplegar")){
          subMenu.classList.remove("desplegar");
          subMenu.removeAttribute("style");        }
         else{ 
        subMenu.classList.add("desplegar");
        subMenu.style.height= height + "px";
      }
      }
  });
}


const itf = document.querySelector(".itf")
itf.addEventListener("click",()=>{
	alert ("se abrira una nueva pestaña");
	window.open("https://es.wikipedia.org/wiki/Federaci%C3%B3n_Internacional_de_Taekwondo");
})
