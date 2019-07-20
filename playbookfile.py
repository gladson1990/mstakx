import time

from google.oauth2 import service_account
from google.cloud.container_v1 import ClusterManagerClient
from kubernetes import client, config, utils
import os
import yaml
import urllib2

cred_path = r'D:\Downloads\test-1cd0ae61b6e7.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path
project_id = 'peak-elevator-247105'
zone = 'us-central1-a'
cluster_id = "standard-cluster-1"
namespaces = ['staging', 'production']
guest_book_app_urls=['https://k8s.io/examples/application/guestbook/redis-master-deployment.yaml',
                     'https://k8s.io/examples/application/guestbook/redis-master-service.yaml',
                     'https://k8s.io/examples/application/guestbook/redis-slave-deployment.yaml',
                     'https://k8s.io/examples/application/guestbook/redis-slave-service.yaml',
                     'https://k8s.io/examples/application/guestbook/frontend-deployment.yaml',
                     'https://k8s.io/examples/application/guestbook/frontend-service.yaml',
                     ]


class kube_object():
    def __init__(self, project_id, zone, cluster_id):
        SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
        credentials = service_account.Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
                                                                            scopes=SCOPES)
        cluster_manager_client = ClusterManagerClient(credentials=credentials)
        cluster = cluster_manager_client.get_cluster(project_id, zone, cluster_id)
        configuration = client.Configuration()
        configuration.host = "https://" + cluster.endpoint + ":443"
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + credentials.token}
        client.Configuration.set_default(configuration)

        self.api_client = client.ApiClient()
        self.v1 = client.CoreV1Api()

    def create_ingress_nginx_controller(self):
        k8sapi = utils.create_from_yaml(self.api_client, 'ingress.yaml')

    def create_namespace(self, namespaces):
        for namespace in namespaces:
            with open('namespace.yaml') as f:
                namespace_spec = yaml.load(f)
            namespace_spec['metadata']['name'] = namespace
            self.v1.create_namespace(body=namespace_spec)

    def create_guestbook(self, namespaces, guest_book_app_urls):
        for namespace in namespaces:
            for url in guest_book_app_urls:
                json_data = yaml.load(urllib2.urlopen(url).read(), Loader=yaml.FullLoader)
                json_data['metadata']['namespace'] = namespace
                spec_file = "temp%s.yaml" % time.time()
                with open(spec_file, "w") as f:
                    yaml.dump(json_data, f)
                k8sapi = utils.create_from_yaml(self.api_client, spec_file)
                os.remove(spec_file)

    def expose_hostname(self):
        k8sapi = utils.create_from_yaml(self.api_client, 'ingress_services.yaml')

    def pod_autoscale(self):
        k8sapi = utils.create_from_yaml(self.api_client, 'autoscale.yaml')


a = kube_object(project_id,zone,cluster_id)
a.create_ingress_nginx_controller()
# a.create_namespace(namespaces)
# a.create_guestbook(namespaces,guest_book_app_urls)
# a.pod_autoscale()

