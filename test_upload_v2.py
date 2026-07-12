print('START')
try:
    from s3_client import AWSS3Client
    print('IMPORTED')
    client = AWSS3Client()
    print('CLIENT_CREATED')
    with open('tmp_test_upload2.txt', 'wb') as f:
        f.write(b'hello v2')
    try:
        url = client.upload_file('tmp_test_upload2.txt', 'ignored')
        print('SUCCESS', url)
    except Exception as e:
        print('ERROR', repr(e))
except Exception as e:
    print('IMPORT ERROR', repr(e))
