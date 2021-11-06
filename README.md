kubectl get service

kubectl get deployment

kubectl get ingress

kubectl get hpa



# Task A3

## Steps to reproduce solution

### 1. Ensure Docker desktop is configured with Kubernetes

- Go to settings &#8594; Kubernetes
- Check the option 'Enable Kubernetes'
- Click 'Apply & Restart'

### 2. Expose pods to the cluster

Pods are configured in the yaml file. The image used is nginx. Create Deployment by running the following command:

```
$ kubectl apply -f ./run-my-nginx.yaml
deployment.apps/my-nginx created
```

After a few moments, the Deployments should be ready. You can check running Deployments by executing the command:

```
$ kubectl get deployments
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
my-nginx   2/2     2            2           23m
```

In this Deployment, we have specified 2 replicas in `run-my-nginx.yaml`. You can check running Pods too by running:

```
$ kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
my-nginx-5b56ccd65f-4sv4j   1/1     Running   0          9m26s
my-nginx-5b56ccd65f-nhrvb   1/1     Running   0          9m26s
```

### 3. Expose the Deployment

This is to create a Service for `my-nginx` Deployment.

```
$ kubectl expose deployment my-nginx
service/my-nginx exposed
```

```
$ kubectl get service
NAME         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP   5d19h
my-nginx     ClusterIP   10.96.195.245    <none>        80/TCP    4s
```

## 4. Prerequisite: Install Ingress Controller

Following this link: https://kubernetes.github.io/ingress-nginx/deploy/

First, we need to install NGINX Ingress Controller for Ingress to work. Before running the following installation command, make sure Kubernetes is enabled at Docker settings.

```
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml
namespace/ingress-nginx created
serviceaccount/ingress-nginx created
configmap/ingress-nginx-controller created
clusterrole.rbac.authorization.k8s.io/ingress-nginx created
clusterrolebinding.rbac.authorization.k8s.io/ingress-nginx created
role.rbac.authorization.k8s.io/ingress-nginx created
rolebinding.rbac.authorization.k8s.io/ingress-nginx created
service/ingress-nginx-controller-admission created
service/ingress-nginx-controller created
deployment.apps/ingress-nginx-controller created
ingressclass.networking.k8s.io/nginx created
validatingwebhookconfiguration.admissionregistration.k8s.io/ingress-nginx-admission created
serviceaccount/ingress-nginx-admission created
clusterrole.rbac.authorization.k8s.io/ingress-nginx-admission created
clusterrolebinding.rbac.authorization.k8s.io/ingress-nginx-admission created
role.rbac.authorization.k8s.io/ingress-nginx-admission created
rolebinding.rbac.authorization.k8s.io/ingress-nginx-admission created
job.batch/ingress-nginx-admission-create created
job.batch/ingress-nginx-admission-patch created
```

A few pods should start at `ingress-nginx` namespace.

```
$ kubectl get pods --namespace=ingress-nginx
NAME                                        READY   STATUS      RESTARTS   AGE
ingress-nginx-admission-create-7mhhk        0/1     Completed   0          54s
ingress-nginx-admission-patch-k9zjw         0/1     Completed   1          54s
ingress-nginx-controller-5c8d66c76d-6zb2h   1/1     Running     0          54s
```

With Ingress Controller set up, we can now apply the Ingress resource.

## 2. Apply Ingress

`ingress-nginx.yaml` file is configured with ingress rules and sticky session, where the backend Service is `my-nginx` created previously. Run the following command to apply the Ingress:

```
$ kubectl apply -f ./ingress-nginx.yaml
ingress.networking.k8s.io/ingress-nginx created
```

```
$ kubectl get ingress
NAME            CLASS   HOSTS              ADDRESS   PORTS   AGE
ingress-nginx   nginx   demo.localdev.me             80      3s
```

Next, forward the local port to the Ingress controller. This needs to be done for local testing, as `demo.localdev.me` is not a deployed endpoint.

```
$ kubectl port-forward --namespace=ingress-nginx service/ingress-nginx-controller 8080:80
Forwarding from 127.0.0.1:8080 -> 80
Forwarding from [::1]:8080 -> 80
```

To test out sticky sessions, keep the above terminal running and test it out in browser.

- Access `http://demo.localdev.me:8080/` and check for cookies. `INGRESS_COOKIE` will be set and it will not change after refreshing the page.

![alt text](./nginx1.png)

- Test it out in another browser to see a different cookie value, which also does not change after refreshing the page.

![alt text](./nginx2.png)


### Additional Reading: Ingress vs Ingress Controller

In order for the Ingress resource to work, the cluster must have an ingress controller running.

Ingress should be the rules for the traffic, which indicate the destination of a request will go through in the cluster. Ingress Controller is the implementation for the Ingress.

## Horizontal Pod Autoscaler