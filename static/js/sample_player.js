// function playSample(url) {
// 	var sound = new Howl({
// 		src: [url],
// 		autoplay: false,
// 		loop: false,
// 		html5: true,
// 		format: ['mp3', 'wav'],
// 	});
// 	sound.play();
// }

const playerControls = {
	playBtn: document.getElementById('playBtn'),
	nxtBtn: document.getElementById('nxtBtn'),
	prvBtn: document.getElementById('prvBtn'),
};

let sound = null;
let currentUrl = ''

const playPause = (url) => {
	if (url !== currentUrl) {
		if (sound) {
			sound.stop();
		}
		sound = new Howl({
			src: [url],
			autoplay: false,
			loop: false,
			html5: true,
			format: ['mp3', 'wav'],
		});
		currentUrl = url;
	}
	sound.playing() ? sound.pause() : sound.play();
};
