import sys
from io import BytesIO
sys.path.insert(0, '')
from wav_server import app

app.config['TESTING'] = True
with app.test_client() as client:
    wav_content = b'RIFF....'
    # Try with BytesIO
    file_obj = BytesIO(wav_content)
    response = client.post('/upload_wav', data={'file': (file_obj, 'test.wav')})
    print('Status (BytesIO):', response.status_code)
    print('Response:', response.data.decode())
    
    # Try with BytesIO and 3 elements
    file_obj2 = BytesIO(wav_content)
    response2 = client.post('/upload_wav', data={'file': (file_obj2, 'test.wav', 'audio/wav')})
    print('Status (BytesIO, 3 elements):', response2.status_code)
    print('Response:', response2.data.decode())
