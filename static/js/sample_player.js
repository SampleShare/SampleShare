//NOTE: wavesurfers js library
document.addEventListener('DOMContentLoaded', () => {
	const sampleElements = document.querySelectorAll('.sample-url');
	const playButtons = document.querySelectorAll('.play-button');

	const waveSurfersMapObject = {};

	sampleElements.forEach((sampleEle, index) => {
		const sampleUrl = sampleEle.value;
		const containerId = `waveform-${index + 1}`;
		const wavesurfer = initWaveSurfer(sampleUrl, containerId);

		waveSurfersMapObject[index] = wavesurfer

		playButtons[index].addEventListener('click', () => {
			if (wavesurfer.isPlaying()) {
				wavesurfer.pause();
				playButtons[index].querySelector('i').classList.replace('fa-pause', 'fa-play');
			} else {
				wavesurfer.play();
				playButtons[index].querySelector('i').classList.replace('fa-play', 'fa-pause');
			}
		});
	});

});

const initWaveSurfer = (url, containerId) => {
	//some of the options for waveforms, more here: https://wavesurfer.xyz/examples/?all-options.js
	const wavesurfer = WaveSurfer.create({
		container: `#${containerId}`,
		height: 50,
		normalize: true,
		waveColor: '#00FFCC',
		progressColor: '#6A1B9A',
		cursorColor: '#FFFFFF',
		barWidth: NaN,
		barGap: NaN,
		barRadius: NaN,
		cursorWidth: 2,
		fillParent: true,
		mediaControls: false,
		dragToSeek: true,
		backend: 'MediaElement',

		renderFunction: (channels, ctx) => {
			const { width, height } = ctx.canvas
			const scale = channels[0].length / width
			const step = 10

			ctx.translate(0, height / 2)
			ctx.strokeStyle = ctx.fillStyle
			ctx.beginPath()

			for (let i = 0; i < width; i += step * 2) {
				const index = Math.floor(i * scale)
				const value = Math.abs(channels[0][index])
				let x = i
				let y = value * height

				ctx.moveTo(x, 0)
				ctx.lineTo(x, y)
				ctx.arc(x + step / 2, y, step / 2, Math.PI, 0, true)
				ctx.lineTo(x + step, 0)

				x = x + step
				y = -y
				ctx.moveTo(x, 0)
				ctx.lineTo(x, y)
				ctx.arc(x + step / 2, y, step / 2, Math.PI, 0, false)
				ctx.lineTo(x + step, 0)
			}

			ctx.stroke()
			ctx.closePath()
		},
	});

	wavesurfer.load(url);
	wavesurfer.on('interaction', () => {
		wavesurfer.isPlaying() ? wavesurfer.pause() : wavesurfer.play();
	});

	document.addEventListener('keydown', (event) => {
		if (event.key === 'ArrowLeft' && wavesurfer.isPlaying()) {
			wavesurfer.seekTo(0);
		}
	});
	return wavesurfer
};

