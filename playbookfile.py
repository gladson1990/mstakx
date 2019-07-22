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
cluster_id = "standard-cluster-3"
namespaces = ['staging', 'production']
guest_book_app_urls = ['https://k8s.io/examples/application/guestbook/redis-master-deployment.yaml',
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
        print "Creating nginx controller"
        k8sapi = utils.create_from_yaml(self.api_client, 'nginx.yaml')
        time.sleep(20)
        k8sapi = utils.create_from_yaml(self.api_client, 'ingres.yaml')
        return k8sapi

    def create_namespace(self, namespaces):
        for namespace in namespaces:
            print "cReating namespace %s" % namespace
            with open('namespace.yaml') as f:
                namespace_spec = yaml.load(f)
            namespace_spec['metadata']['name'] = namespace
            self.v1.create_namespace(body=namespace_spec)

    def create_guestbook(self, namespaces, guest_book_app_urls):
        apis = []
        for namespace in namespaces:
            for url in guest_book_app_urls:
                print "Creating kubectl %s in %s namespace " % (url, namespace)
                json_data = yaml.load(urllib2.urlopen(url).read(), Loader=yaml.FullLoader)
                json_data['metadata']['namespace'] = namespace
                spec_file = "temp%s.yaml" % time.time()
                with open(spec_file, "w") as f:
                    yaml.dump(json_data, f)
                k8sapi = utils.create_from_yaml(self.api_client, spec_file)
                apis.append(k8sapi)
                os.remove(spec_file)
        return apis

    def expose_hostname(self):
        print "Expose hostname "
        k8sapi = utils.create_from_yaml(self.api_client, 'ingress_services.yaml')
        return k8sapi

    def pod_autoscale(self):
        print "Autoscaling the pods"
        k8sapi = utils.create_from_yaml(self.api_client, 'autoscale.yaml')
        return k8sapi


if __name__ == "__main__":
    try:
        a = kube_object(project_id, zone, cluster_id)
        ingnx_controller = a.create_ingress_nginx_controller()
        namespace = a.create_namespace(namespaces)
        application = a.create_guestbook(namespaces, guest_book_app_urls)
        hostname_ingres = a.expose_hostname()
        autoscale = a.pod_autoscale()
    except Exception as e:
        print "failed due to %s" % e
        import pdb
        pdb.set_trace()
