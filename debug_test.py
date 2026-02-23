import sys
sys.path.insert(0, '')
from wav_server import app

app.config['TESTING'] = True
with app.test_client() as client:
    wav_content = b'RIFF....'
    response = client.post('/upload_wav', data={'file': (wav_content, 'test.wav', 'audio/wav')})
    print('Status:', response.status_code)
    print('Response:', response.data.decode())
