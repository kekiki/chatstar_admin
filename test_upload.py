from s3_client import AWSS3Client

client = AWSS3Client()

with open('tmp_test_upload.txt', 'wb') as f:
    f.write(b'hello from smoke test')

try:
    url = client.upload_file('tmp_test_upload.txt', 'ignored')
    print('SUCCESS', url)
except Exception as e:
    print('ERROR', repr(e))
