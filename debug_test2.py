import sys
sys.path.insert(0, '')
from wav_server import app

app.config['TESTING'] = True
with app.test_client() as client:
    wav_content = b'RIFF....'
    # Try with 2 elements
    response = client.post('/upload_wav', data={'file': (wav_content, 'test.wav')})
    print('Status (2 elements):', response.status_code)
    print('Response:', response.data.decode())
    
    # Try with 3 elements and explicit content_type
    response2 = client.post('/upload_wav', data={'file': (wav_content, 'test.wav', 'audio/wav')}, content_type='multipart/form-data')
    print('Status (3 elements, explicit ct):', response2.status_code)
    print('Response:', response2.data.decode())
