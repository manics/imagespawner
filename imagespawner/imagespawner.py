from kubespawner import KubeSpawner
from traitlets import default, Unicode, List
from tornado import gen


class KubeImageChooserSpawner(KubeSpawner):
    '''Enable the user to select the docker image that gets spawned.

    Define the available docker images in the JupyterHub configuration:

    c.JupyterHub.spawner_class = KubeImageChooserSpawner
    c.KubeImageChooserSpawner.dockerimages = [
        'jupyterhub/singleuser',
        'jupyter/r-singleuser'
    ]
    '''
    
    dockerimages = List(
        trait = Unicode(),
        default_value = ['jupyterhub/singleuser'],
        minlen = 1,
        config = True,
        help = "Docker images that have been pre-pulled to the execution host."
    )
    form_template = Unicode("""
        <label for="dockerimage">Select a Docker image:</label>
        <select class="form-control" name="dockerimage" required autofocus>
            {option_template}
        </select>""",
        config = True, help = "Form template."
    )
    option_template = Unicode("""
        <option value="{image}">{image}</option>""",
        config = True, help = "Template for html form options."
    )

    @default('options_form')
    def _options_form(self):
        """Return the form with the drop-down menu."""
        options = ''.join([
            self.option_template.format(image=di) for di in self.dockerimages
        ])
        return self.form_template.format(option_template=options)

    def options_from_form(self, formdata):
        """Parse the submitted form data and turn it into the correct
           structures for self.user_options."""

        default = self.dockerimages[0]

        # formdata looks like {'dockerimage': ['jupyterhub/singleuser']}"""
        dockerimage = formdata.get('dockerimage', [default])[0]

        # Don't allow users to input their own images
        if dockerimage not in self.dockerimages: dockerimage = default

        options = {
            'container_image': dockerimage,
            'container_prefix': dockerimage.replace('/', '-'),
        }
        return options

    @gen.coroutine
    def start(self, *args, **kwargs):
        # TODO: Override _expand_user_properties() to include
        # container_prefix?
        self.singleuser_image_spec = self.user_options['container_image']

        # start the container
        ip, port = yield super(KubeImageChooserSpawner, self).start(
            *args, **kwargs)
        return ip, port


# http://jupyter.readthedocs.io/en/latest/development_guide/coding_style.html
# vim: set ai et ts=4 sw=4:
