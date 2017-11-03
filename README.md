# Amazon-S3-client

### This project consists of three separate implementations of an Amazon S3 Client, using features offered by boto(2.48) library.

To run the client, first, one has to generate a pair of **access and secret keys** and insert them in the specific variables **(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)**, and second, a valid **bucket name** must be chosen. Use the following command to run the client:

``` bash
python [client_name].py [path_to_directory] [valid_bucket_name]
```

- client.py => Sequential implementation. Each file in the given directory is uploaded to the server.
- multipart_client.py => The file is splitted into chunks that are sent sequentally to the service.
- pclient.py => Uses the same feature as multipart client, but as a bonus, this client uploades concurrently the chunks using python threads.
