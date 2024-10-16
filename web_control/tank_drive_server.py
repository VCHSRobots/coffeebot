import asyncio, queue
import websockets
from aiohttp import web
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
msg_queue = None

# HTML content
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tank Drive Control</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            position: fixed;
            width: 100%;
            height: 100%;
        }
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            background-color: #f0f0f0;
        }
        .container {
            display: flex;
            flex: 1;
            touch-action: none;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        .slider-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
        }
        .slider {
            -webkit-appearance: none;
            width: 60px;
            height: 200px;
            background: #d3d3d3;
            outline: none;
            writing-mode: bt-lr;
            -webkit-appearance: slider-vertical;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 25px;
            height: 25px;
            background: #4CAF50;
            cursor: pointer;
            border-radius: 50%;
        }
        .slider::-moz-range-thumb {
            width: 25px;
            height: 25px;
            background: #4CAF50;
            cursor: pointer;
            border-radius: 50%;
        }
        #status {
            text-align: center;
            padding: 10px;
            font-weight: bold;
        }
        .turn-button {
            width: 80px;
            height: 80px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 60%;
        }
    </style>
</head>
<body>
    <div id="status">Disconnected</div>
    <div class="container">
        <button id="leftTurn" class="turn-button">Left</button>
        <div class="controls">
            <div class="slider-container">
                <input type="range" min="-100" max="100" value="0" class="slider" id="leftSlider">
            </div>
            <div class="slider-container">
                <input type="range" min="-100" max="100" value="0" class="slider" id="rightSlider">
            </div>
        </div>
        <button id="rightTurn" class="turn-button">Right</button>
    </div>
    <script>
        const leftSlider = document.getElementById('leftSlider');
        const rightSlider = document.getElementById('rightSlider');
        const leftTurnBtn = document.getElementById('leftTurn');
        const rightTurnBtn = document.getElementById('rightTurn');
        const status = document.getElementById('status');
        let ws;

        function connectWebSocket() {
            console.log('Attempting to connect to WebSocket');
            ws = new WebSocket('ws://' + window.location.host + '/ws');
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                status.textContent = 'Connected';
                status.style.color = 'green';
            };

            ws.onclose = function(event) {
                console.log('WebSocket closed. Code:', event.code, 'Reason:', event.reason);
                status.textContent = 'Disconnected';
                status.style.color = 'red';
                setTimeout(connectWebSocket, 1000);
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                status.textContent = 'Error';
                status.style.color = 'red';
            };

            ws.onmessage = function(event) {
                console.log('Received message:', event.data);
            };
        }

        connectWebSocket();

        function sendValues() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                const leftValue = leftSlider.value / 100;
                const rightValue = rightSlider.value / 100;
                const data = JSON.stringify({left: leftValue, right: rightValue});
                console.log('Sending:', data);
                ws.send(data);
            }
        }

        setInterval(sendValues, 20);

        function resetSlider(slider) {
            slider.value = 0;
        }

        leftSlider.addEventListener('touchend', () => resetSlider(leftSlider));
        rightSlider.addEventListener('touchend', () => resetSlider(rightSlider));
        leftSlider.addEventListener('mouseup', () => resetSlider(leftSlider));
        rightSlider.addEventListener('mouseup', () => resetSlider(rightSlider));

        leftTurnBtn.addEventListener('click', () => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({turn: 'left'}));
            }
        });

        rightTurnBtn.addEventListener('click', () => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({turn: 'right'}));
            }
        });
    </script>
</body>
</html>
"""

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    logger.info('WebSocket connection opened')

    try:
        await ws.send_str("Connected to WebSocket server")
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                logger.info(f'Received message: {msg.data}')
                #msg_queue.put(msg.data)
                try:
                    msg_queue.put(msg.data, block=False)
                except queue.Full:
                    print("Queue is full, cannot add message")
            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f'WebSocket connection closed with exception {ws.exception()}')
    finally:
        logger.info('WebSocket connection closed')
    return ws

async def index(request):
    return web.Response(text=html, content_type='text/html')

def run_teleop_server(queue):
    global msg_queue
    msg_queue=queue
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/ws', websocket_handler)

    logger.info('Starting server')
    web.run_app(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    teleop_queue = queue.Queue(2)
    run_teleop_server(teleop_queue)