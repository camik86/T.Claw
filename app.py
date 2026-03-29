import json
from flask import Flask, render_template, request, jsonify, Response
from config import config
from agent import agent

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', configured=agent.is_configured())


@app.route('/settings')
def settings():
    return render_template('settings.html', config=config)


@app.route('/api/save-config', methods=['POST'])
def save_config():
    data = request.json
    config.api_key = data.get('api_key', '')
    config.endpoint_id = data.get('endpoint_id', '')
    config.model = data.get('model', 'doubao-seed-2-0-pro')
    agent.update_config()
    return jsonify({'success': True})


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    stream = data.get('stream', False)
    
    if not user_input:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        if stream:
            return Response(
                generate_stream(agent, user_input),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
        else:
            response = agent.chat(user_input, stream=False)
            return jsonify({'response': response})
    except Exception as e:
        if stream:
            return f"data: {json.dumps({'error': str(e)})}\n\n", 500
        return jsonify({'error': str(e)}), 500


def generate_stream(agent_instance, user_input):
    try:
        response = agent_instance.chat(user_input, stream=True)
        yield f"data: {json.dumps({'response': response, 'done': True})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12101, debug=True)
