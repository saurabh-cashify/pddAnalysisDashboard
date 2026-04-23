# Deploy pddAnalysisDashboard to a Kubernetes cluster

Steps to deploy the dashboard using the **Dockerfile**, **ecr_build_push.py**, **deployment.yaml**, and **service.yaml**.

---

## Prerequisites

- **Kubernetes cluster** (e.g. Minikube for local, or EKS on AWS)
- **kubectl** configured for your cluster
- **Docker** installed and running
- **AWS CLI** configured (required only for ECR push; skip for local/Minikube)

---

## Step 1: Build the image

The **Dockerfile** in this directory builds the pdd-dashboard image.

### Option A: Push to ECR (for AWS EKS or any cluster using ECR)

1. Install dependency:
   ```bash
   pip install boto3
   ```

2. From the **pddAnalysisDashboard** directory, run the script. It will:
   - Create an ECR repository (if it does not exist)
   - Build the image using the Dockerfile
   - Log Docker into ECR and push the image

   ```bash
   cd kuldeep_lambda_model_payload/pddAnalysisDashboard

   # Default: repo `pdd-dashboard`, tag `1.0`, region from env or us-east-1
   python ecr_build_push.py

   # Or with options
   python ecr_build_push.py --repo pdd-dashboard --region us-east-1 --tag 1.0
   ```

3. Note the **image URI** printed at the end (e.g. `123456789012.dkr.ecr.us-east-1.amazonaws.com/pdd-dashboard:1.0`).

4. Update **deployment.yaml**: set `image` to that ECR URI and `imagePullPolicy: Always`:
   ```yaml
   containers:
     - name: pdd-dashboard-container
       image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/pdd-dashboard:1.0
       imagePullPolicy: Always
   ```

### Option B: Local / Minikube (no ECR)

1. Use Minikube’s Docker so the cluster can use the image:
   ```bash
   eval $(minikube docker-env)
   cd kuldeep_lambda_model_payload/pddAnalysisDashboard
   docker build -t pdd-dashboard:1.0 .
   ```

2. Keep **deployment.yaml** as-is (`image: pdd-dashboard:1.0`, `imagePullPolicy: Never`).

---

## Step 2: Deploy to Kubernetes

Run from the **repository root** (or adjust paths).

1. Apply the **Deployment** (creates pods from the Dockerfile image):
   ```bash
   kubectl apply -f kuldeep_lambda_model_payload/pddAnalysisDashboard/deployment.yaml
   ```

2. Apply the **Service** (exposes the deployment, e.g. NodePort 30080):
   ```bash
   kubectl apply -f kuldeep_lambda_model_payload/pddAnalysisDashboard/service.yaml
   ```

---

## Step 3: Verify and open in browser

1. Check that pods are running and ready:
   ```bash
   kubectl get pods -l app=pdd-dashboard
   kubectl get svc pdd-dashboard-service
   ```

2. Open the dashboard:
   - **NodePort (e.g. Minikube):**  
     `http://<NODE_IP>:30080`  
     Minikube: `minikube service pdd-dashboard-service --url` or `http://$(minikube ip):30080`
   - **LoadBalancer (e.g. EKS):**  
     Use the EXTERNAL-IP or hostname from `kubectl get svc pdd-dashboard-service`
   - **Port-forward (any cluster):**  
     `kubectl port-forward svc/pdd-dashboard-service 8050:80`  
     Then open: **http://localhost:8050**

---

## Summary order

| Step | What |
|------|------|
| 1    | Build image: **Dockerfile** (via `docker build` or **ecr_build_push.py** for ECR) |
| 2    | Deploy workload: **deployment.yaml** |
| 3    | Expose traffic: **service.yaml** |
| 4    | Open in browser using NodePort, LoadBalancer, or port-forward |
