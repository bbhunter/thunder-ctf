from flask import render_template
def main(request):
	from googleapiclient import discovery
	import google.auth
	import os
	

	
	# Set the project ID
	PROJECT_ID = os.environ['GCP_PROJECT']
	FUNCTION_REGION = os.environ['FUNCTION_REGION']
	NONCE = os.environ.get('NONCE', 'Specified environment variable is not set.')
	RESOURCE_PREFIX = os.environ.get('RESOURCE_PREFIX', 'Specified environment variable is not set.')
	LEVEL_NAME = os.environ.get('LEVEL_NAME', 'Specified environment variable is not set.')

	# Get credential of cloud function account
	credentials, project_id = google.auth.default()

	#score function url
	surl  = f'https://{FUNCTION_REGION}-{PROJECT_ID}.cloudfunctions.net/scores-f-{NONCE}'

	#Build instance REST API python object
	instance_api = discovery.build('compute', 'v1', credentials=credentials)
	err=[]
	resources=[]
	url=f'https://europe-west1-{PROJECT_ID}.cloudfunctions.net/{RESOURCE_PREFIX}-f-check-{NONCE}'
	try:
		instances= instance_api.instances().list(zone="us-east5-c", project=PROJECT_ID).execute()["items"]
		for instance in instances:
			if instance["name"].startswith(RESOURCE_PREFIX):
				resources.append(f'Instance: {instance["name"]}({instance["machineType"]})')
	except Exception as e:
		resources.append("Instance: Insufficient privilege!")
		err.append(str(e))
	if len(err)!=0:
		return render_template(f'{RESOURCE_PREFIX}-access.html', resources=resources, url=url, err=err,prefix=RESOURCE_PREFIX,level_name=LEVEL_NAME, nonce=NONCE)

	#Build storage REST API python object
	storage_api = discovery.build('storage', 'v1', credentials=credentials)
	
	try:
		buckets = storage_api.buckets().list(project=PROJECT_ID).execute()["items"]
		for bucket in buckets:
			if bucket["name"].startswith(RESOURCE_PREFIX):
				resources.append(f'Bucket: {bucket["name"]}')
	except Exception as e:
		resources.append('Bucket: Insufficient privilege!')
		err.append(str(e))
	
	
	
	
	return render_template(f'{RESOURCE_PREFIX}-access.html', resources=resources, url=url, err=err,prefix=RESOURCE_PREFIX,level_name=LEVEL_NAME, nonce=NONCE, surl=surl)

	

