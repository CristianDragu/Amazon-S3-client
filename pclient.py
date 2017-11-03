import boto
import sys
import datetime
import math
import threading
from boto.s3.key import Key
from os import listdir, stat
from os.path import isfile, join
from argparse import ArgumentParser
from filechunkio import FileChunkIO

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

def percent_cb(complete, total):
	sys.stdout.write('.')
	sys.stdout.flush()

def upload_chunk(path, offset, bytes, count, mp):
	with FileChunkIO(path, 'r', offset = offset, bytes = bytes) as fp:
		mp.upload_part_from_file(fp, part_num = count + 1, cb = percent_cb, num_cb = 10)

def send_files(access_key, secret_key, path, bucket_name):
	conn = boto.connect_s3(access_key, secret_key)
	bucket = conn.lookup(bucket_name)

	if bucket:
		for key in bucket.list():
			key.delete()
	else:
		conn.create_bucket(bucket_name)

	files = []
	files_path = []

	for f in listdir(path):
		if isfile(join(path, f)):
			files.append(f)
			files_path.append(join(path, f))

	for i in range(len(files)):
		print 'Uploading %s to Amazon S3 bucket %s' % (files[i], bucket_name)

		file_size = stat(files_path[i]).st_size # in KB
		elapsed_time = 0

		# if the file size is lower than 10 MB, proceed with basic upload
		if (file_size / 1024.0 / 1024.0 < 10.0):
			k = Key(bucket)
			k.key = files[i]

			start_time = datetime.datetime.now()
			k.set_contents_from_filename(files_path[i], cb = percent_cb, num_cb = 10)
			elapsed_time = datetime.datetime.now() - start_time
		else:
			multipart = bucket.initiate_multipart_upload(files[i])
			chunk_size = 10485760 # 10 MB
			chunk_count = int(math.ceil(file_size / float(chunk_size)))
			threads = []
			for c in range(chunk_count):
				offset = c * chunk_size
				bytes = min(chunk_size, file_size - offset)
				threads.append(threading.Thread(target = upload_chunk, args = (files_path[i], offset, bytes, c, multipart)))
			start_time = datetime.datetime.now()
			for thread in threads:
				thread.start()
			for thread in threads:
				thread.join()
			multipart.complete_upload()
			elapsed_time = datetime.datetime.now() - start_time

		print "Time elapsed: {}".format(elapsed_time)

if __name__ == '__main__':

	parser = ArgumentParser()
	parser.add_argument("--path", default = "img", help = "Path to files for upload. Default path is '.'.")
	parser.add_argument("--bucket_name", default = "your-bucket-name", help = "Default bucket.")
	args = parser.parse_args()

	send_files(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, args.path, args.bucket_name)
