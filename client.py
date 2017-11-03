import boto
import sys
import datetime
from boto.s3.key import Key
from os import listdir
from os.path import isfile, join
from argparse import ArgumentParser

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

def percent_cb(complete, total):
	sys.stdout.write('.')
	sys.stdout.flush()

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

		k = Key(bucket)
		k.key = files[i]

		start_time = datetime.datetime.now()
		k.set_contents_from_filename(files_path[i], cb = percent_cb, num_cb = 10)
		elapsed_time = datetime.datetime.now() - start_time

		print "Time elapsed: {}".format(elapsed_time)

if __name__ == '__main__':

	parser = ArgumentParser()
	parser.add_argument("--path", default = "img", help = "Path to files for upload. Default path is '.'.")
	parser.add_argument("--bucket_name", default = "cristi-dragu-big-data-bucket", help = "Default bucket.")
	args = parser.parse_args()

	send_files(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, args.path, args.bucket_name)
