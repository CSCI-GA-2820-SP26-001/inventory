# Tekton CD Runbook (OpenShift)

This runbook helps you deploy and validate the Requirement 6 pipeline quickly.

## 1) Apply Order

From the repository root:

```bash
oc apply -f .tekton/workspace.yaml
oc apply -f .tekton/tasks.yaml
oc apply -f .tekton/pipeline.yaml
oc apply -f .tekton/triggers.yaml
```

Confirm resources:

```bash
oc get pvc pipeline-workspace
oc get task lint test build-image deploy bdd-test
oc get pipeline inventory-cd-pipeline
oc get el inventory-listener
oc get route inventory-listener
```

## 2) Configure Trigger Defaults

Before first run, edit `.tekton/triggers.yaml` defaults in `TriggerTemplate`:

- `base-url` -> your app public route, e.g. `http://inventory-route-<ns>.apps.<cluster-domain>`
- `image` -> your OpenShift internal registry image, e.g. `image-registry.openshift-image-registry.svc:5000/<namespace>/inventory:latest`
- `deployment-name` / `container-name` if not `inventory`

Re-apply after edits:

```bash
oc apply -f .tekton/triggers.yaml
```

## 3) GitHub Webhook Setup

Get EventListener host:

```bash
EL_HOST=$(oc get route inventory-listener -o jsonpath='{.spec.host}')
echo "$EL_HOST"
```

In GitHub repo settings:

- **Payload URL**: `http://$EL_HOST`
- **Content type**: `application/json`
- **Events**: Just the **Push** event
- **Secret**: optional (if used, add matching interceptor secret validation later)
- **Active**: enabled

## 4) Manual Trigger Test Payload

You can simulate a push event to verify the listener:

```bash
curl -i -X POST "http://$EL_HOST" \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{
    "ref": "refs/heads/master",
    "repository": {
      "clone_url": "https://github.com/CSCI-GA-2820-SP26-001/inventory.git"
    }
  }'
```

Check that a PipelineRun was created:

```bash
oc get pipelineruns --sort-by=.metadata.creationTimestamp
```

## 5) Observe First PipelineRun

Using Tekton CLI (`tkn`):

```bash
tkn pipelinerun list
tkn pipelinerun logs -f <pipelinerun-name>
```

Using `oc` only:

```bash
oc describe pipelinerun <pipelinerun-name>
oc get taskrun
oc describe taskrun <taskrun-name>
oc logs pod/<taskrun-pod-name> -c step-<step-name>
```

## 6) Common Troubleshooting

- **No PipelineRun created**
  - Verify EventListener route exists and webhook payload URL is correct.
  - Check EventListener logs:
    ```bash
    oc logs deploy/el-inventory-listener
    ```

- **Image build/push fails**
  - Confirm OpenShift service account has permission to push to target image stream/namespace.
  - Verify `image` parameter path points to the correct registry/namespace.

- **Deploy task fails**
  - Confirm deployment/container names match Kubernetes manifests.
  - Validate manifests:
    ```bash
    oc apply --dry-run=client -R -f k8s/
    ```

- **BDD task fails**
  - Confirm `base-url` resolves and route is accessible from cluster task pods.
  - Check app health endpoint:
    ```bash
    curl -sS "$BASE_URL/health"
    ```

## 7) Fast Re-run

To retrigger quickly without a code change, use GitHub webhook redelivery or re-send the curl payload from section 4.
