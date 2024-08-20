(function($) {

	"use strict";

	var fullHeight = function() {

		$('.js-fullheight').css('height', $(window).height());
		$(window).resize(function(){
			$('.js-fullheight').css('height', $(window).height());
		});

	};
	fullHeight();

	$('#sidebarCollapse').on('click', function () {
      $('#sidebar').toggleClass('active');
  });

})(jQuery);


const toggleCollapse = (element) => {
    const collapseElement = document.getElementById(element.getAttribute('href'));
    collapseElement.classList.toggle('show');
};

document.querySelectorAll('.stretched-link').forEach((link) => {
    link.addEventListener('click', (event) => {
        event.preventDefault();
        toggleCollapse(event.target);
    });
});
