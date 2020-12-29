window.addEventListener('load', function() {
	times = document.getElementsByClassName('time-posted')
	for(let i=0; i<times.length; i++) {
		times[i].replaceChildren((new Date(times[i].textContent)).toGMTString())
	}
});