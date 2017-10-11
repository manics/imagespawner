# imagespawner

KubeSpawner with image selection

Let JupyterHub users choose which docker image they want to spawn.

In your JupyterHub configuration:

```
c.JupyterHub.spawner_class = KubeImageChooserSpawner
c.KubeImageChooserSpawner.dockerimages = [
    'jupyterhub/singleuser',
    'jupyter/r-singleuser'
]
```

Requirements:
- https://github.com/jupyterhub/kubespawner
