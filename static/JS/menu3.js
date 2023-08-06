const btnMenu= document.querySelector("#btnmenu");
const menu= document.querySelector("#menu");
btnMenu.addEventListener("click", function(){
  menu.classList.toggle("mostrar");
});

const subMenuBtn = document.querySelectorAll(".submenu-btn");
for (let i=0; i<subMenuBtn.length; i++){
  subMenuBtn[i]. addEventListener("click", function(){
      if (window.innerWidth < 1024) {
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

window.addEventListener('load', function(){
	new Glider(document.querySelector('.carrousel__lista'), {
		  slidesToShow: 4,
  slidesToScroll: 4,
  draggable: true,
  dots: '.carrousel__indicadores',
  arrows: {
    prev: '.carrousel__anterior',
    next: '.carrousel__siguiente'
  }
	});
   responsive: [
    {
      // screens greater than >= 775px
      breakpoint: 775,
      settings: {
        // Set to `auto` and provide item width to adjust to viewport
        slidesToShow: 'auto',
        slidesToScroll: 'auto',
        itemWidth: 150,
        duration: 0.25
      }
    },{
      // screens greater than >= 1024px
      breakpoint: 1024,
      settings: {
        slidesToShow: 2,
        slidesToScroll: 1,
        itemWidth: 150,
        duration: 0.25
      }
    }
  ]
})
 window.addEventListener('load', function(){
        new Glider(document.getElementById('examenes'), {
            slidesToShow: 4,
            dots: '#dots2',
            draggable: true,
            arrows: {
                prev: '#glider-prev2',
                next: '#glider-next2'
            },
        });
    });
  window.addEventListener('load', function(){
        new Glider(document.getElementById('glider3'), {
            slidesToShow: 4,
            dots: '#dots3',
            draggable: true,
            arrows: {
                prev: '#glider-prev3',
                next: '#glider-next3'
            },
        });
    });


const itf = document.querySelector(".itf")
itf.addEventListener("click",()=>{
	alert ("se abrira una nueva pestaña");
	window.open("https://es.wikipedia.org/wiki/Federaci%C3%B3n_Internacional_de_Taekwondo");
})

$('#myModal').on('shown.bs.modal', function () {
  $('#myInput').trigger('focus')
})