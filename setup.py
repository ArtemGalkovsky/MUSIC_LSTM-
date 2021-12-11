from os import path, getcwd, listdir, mkdir

NECESSARY_DATA = {
    ".": {"folders": ["web"]},
    "web": {"folders": ["static", "templates", "Upload", "Weights"]},
    "web/static": {"folders": ["CSS", "JS", "lang", "Generated"], "files": ["favicon.ico"]},
    "web/templates": {"files": ["index.html", "main.html", "train.html", "lang_choose.html", "header.html"]},
    "web/static/JS": {"files": ["header.js", "main.js", "train.js"]},
    "web/static/CSS": {"files": ["footer.css", "style.css", "main.css", "header.css", "train.css"]},
    "web/static/lang": {"files": ["ru.json", "en.json"]}
}

FILES = {"index.html": """<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="decription" content="Audio Updater With Neural Network.">
	<meta name="keywords" content="NN, LSTM, Neural Network">
	<meta name="author" content="Artem Galkovsky">
	<title>Neural Network</title>
	<link rel="stylesheet" href="{{ url_for('static', filename='CSS/style.css') }}">
	<link rel="preconnect" href="https://fonts.gstatic.com">
	<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@1,800&display=swap" rel="stylesheet">
	<link rel="preconnect" href="https://fonts.gstatic.com">
	<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@1,500;1,800&display=swap" rel="stylesheet">
	<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
</head>
<body>
	<div class="wrapper">
		<div class="container">
				{% include "header.html" %}

				{% include "main.html" %}
		</div>
	</div>
</body>
</html>""",
         "main.html": """<main>
	<link rel="stylesheet" href="{{ url_for('static', filename='CSS/main.css') }}">
	<div class="neural_network">
		<form name="nn_form" class="nn_form" action="/sys/data-ready" method="POST" enctype="multipart/form-data">
			<ul>
				<li title="{{ FILE_HOVER }}"><input type="file" accept=".wav" data-value="{{ FILE_LABEL }}" required name="file"></li>	
				<li title="{{ INPUT_HOVER }}" class="slide_container">
					<input type="range" min="0" max="1" step="0.001" value="0.500" data-value="{{ INPUT_LABEL }} 0.500" required name="input" data-type="{{ INPUT_LABEL }}"></li>	
				<li title="{{ LR_HOVER }}" class="slide_container">
					<input type="range" min="0" max="1" step="0.001" value="1.000" data-value="{{ LR_LABEL }} 1.000" required name="lr" data-type="{{ LR_LABEL }}"></li>								
				<li title="{{ CHUNKS_HOVER }}"><input type="number" placeholder="{{ CHUNKS_LABEL }}" required name="chunks"></li>
				<li title="{{ EPOCHS_HOVER }}"><input type="number" placeholder="{{ EPOCHS_LABEL }}" required name="epochs"></li>
				<li title="{{ BATCHES_HOVER }}"><input type="number" placeholder="{{ BATCHES_LABEL }}" required name="batches"></li>
			</ul>
			<button class="send_data" form="nn_form" type="submit" data-type="nn_form">{{ SEND_LABEL }}</button>
		</form>
	</div>
	<script type="text/javascript" src="{{ url_for('static', filename='JS/main.js') }}"></script>
	<script type="text/javascript">
		let sliders = document.querySelectorAll(".slide_container > input")
		sliders.forEach(slider => {
			slider.addEventListener("input", e => {
				console.log(e)
				let value = `${Number.parseFloat(slider.value).toFixed(3)}`
				slider.setAttribute("value", value)
				slider.dataset.value = slider.dataset.type + value
			})
		})
	</script>
</main>""",
         "train.html": """<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Training</title>
	<link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='CSS/train.css') }}">
	<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@1,500;1,800&display=swap" rel="stylesheet">
	<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
</head>
<body>
	<div class="wrapper">
		<div class="container">
			<div class="progress_bar">
				<div class="progress">0%</div>
			</div>
			<div class="console_container">
				<div class="console"></div>
			</div>
			<div class="info">

			</div>
		</div>
	</div>
	<script type="text/javascript" src="{{ url_for('static', filename='JS/train.js') }}"></script>
	<script type="text/javascript">
		window.procID = "{{ proc_id }}"
		document.addEventListener("DOMContentLoaded", () => {
			consoleAppend("{{ CONSOLE_HELLO }}", "color: #d66024")
			consoleAppend("{{ CONSOLE_TRAIN_START }}", "color: #d66024")
			consoleAppend("{{ CONSOLE_REFRESH }}", "color: #d66024")
			consoleAppend("{{ PROCESS_ID }} {{ proc_id }}")
			startSendingRequests()
		})
		function jsonProcessing (json, requestInterval) {
			let progress = document.querySelector(".progress")
			json.reverse()

			intervals.push(setInterval(() => {

				let js = json.pop()
				if (js) {
					let done = `${js.percent_done}%`
					progress.textContent = done
					progress.style.width = done
					let msgType = js.text.msg_type

					let text = ""

					if(msgType == "net_num") {
						text += "{{ CURRENT_CHUNK }} "
					} else if(msgType == "finished") {
						text += "{{ FINISHED }} {{ TIME }} "
					} else if(msgType == "audio ready") {
						clearInterval(requestInterval)
						console.log("audio")
						text += `<audio src='/static/Generated/${js.text.msg}' style="vertical-align: bottom" controls>`
					}

					text += js.text.msg
					consoleAppend(text, js.text.style)

					!json.length ? intervals.forEach(int => {clearInterval(int)}) : 0
				}

			}, parseInt(10000 / json.length)))
		}	
	</script>
</body>
</html>""",
         "lang_choose.html": """<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Choose Lang</title>
	<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
</head>
<body>
	<div class="wrapper">
		<div class="window">
			<h1>Выберите Язык:<br>Choose Lang:</h1>
			<a href="/main/ru">Русский</a>
			<a href="/main/en">English</a>
		</div>
	</div>
	<style>
		.wrapper{
			width: 100%;
			height: 100%;
			background: background: linear-gradient(to right, #03cffc, #e6a900);
			font-size: 1.6vw;
		}

		a{
			font-size: 5vw;
			color: purple;
			padding: 1vw;
		}

		a, a:visited{text-decoration: none;}
		a:hover{text-decoration: none;}

		*, *:before, *:after{
			-moz-box=box-sizing: border-box;
			-webkit-box-sizing: border-box;
			box-sizing: border-box;
		}

		.window{
			display: inline-block;
			text-align: center;
			border: solid 0.3vw red;
			border-radius: 5vw;
			background: linear-gradient(to right, #03cffc, #e6a900);
			animation-duration: 3s;
			animation-name: move_window;
			animation-iteration-count: 1;
			animation-timing-function: ease-in-out;

			height: 19vw;
			width: 50vw;
			margin: 7% 25%;
		}
	</style>
</body>
</html>""",
         "header.html": """<header>
	<link rel="stylesheet" href="{{ url_for('static', filename='CSS/header.css') }}">
	<span class="logo">NN</span>
	<span class="title">{{ TYPE_LABEL }}</span>
	<div class="menu">
		<span class="choosing_field">{{ TYPE }}</span>
	</div>
	<script type="text/javascript" src="{{ url_for('static', filename='JS/header.js') }}"></script>
</header>""",
         "header.js": """function main() {
	let menu = document.querySelector(".menu")
	let options = document.querySelectorAll(".options > li")
	let optionsContainer = document.querySelector(".options")
	let choosingField = document.querySelector(".choosingField")

	choosingField.textContent = options[0].textContent
	choosingField.dataset.id = options[0].dataset.id

	menu.addEventListener("click", (e) => {
		optionsContainer.classList.toggle("closed")
		clearTimeout(autoClosing)

		if(!optionsContainer.classList.contains("closed")){
			var autoClosing = setTimeout(() => {
				optionsContainer.classList.add("closed")
			}, 6000)
		}
	})

	options.forEach((element) => {
		element.addEventListener("click", (e) => {
			choosingField.dataset.id = element.dataset.id
			deleteAnimation(choosingField, element)

		})
	});
}

function deleteAnimation (choosingField, element) {
	let deletingInterval = setInterval(() => {
		let textLen = choosingField.textContent.length

		if(textLen <= 0) {
			clearInterval(deletingInterval)
			appendAnimation(choosingField, element)
		} 

		choosingField.textContent = choosingField.textContent.slice(0, textLen - 1)

	}, 50)
}

function appendAnimation (choosingField, element) {
	let text = element.textContent
	let letterIndex = 0
	let appendingInterval = setInterval(() => {
		if(letterIndex < text.length) {
			choosingField.textContent += text[letterIndex]
			letterIndex++
		} else {
			clearInterval(appendingInterval)
		}
	}, 50)
}
""",
         "main.js": """let uploadFile = document.querySelector(".nn_form ul li > input[type='file']")
uploadFile.addEventListener("input", () => {
		uploadFile.setAttribute("data-value", uploadFile.files.item(0).name)
})

let sendButton = document.querySelector(".send_data")
sendButton.addEventListener("click", () => {
	let isValidationClear = validateData(sendButton.dataset.type, sendButton)
	if(isValidationClear) {
		document.querySelector(`.${sendButton.dataset.type}`).submit()
	}
})




function errorInValidation (element) {
	if(element.style.background != "red") {
		let elementBg = element.style.background
		element.style.background = "red"
		var validationErrorTimeout = setTimeout(() => {
			element.style.background = elementBg
		}, 1000)
	}
	return 0
}

function validateData (formClass, button) {

	let data = Array.from(document.querySelectorAll(`.${formClass} ul li > input`))

	let validationResults = []

	validationResults.push(!data[0].files.length ? errorInValidation(data[0]) : 1)
	data.slice(3, 6).forEach((element) => {

		validationResults.push(!parseInt(element.value) ? errorInValidation(element) : 1)
	})

	let isClear = validationResults.every(Boolean)

	isClear ? 0 : errorInValidation(button)

	return isClear
}""",
         "train.js": """var consoleLine = 0
var intervals = []

function consoleAppend (text, style) {
	let console = document.querySelector(".console")
	console.innerHTML += `<p style='${style}'>${consoleLine}: ${text}</p>`
	consoleLine += 1
}

function startSendingRequests () {
	var requestInterval = setInterval(() => {
			fetch("/sys/get-proc-info", {
				method: "POST",
				body: JSON.stringify({"proc_id": window.procID})
			}).then(response => {
				response.json().then(result => {
					jsonProcessing(Array.from(result), requestInterval)

				})
			})
	}, 10000)
}
""",
         "footer.css": """""",
         "style.css": """*{
	padding: 0;
	margin: 0;
	border: 0;
}

*, *:before, *:after{
	-moz-box=box-sizing: border-box;
	-webkit-box-sizing: border-box;
	box-sizing: border-box;
}

nav, footer, header, aside{
	display: block;
}

html, body{
	height: 100%;
	width: 100%;
	font-size: 100%;
	line-height: 1;
	font-size: 14px;
	-ms-text-size-adjust: 100%;
	-moz-text-size-adjust: 100%;
	-webkit-text-size-adjust: 100%;
}


input, button, textarea{
	font-family: inherit;

}

*{	
	outline: 0;
}

input::-ms-clear{display: none;}
button{cursor: pointer;}
button::-moz-focus-inner{padding: 0; border: 0}
a, a:visited{text-decoration: none;}
a:hover{text-decoration: none;}
ul li{list-style-type: none;}
img{vertical-align: top;}
select{-webkit-appearance: none}

.wrapper{
	width: 100%;
	height: 100%;
	font-family: 'JetBrains Mono', monospace;
	background: linear-gradient(to right, #03cffc, #e6a900);
}

.container{
	width: 100%;
	height: 100%;
	font-size: 10vh;
}
""",
         "main.css": """*{
	padding: 0;
	margin: 0;
	border: 0;
}

*, *:before, *:after{
	-moz-box=box-sizing: border-box;
	-webkit-box-sizing: border-box;
	box-sizing: border-box;
}

nav, footer, header, aside{
	display: block;
}

html, body{
	height: 100%;
	width: 100%;
	font-size: 100%;
	line-height: 1;
	font-size: 14px;
	-ms-text-size-adjust: 100%;
	-moz-text-size-adjust: 100%;
	-webkit-text-size-adjust: 100%;
}


input, button, textarea{
	font-family: inherit;

}

*{	
	outline: 0;
}

input::-ms-clear{display: none;}
button{cursor: pointer;}
button::-moz-focus-inner{padding: 0; border: 0}
a, a:visited{text-decoration: none;}
a:hover{text-decoration: none;}
ul li{list-style-type: none;}
img{vertical-align: top;}
select{-webkit-appearance: none}

.hide{
	display: none;
}

main{
	height: auto;
	font-size: 7.7vw;
	background: linear-gradient(to right, #03cffc, #e6a900);
	outline: linear-gradient(to right, #03cffc, #e6a900);
	transition: 0.6s ease-out;
	transform: translateY(0%);
	z-index: 0;
	opacity: 1;
	color: #b4ffdd;
}

main.fell_off{
	transition: 0.9s ease-in;
	transform: translateY(450px);
	opacity: 0;
}

.nn_form > ul li{
	display: block;
	padding: 1vw 5vw;
}

.nn_form ul li > input[type="file"]{
	margin-top: 3vw;
	height: 10.16vw;
}

.nn_form ul li > input[type="file"]::-webkit-file-upload-button{
  visibility: hidden;
}

.nn_form ul li > input[type="file"]::before{
	content: attr(data-value);
	display: inline-block;
	text-align: center;
	width: 100%;
	height: auto;
	text-overflow: ellipsis;
	overflow: hidden;
	white-space: nowrap;
}

.nn_form ul li > input[type="number"]::-webkit-inner-spin-button,
.nn_form ul li > input[type="number"]::-webkit-outer-spin-button{
	-webkit-appearance: none;
	margin: 0;
}

.nn_form ul li > input{
	background: linear-gradient(45deg, #f5c240, #f54c40);
	height: 100%;
	width: 100%;
	vertical-align: top;
	font-size: 100%;
	border-radius: 100px;
	color: #a74fff;
	padding-left: 3vw;
	padding-right: 3vw;
	text-align: center;
}

.nn_form ul li > input::placeholder{
	color: #a74fff;
	text-align: center;
}

.slide_container{
	width: 100%;
}

.slide_container > input:after{
	content: attr(data-value);
	position: absolute;
	z-index: 0;
	padding: 0vw 5vw;
	width: 90%;
	text-align: center;
	opacity: 0.5;
}

.slide_container > input{
	-webkit-appearance: none;
	padding: 0.16vw 0.3vw !important;
  	appearance: none;
  	width: 100%;
  	height: 100%;
  	background: linear-gradient(45deg, #f5c240, #f54c40);
  	outline: none;
  	-webkit-transition: 0.2s;
  	transition: opacity 0.2s;
  	overflow: auto;
  	z-index: 2;
}

.slide_container > input::-webkit-slider-thumb {
  	-webkit-appearance: none;
  	appearance: none;
  	width: 10vw;
  	height: 10vw;
  	background: linear-gradient(45deg, #03cffc, #e6a900);
  	border-radius: 100px;
}

.slide_container > input::-moz-range-thumb {
  	width: 10vw;
  	height: 10vw;
  	background: linear-gradient(to right, #03cffc, #e6a900);
  	border-radius: 100px;
}

form{
	overflow: auto;
}

.send_data{
	height: 10vw;
	width: 30vw;
	background: linear-gradient(45deg, #f5c240, #f54c40);
	font-size: 7vw;
	outline: 0;
	border-radius: 50px;
	margin: 0vw 5vw 1vw 3vw;
	float: right;
}""",
         "header.css": """*{
	padding: 0;
	margin: 0;
	border: 0;
}

*, *:before, *:after{
	-moz-box=box-sizing: border-box;
	-webkit-box-sizing: border-box;
	box-sizing: border-box;
}

nav, footer, header, aside{
	display: block;
}

html, body{
	height: 100%;
	width: 100%;
	font-size: 100%;
	line-height: 1;
	font-size: 14px;
	-ms-text-size-adjust: 100%;
	-moz-text-size-adjust: 100%;
	-webkit-text-size-adjust: 100%;
}


input, button, textarea{
	font-family: inherit;

}

*{	
	outline: 0;
}

input::-ms-clear{display: none;}
button{cursor: pointer;}
button::-moz-focus-inner{padding: 0; border: 0}
a, a:visited{text-decoration: none;}
a:hover{text-decoration: none;}
ul li{list-style-type: none;}
img{vertical-align: top;}
select{-webkit-appearance: none}

header{
	z-index: 1;
	font-family: 'JetBrains Mono', monospace;
	overflow: auto;
	width: 100%;
	background: linear-gradient(to right, #03cffc, #e6a900);
	font-size: 7.7vw;
}

.logo{
	float: right;
	padding-right: 3vw;
}

span{
	display: inline-block;
	padding: 1.3vw 0 1.3vw 2.5vw;
}

.title{
	color: #ffd67d;
}


.choosing_field{
	padding-left: 0;
}

.menu{
	display: inline-block;
	width: 50vw;
	background: linear-gradient(to right, #f5c240, #f54c40);
	text-align: center;
	height: 100%;
}
""",
         "train.css": """*{
	padding: 0;
	margin: 0;
	border: 0;
}

*, *:before, *:after{
	-moz-box=box-sizing: border-box;
	-webkit-box-sizing: border-box;
	box-sizing: border-box;
}

nav, footer, header, aside{
	display: block;
}

html, body{
	height: 100%;
	width: 100%;
	font-size: 100%;
	line-height: 1;
	font-size: 14px;
	-ms-text-size-adjust: 100%;
	-moz-text-size-adjust: 100%;
	-webkit-text-size-adjust: 100%;
}


input, button, textarea{
	font-family: inherit;

}

*{	
	outline: 0;
}

input::-ms-clear{display: none;}
button{cursor: pointer;}
button::-moz-focus-inner{padding: 0; border: 0}
a, a:visited{text-decoration: none;}
a:hover{text-decoration: none;}
ul li{list-style-type: none;}
img{vertical-align: top;}
select{-webkit-appearance: none}

.wrapper{
	width: 100%;
	height: 100%;
	font-family: 'JetBrains Mono', monospace;
	background: linear-gradient(to right, #03cffc, #e6a900);
}

.container{
	overflow: auto;
	width: 100%;
	height: 100%;
	float: left;
}

.progress_bar{
	position: relative;
	width: 80%;
	text-align: center;
	margin: 5vw auto;
	height: 8vw;
	background: gray;
	font-size: 8vw;
	overflow: hidden;
	border-radius: 10vw;
}

.progress{
	display: inline-block;
	width: 0%;
	height: 100%;
	background: linear-gradient(to right, #f5c240, #f54c40);
	float: left;
	padding: 0% 1%;
}

.console_container{
	display: flex;
	position: relative;
	background: linear-gradient(to right, #f5c240, #f54c40);
	width: 80%;
	height: 60vw;
	margin: 0 auto;
	border-radius: 10vw;
	margin-bottom: 3vw;
}

.console{
	width: 98%;
	height: 98%;
	background: gray;
	margin: auto;
	vertical-align: middle;
	border-radius: 10vw;
	font-size: 3vw;
	padding: 5vw;
	word-wrap: break-word;
	overflow: auto;
	scrollbar-width: none;
	-ms-overflow-style: none;
	transition: width 2s;

}

.console::-webkit-scrollbar{
	display: none;
}

.console > pre{
	font-family: 'JetBrains Mono', monospace;
}""",
         "ru.json": """{	
	"main": {
		"TYPE": "Нейросеть",
		"TYPE_LABEL": "Тип:",

		"FILE_HOVER": "Выберите небольшой музыкальный файл формата wav. Очень важно выбрать маленький файл, иначе может просто не хватить оперативной памяти.",
		"FILE_LABEL": "Выберите файл",

		"INPUT_HOVER": "Входные данные. Данные которые будут использоваться как X. Лучшее значение - среднее, то есть 0.5.",
		"INPUT_LABEL": "Вход. знач:",

		"LR_HOVER": "Скорость Обучения. Зависит от параметров ниже.",
		"LR_LABEL": "v обучения:",

		"CHUNKS_HOVER": "Количество частей/чанков. Количество частей, на которые будет разделён аудио файл. Формула расчёта: 1 секунда ~= 20000 => 20000 * время. Не используйте значения больше допустимых (из формулы), иначе не хватит оперативной памяти.",
		"CHUNKS_LABEL": "Кол-во частей",

		"EPOCHS_HOVER": "Количество эпох. Количество проходов по одной части.",
		"EPOCHS_LABEL": "Кол-во эпох",

		"BATCHES_HOVER": "Количество партий/батчей. Количество входных значений для прохождения одной эпохи.",
		"BATCHES_LABEL": "Кол-во партий",

		"SEND_LABEL": "Send"

	},
	"train": {
		"CURRENT_CHUNK": "Текущая Часть:",
		"FINISHED": "Завершено!",
		"TIME": "Время:",
		"CONSOLE_HELLO": "Привет, я консоль! ",
		"CONSOLE_TRAIN_START": "Обучение начато.",
		"CONSOLE_REFRESH": "Консоль будет обновляться примерно каждые 10 секунд.",
		"PROCESS_ID": "Серверный Идентификатор Процесса Нейросети: "
	}
}""",
         "en.json": """{	
	"main": {
		"TYPE": "Neural Net",
		"TYPE_LABEL": "Type:",

		"FILE_HOVER": "Select a small music file in wav format. It is very important to choose a small file, otherwise there may simply not be enough RAM.",
		"FILE_LABEL": "Select File",

		"INPUT_HOVER": "Input data. The data to be used as X. The best value is the average, that is 0.5.",
		"INPUT_LABEL": "Input:",

		"LR_HOVER": "Learning Speed. Depends on the options below.",
		"LR_LABEL": "LearnRate:",

		"CHUNKS_HOVER": "Number of parts / chunks. The number of parts into which the audio file will be divided. Calculation formula: 1 second ~ = 20000 => 20000 * time. Do not use values ​​larger than the allowable ones (from the formula), otherwise there will not be enough RAM.",
		"CHUNKS_LABEL": "Number Of Chunks",

		"EPOCHS_HOVER": "The number of epochs. Number of passes for one chunk.",
		"EPOCHS_LABEL": "Number Of Epochs",

		"BATCHES_HOVER": "The number of batches. The number of inputs to go through one epoch.",
		"BATCHES_LABEL": "Number Of Batches",

		"SEND_LABEL": "Send"

	},
	"train": {
		"CURRENT_CHUNK": "Current Chunk:",
		"FINISHED": "Finished!",
		"TIME": "Time:",
		"CONSOLE_HELLO": "Hello, I'm Console.",
		"CONSOLE_TRAIN_START": "Training Start.",
		"CONSOLE_REFRESH": "The console is refreshed approximately every 10 seconds.",
		"PROCESS_ID": "Server Neural Network Process ID:"
	}
}""", "favicon.ico": b'\x00\x00\x01\x00\x01\x00  \x00\x00\x01\x00 \x00\xa8\x10\x00\x00\x16\x00\x00\x00(\x00\x00\x00 \x00\x00\x00@\x00\x00\x00\x01\x00 \x00\x00\x00\x00\x00\x00\x10\x00\x00\xc3\x0e\x00\x00\xc3\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1b\x00\x10\x11\x16\x00\x13\x13\x17\x07\x0e\x0f\x15\x1c\x0e\x0f\x15\x1c\x13\x13\x17\x07\x10\x11\x16\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x15\x15\x187\x1c\x1c\x1b\xa5/-#\xd8/-#\xd8\x1c\x1c\x1b\xa5\x15\x15\x187\x00\x00\x00\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x19\x19\x1a\x00\x15\x15\x187,*"\xdb\x83|I\xff\xbe\xb3b\xff\xbe\xb3b\xff\x84}I\xff,*"\xdc\x15\x15\x187\x19\x19\x1a\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x11\x12\x16\x05\x1c\x1c\x1b\xa6\x84}I\xff\xe1\xd4r\xff\xe1\xd4r\xff\xe1\xd4r\xff\xe1\xd4r\xff\x84}I\xff\x1c\x1c\x1b\xa6\x11\x12\x16\x05\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x0e\x0f\x15\x19/-#\xd8\xbe\xb3b\xff\xe1\xd4r\xff\xdf\xd2q\xff\xdf\xd2q\xff\xe1\xd4r\xff\xbe\xb3b\xff/-#\xd8\x0e\x0f\x15\x19\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1b\x1b\x1b\x00\x18\x10\x0f\x00\x19\x13\x12\x06\x18\x0f\r\x19\x18\x0f\r\x19\x19\x13\x12\x06\x18\x10\x0f\x00\x1a\x1a\x19\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x12\x13\x17&.-#\xe1\xbf\xb4c\xff\xe1\xd4r\xff\xdf\xd2q\xff\xdf\xd2q\xff\xe1\xd4r\xff\xbe\xb3b\xff/-#\xd8\x0e\x0f\x15\x19\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\n\x00\x00\x00\x19\x15\x147\x1a\x1c\x1c\xa7\x1e.1\xda\x1e.1\xda\x1a\x1c\x1c\xa7\x19\x15\x147\x16\x06\x03\x00\x1a\x1a\x1a\x0f\x1a\x1a\x1a\\\x1a\x1a\x1a\xb7\x1b\x1b\x1b\xe5\x86~J\xff\xe1\xd4r\xff\xe1\xd4r\xff\xe1\xd4r\xff\xe1\xd4r\xff\x84}I\xff\x1c\x1c\x1b\xa5\x11\x11\x16\x04\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x19\x19\x00\x19\x15\x157\x1d+.\xdc.\x81\x90\xff:\xbb\xd1\xff:\xbb\xd2\xff.\x81\x90\xff\x1d+.\xda\x1a\x18\x18y\x1a\x1a\x1a\xb6\x1a\x1a\x1a\xb8\x1a\x1a\x1aX\x16\x16\x18D+*"\xe1\x83|H\xff\xbf\xb4c\xff\xbf\xb4c\xff\x84}I\xff*)!\xf9\x18\x18\x19\x9c\x1a\x1a\x1a\t\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x11\x10\x05\x1a\x1c\x1c\xa5.\x82\x90\xffA\xdd\xf8\xff@\xdd\xf9\xff@\xdd\xf9\xffA\xdd\xf8\xff/\x83\x91\xff\x1a\x1b\x1b\xe6\x1a\x1a\x1a`\x1a\x1a\x1a\x0f\x1a\x1a\x1a\x00\x1a\x1a\x1a#\x19\x19\x19\xc8\x1c\x1c\x1b\xbb-,#\xe8-,"\xea\x1c\x1c\x1b\xa4\x17\x17\x18Q\x1a\x1a\x1a\xb6\x1a\x1a\x1a\x86\x1a\x1a\x1a\x08\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x0f\r\x1c\x1e.1\xd7:\xbb\xd2\xff@\xdd\xf8\xff@\xdb\xf6\xff@\xdb\xf6\xff@\xdd\xf8\xff:\xbb\xd1\xff\x1e.1\xd8\x18\x0e\r\x18\x1a\x1a\x1a\x00\x1a\x1a\x1a\x02\x1a\x1a\x1a\x8d\x1a\x1a\x1a\x97\x14\x14\x17\x07\x18\x18\x19\x8c\x18\x18\x19\x8d\t\t\x13\x02\x19\x19\x19\x00\x1a\x1a\x1a&\x1a\x1a\x1a\xbd\x1a\x1a\x1a~\x1a\x1a\x1a\x06\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x0f\r\x1c\x1e.1\xd7:\xbb\xd2\xff@\xdd\xf8\xff@\xdb\xf6\xff@\xdb\xf6\xff@\xdd\xf8\xff:\xbb\xd2\xff\x1e.1\xd8\x18\x0f\r\x19\x1a\x1a\x1a\x00\x1a\x1a\x1a?\x1a\x1a\x1a\xc7\x1a\x1a\x1a*\x1a\x1a\x1a\x00\x1a\x1a\x1a\x83\x1a\x1a\x1a\x83\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a,\x1a\x1a\x1a\xc1\x1a\x1a\x1aw\x1a\x1a\x1a\x04\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x12\x10\x06\x1a\x1c\x1c\xa5.\x82\x90\xffA\xdd\xf8\xff@\xdd\xf9\xff@\xdd\xf9\xffA\xdd\xf8\xff.\x82\x90\xff\x1a\x1c\x1c\xa6\x18\x10\x0e\x04\x1a\x1a\x1a\x0c\x1a\x1a\x1a\xae\x1a\x1a\x1as\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x83\x1a\x1a\x1a\x83\x1a\x1a\x1a\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a1\x1a\x1a\x1a\xc4\x1a\x1a\x1ao\x1a\x1b\x1b\x03\x18\x12\x11\x05\x18\x0f\r\x19\x18\x0f\r\x19\x19\x13\x12\x06\x18\x10\x0f\x00\x1b\x1b\x1b\x00\x00\x00\x00\x00\x1a\x19\x19\x00\x19\x15\x157\x1d+.\xdc.\x82\x90\xff:\xbb\xd2\xff:\xbb\xd2\xff.\x81\x90\xff\x1d+-\xe0\x19\x15\x157\x1a\x19\x19\x00\x1a\x1a\x1ab\x1a\x1a\x1a\xb8\x1a\x1a\x1a\x13\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x83\x1a\x1a\x1a\x83\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a7\x1a\x1a\x1a\xc3\x1a\x18\x18\x83\x1a\x1c\x1c\xa3\x1e.1\xd9\x1e.1\xda\x1a\x1c\x1c\xa7\x19\x15\x147\x08\x00\x00\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x05\x00\x00\x00\x19\x15\x157\x1a\x1c\x1c\xa7\x1e.1\xda\x1e.1\xd8\x1a\x1c\x1c\xc3\x1a\x19\x18\xc2\x1a\x1b\x1b\x17\x1a\x1a\x1a\x1d\x1a\x1a\x1a\xc3\x1a\x1a\x1aN\x1a\x1a\x1a\x00\x19\x19\x17\x07\x17\x18\x12=\x19\x19\x16\xb7\x19\x19\x16\xb7\x17\x17\x12=\x19\x19\x17\x07\x19\x19\x16\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x1a\x19\x19\x00\x19\x17\x17d\x1d)+\xfb.\x82\x90\xff:\xbb\xd1\xff:\xbb\xd2\xff.\x81\x90\xff\x1d+.\xdb\x19\x15\x157\x1a\x19\x19\x00\x00\x00\x00\x00\x1a\x19\x19\x00\x18\x10\x0f\x00\x18\x13\x12\x06\x18\x0f\r\x19\x18\x0e\r\x18\x19\x17\x17\x0f\x1a\x1a\x1a\xa4\x1a\x1a\x1a\x85\x1a\x1a\x1a\x89\x1a\x1a\x1a\x9c\x1a\x1a\x1a\x05\x19\x19\x18\x0e\x1a\x1a\x19\x8e&%?\xf273o\xff73o\xff&%?\xf2\x1a\x1a\x19\x8e\x19\x19\x18\x0e\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x18\x11\x10\x05\x1a\x1c\x1c\xa4/\x82\x91\xffA\xdd\xf8\xff@\xdd\xf9\xff@\xdd\xf9\xffA\xdd\xf8\xff.\x82\x90\xff\x1a\x1c\x1c\xa5\x18\x11\x10\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a-\x1a\x1a\x1a\xd2\x1a\x1a\x1a\xd4\x1a\x1a\x1a,\x1a\x1a\x1a\x00\x19\x19\x16r-*Q\xfcSL\xc3\xff\\T\xdd\xff\\T\xdd\xffSL\xc3\xff-*Q\xfc\x19\x19\x16q\x1a\x1a\x1a\x00\x1a\x1a\x1a\x05\x19\x13\x12(\x1e.1\xdb:\xbb\xd2\xff@\xdd\xf8\xff@\xdb\xf6\xff@\xdb\xf6\xff@\xdd\xf8\xff:\xbb\xd1\xff\x1e.1\xd7\x18\x0f\r\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x0c\x1a\x1a\x1a\xbe\x1a\x1a\x1a\xcb\x1a\x1a\x1a\x13\x16\x17\x0f\x0e\x1e\x1d%\xc7JD\xa8\xff\\T\xdf\xff[S\xdb\xff[S\xdb\xff\\T\xdf\xffJD\xa8\xff\x1d\x1d$\xde\x1a\x1a\x19\x9d\x1a\x1a\x1a\xb0\x1a\x19\x18\xc4\x1e,/\xf5:\xbc\xd3\xff@\xdd\xf8\xff@\xdb\xf6\xff@\xdb\xf6\xff@\xdd\xf8\xff:\xbb\xd2\xff\x1e.1\xd7\x18\x0f\r\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\\\x1a\x1a\x1a\xc1\x1a\x1a\x1a\xba\x1a\x1a\x1av\x16\x16\x0e\x1c"!2\xddRK\xc0\xff\\S\xdd\xff[S\xdb\xff[S\xdb\xff\\T\xdd\xffRK\xc1\xff"!0\xed\x19\x19\x17z\x1a\x1a\x1aN\x1a\x19\x196\x1a\x1c\x1c\xab/\x82\x91\xffA\xdd\xf8\xff@\xdd\xf9\xff@\xdd\xf9\xffA\xdd\xf8\xff.\x82\x90\xff\x1a\x1c\x1c\xa5\x18\x11\x10\x06\x00\x00\x00\x00\x1b\x1b\x1b\x00\x0f\x14\x16\x00\x12\x15\x17\x06\x0e\x12\x15\x19\r\x12\x15\x17\x19\x19\x1a!\x1a\x1a\x1a\xbf\x1a\x1a\x1aQ\x1a\x1a\x1a3\x1a\x1a\x1a\xc5\x19\x19\x18S\x1e\x1d%\xd3JD\xa8\xff\\T\xdf\xff[S\xdb\xff[S\xdb\xff\\T\xdf\xffJD\xa8\xff\x1e\x1d%\xc7\x17\x17\x10\x0f\x1a\x1a\x1a\x00\x1a\x19\x18\x00\x1a\x18\x17r\x1d)+\xfc.\x82\x91\xff:\xbb\xd2\xff:\xbb\xd2\xff.\x82\x90\xff\x1d+.\xdc\x19\x15\x157\x1a\x19\x19\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x15\x17\x187\x1c\x1b\x1b\xa70\'"\xda0\'"\xd7\x1c\x1b\x1b\xd1\x18\x19\x19\xad\x1c\x1b\x1a\x08\x1a\x1a\x1a\x0f\x1a\x1a\x1a\xaa\x1a\x1a\x1a\xe9\x19\x19\x18\xd4-*R\xf9SL\xc3\xff\\T\xdd\xff\\T\xdd\xffSL\xc3\xff-*Q\xfc\x19\x19\x16r\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1a\x1a\x1aQ\x1a\x1a\x1a\xc8\x1a\x18\x17s\x1a\x1c\x1c\xa3\x1e.1\xd9\x1e.1\xda\x1a\x1c\x1c\xa7\x19\x15\x147\x08\x00\x00\x00\x1a\x1a\x1a\x00\x19\x19\x1a\x00\x15\x17\x187-%!\xdb\x8b^B\xff\xca\x84Y\xff\xca\x84Y\xff\x8b^B\xff-&!\xdb\x18\x19\x19x\x1a\x1a\x1a\xb5\x1a\x1a\x1a\xb5\x1a\x1a\x1a\xcb\x1a\x1a\x1a\x83\x1a\x1a\x19\x8d&%?\xf263n\xff63n\xff&%?\xf2\x1a\x1a\x19\x8f\x19\x19\x18\x0e\x1a\x1a\x1a\x00\x1a\x1a\x1aQ\x1a\x1a\x1a\xcb\x1a\x1a\x1aQ\x19\x14\x13\x00\x18\x12\x12\x06\x18\x0f\r\x19\x18\x0f\r\x19\x18\x13\x12\x06\x18\x10\x0f\x00\x1a\x1a\x19\x00\x00\x00\x00\x00\x11\x14\x17\x05\x1c\x1b\x1b\xa5\x8c^B\xff\xef\x9af\xff\xef\x9af\xff\xef\x9af\xff\xef\x9af\xff\x8c_C\xff\x1b\x1b\x1a\xe6\x1a\x1a\x1a`\x1a\x1a\x1a\r\x1a\x1a\x1a@\x1a\x1a\x1a\xc6\x1a\x1a\x1a3\x17\x18\x12<\x18\x18\x13s\x18\x18\x13s\x17\x18\x12?\x19\x19\x17\x07\x19\x1a\x17\x00\x1a\x1a\x1aQ\x1a\x1a\x1a\xcb\x1a\x1a\x1aQ\x1b\x1b\x1b\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x12\x16\x1c0\'"\xd7\xca\x84X\xff\xef\x9af\xff\xed\x99e\xff\xed\x99e\xff\xef\x9af\xff\xca\x84X\xff0\'"\xd8\r\x12\x15\x18\x1a\x1a\x1a\x00\x1a\x1a\x1a\x01\x1a\x1a\x1a\x84\x1a\x1a\x1a\xa3\x16\x19\x18\x0c\n\x15\x12\x14\n\x15\x12\x15\x0c\x15\x13\x03\x12\x17\x16\x00\x1a\x1a\x1aQ\x1a\x1a\x1a\xcb\x1a\x1a\x1aQ\x1b\x1b\x1b\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x12\x16\x1c0\'"\xd7\xca\x84X\xff\xef\x9af\xff\xed\x99e\xff\xed\x99e\xff\xef\x9af\xff\xca\x84Y\xff/\'"\xe1\x13\x16\x17+\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x1b\x1a\x1a\x19\x18\x1a\x19\xc2\x1c\x1b\x1b\xc31!%\xd71!%\xd9\x1c\x1b\x1b\xa3\x17\x19\x19s\x1a\x1a\x1a\xc8\x1a\x1a\x1aQ\x1b\x1b\x1b\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11\x15\x17\x06\x1c\x1b\x1b\xa5\x8c^B\xff\xef\x9af\xff\xef\x9af\xff\xef\x9af\xff\xef\x9af\xff\x8d_C\xff\x1b\x1b\x1a\xe2\x1a\x1a\x1a\xc0\x1a\x1a\x1a\x8a\x1a\x1a\x1a<\x15\x19\x18@- #\xdf\x8f?R\xff\xd0Tr\xff\xd0Tr\xff\x8f@S\xff+ "\xfc\x17\x19\x19r\x18\x1a\x19\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x19\x1a\x00\x15\x17\x187-%!\xdc\x8b^B\xff\xca\x84Y\xff\xca\x84Y\xff\x8b^B\xff-%!\xdb\x16\x17\x18A\x1a\x1a\x1a<\x1a\x1a\x1a\x89\x1a\x1a\x1a\xc0\x1b\x1a\x1b\xe2\x91@S\xff\xf6a\x84\xff\xf7a\x84\xff\xf7a\x84\xff\xf6a\x84\xff\x90@S\xff\x1c\x1b\x1b\xa3\x10\x17\x15\x04\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x15\x17\x187\x1c\x1b\x1b\xa70\'"\xda0\'"\xd9\x1c\x1b\x1b\xa7\x15\x17\x187\x00\x00\x00\x00\x1a\x1a\x1a\x00\x1a\x1a\x1a\x00\x13\x18\x16+0!%\xe1\xd0Ur\xff\xf6a\x84\xff\xf4`\x83\xff\xf4`\x83\xff\xf6a\x84\xff\xd0Tr\xff1!%\xd8\r\x16\x14\x18\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x1a\x1a\x00\x0f\x14\x16\x00\x12\x15\x17\x06\x0e\x13\x15\x19\r\x12\x15\x19\x12\x15\x17\x06\x0f\x14\x16\x00\x19\x1a\x1a\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\r\x16\x14\x191!%\xd8\xd0Tr\xff\xf6a\x84\xff\xf4`\x83\xff\xf4`\x83\xff\xf6a\x84\xff\xd0Tr\xff1!%\xd8\r\x16\x14\x19\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x10\x17\x15\x05\x1c\x1b\x1b\xa6\x8f@S\xff\xf6a\x84\xff\xf7a\x84\xff\xf7a\x84\xff\xf6a\x84\xff\x8f@R\xff\x1c\x1b\x1b\xa6\x10\x17\x15\x05\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x19\x1a\x19\x00\x15\x18\x177. $\xdc\x8f?R\xff\xd0Tr\xff\xd0Tr\xff\x8f?R\xff. #\xdc\x15\x18\x177\x19\x1a\x19\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x15\x18\x177\x1c\x1b\x1b\xa61!%\xd81!%\xd8\x1c\x1b\x1b\xa5\x15\x18\x177\x00\x00\x00\x00\x1a\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x1a\x1a\x00\x0f\x17\x15\x00\x12\x17\x16\x07\r\x16\x14\x1c\r\x16\x14\x1c\x12\x17\x16\x07\x0f\x17\x15\x00\x19\x1a\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xfc?\xff\xff\xf8\x1f\xff\xff\xf0\x0f\xff\xff\xe0\x07\xff\xff\xe0\x07\xff\xe1\xe0\x07\xff\xc0\x80\x07\xff\x80\x00\x07\xff\x00\x10\x03\xff\x00 !\xff\x00"p\xff\x00\x06x\x07\x80F|\x03\xc0\x08\x1e\x01\xe0\x00\x0c\x00\xfe\x10\x08\x00\xfe\x00\x00\x00\xfe\x00\x00\x00\xe0\x00\x06\x01\xc0\x00\x0c\x03\x80\x00\x08\x87\x00\x00\x11\xff\x00 #\xff\x000\x07\xff\x00\x00\x0f\xff\x80\x00\x07\xff\xc0\xe0\x07\xff\xe1\xe0\x07\xff\xff\xe0\x07\xff\xff\xf0\x0f\xff\xff\xf8\x1f\xff\xff\xfc?\xff'}

def setup():
    if input("Setup? Y for Yes, Other for No > ") == "Y":
        try:
            current_path = getcwd()
            data_in_dir = listdir()

            print("CURRENT PATH:", current_path)
            print("DATA IN DIR:", data_in_dir)

            for data in NECESSARY_DATA:
                print("Listening:", data)
                if "folders" in NECESSARY_DATA[data]:
                    for folder in NECESSARY_DATA[data]["folders"]:
                        print(" Listening", folder)
                        if folder in listdir(path.join(current_path, data)):
                            print("Found")
                        else:
                            print("NOT FOUND! Creating...")
                            mkdir(path.join(current_path, data, folder))

                if "files" in NECESSARY_DATA[data]:
                    for file in NECESSARY_DATA[data]["files"]:
                        print("Listening", file)
                        if file in listdir(path.join(current_path, data)):
                            print(" FOUND", file)
                        else:
                            print("NOT FOUND! Creating...")
                            if file == "favicon.ico":
                                with open(path.join(current_path, data, file), "wb") as fl:
                                    fl.write(FILES[file])
                            else:
                                with open(path.join(current_path, data, file), "w+", encoding="UTF-8") as fl:
                                    fl.write(FILES[file])

            print("""\033[92m
                ##########         #      ##########  ##########
                #        #       #  #     #           #
                #        #      #    #    #           #
                ##########     #      #   #           #
                #              ########   ##########  ##########
                #             #        #           #           #
                #             #        #           #           #
                #             #        #  ##########  ##########\033[0m
            """)

        except Exception as error:
            print("ERROR", error)

        input("Enter Something To Close.")
    else:
        print("No Setup.")

setup()
