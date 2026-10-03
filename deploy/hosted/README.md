# LazyEdit Hosted

An invite-only registration service with an isolated LazyEdit + AutoPublish
workspace for each user. Browser profiles, media, settings and queues persist
in that user's volumes. No Pi is required for this deployment.

Read the complete [setup, security and operations guide](../../references/2026-10-03-hosted-multiuser-docker.md)
before starting it. The deployment is separate from the existing live owner
Studio/Pi and does not import their accounts or secrets.

Images built from this directory's Dockerfile:

- `gateway`: public account portal and authenticated workspace routing;
- `provisioner`: private controller, no network listener, fixed Docker template;
- `workspace`: existing editing backend, Studio UI, publisher and private browser.

Each workspace also receives its own PostgreSQL container. The gateway does
not have the Docker socket. Start the generated control Compose file once;
invitations and provisioning then use the normal registration flow.
