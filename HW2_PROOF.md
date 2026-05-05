# Homework 2 Operational Proof (Requirement 6)

This document captures the OpenShift/Tekton operational evidence for Requirement 6.

## Environment

- OpenShift user: `prajanya`
- Namespace/project: `prajanya-dev`
- Cluster API: `https://api.rm2.thpm.p1.openshiftapps.com:6443`

## Tekton/Webhook Endpoints

- EventListener Route:
  - `inventory-listener-prajanya-dev.apps.rm2.thpm.p1.openshiftapps.com`
- Application Route:
  - `inventory.local` (route name: `inventory-hl24c`)

## Applied Resources

The following manifests were applied:

- `.tekton/workspace.yaml`
- `.tekton/tasks.yaml`
- `.tekton/pipeline.yaml`
- `.tekton/triggers.yaml`

## Trigger + Pipeline Evidence

Latest successful PipelineRun:

- `inventory-cd-run-hxdjr`
- Status: `Succeeded`

TaskRun outcomes for `inventory-cd-run-hxdjr`:

- `inventory-cd-run-hxdjr-clone` -> `Succeeded`
- `inventory-cd-run-hxdjr-lint` -> `Succeeded`
- `inventory-cd-run-hxdjr-test` -> `Succeeded`
- `inventory-cd-run-hxdjr-build-image` -> `Succeeded`
- `inventory-cd-run-hxdjr-deploy` -> `Succeeded`
- `inventory-cd-run-hxdjr-bdd-test` -> `Succeeded`

## Commands Used for Verification

```bash
oc project
oc get route -o wide
oc get pipelineruns.tekton.dev --sort-by=.metadata.creationTimestamp
PR=$(oc get pipelineruns.tekton.dev --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1:].metadata.name}')
oc get taskruns --selector=tekton.dev/pipelineRun=$PR
```

## Webhook Trigger Command

```bash
EL_HOST=$(oc get route inventory-listener -o jsonpath='{.spec.host}')
curl -X POST "http://${EL_HOST}" \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"ref":"refs/heads/master","repository":{"clone_url":"https://github.com/CSCI-GA-2820-SP26-001/inventory.git"}}'
```

## Notes

- Several earlier failed runs were expected during iterative hardening of Task and Pipeline parameters.
- Requirement 6 proof is satisfied by the final successful run (`inventory-cd-run-hxdjr`) with all pipeline stages succeeding end-to-end.
