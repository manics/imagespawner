from dockerspawner import DockerSpawner
from kubespawner import KubeSpawner
from re import match
from traitlets import (
    HasTraits,
    List,
    Unicode,
    default,
    observe,
)
from tornado import gen


class ImageChooserMixin(HasTraits):

    dockerimages = List(
        trait=Unicode(),
        default_value=['jupyterhub/singleuser'],
        minlen=1,
        config=True,
        help="Predefined Docker images."
    )

    dockercustomimage_regex = Unicode(
        "^imagedata/jupyter-[a-z0-9:\.-]+$",
        config=True,
        help="Regular expression to validate custom image specifications"
    )

    form_template = Unicode(
        """
        <label for="dockerimage">Select a Docker image:</label>
        <select class="form-control" name="dockerimage" required autofocus>
            {option_template}
        </select>
        <label for="dockerpull">Pull image:</label>
        <input class="form-control" type="checkbox" name="dockerpull" value="yes" />
        <label for="dockercustomimage">Custom image specification:</label>
        <input class="form-control" type="text" name="dockercustomimage" />
        """,
        config=True,
        help="Form template."
    )

    option_template = Unicode(
        """
        <option value="{image}">{image}</option>
        """,
        config=True,
        help="Template for html form options."
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
        self.log.debug('formdata: %s', formdata)

        default = self.dockerimages[0]

        # formdata looks like {'dockerimage': ['jupyterhub/singleuser']}"""
        dockerimage = formdata.get('dockerimage', [default])[0]
        dockercustomimage = formdata.get('dockercustomimage')[0]
        dockerpull = formdata.get('dockerpull') == ['yes']

        if dockercustomimage:
            dockerimage = dockercustomimage
        if (dockerimage not in self.dockerimages and
            not match(self.dockercustomimage_regex, dockerimage)):
                raise ValueError('Invalid Docker image specification')

        options = {
            'dockerimage': dockerimage,
            'container_prefix': dockerimage.replace('/', '-'),
            'dockerpull': dockerpull,
        }
        return options


class DockerImageChooserSpawner(ImageChooserMixin, DockerSpawner):
    '''Enable the user to select the docker image that gets spawned.

    Define the available docker images in the JupyterHub configuration and pull
    them to the execution nodes:

    c.JupyterHub.spawner_class = DockerImageChooserSpawner
    c.DockerImageChooserSpawner.dockerimages = [
        'jupyterhub/singleuser',
        'jupyter/r-singleuser'
    ]
    '''

    @gen.coroutine
    def start(self, image=None, extra_create_kwargs=None,
              extra_start_kwargs=None, extra_host_config=None):
        # start the container
        (ip, port) = yield DockerSpawner.start(
            self, image=self.user_options['dockerimage'],
            extra_create_kwargs=extra_create_kwargs,
            extra_host_config=extra_host_config)
        return (ip, port)


class KubeImageChooserSpawner(ImageChooserMixin, KubeSpawner):
    '''Enable the user to select the docker image that gets spawned.

    Define the available docker images in the JupyterHub configuration:

    c.JupyterHub.spawner_class = KubeImageChooserSpawner
    c.KubeImageChooserSpawner.dockerimages = [
        'jupyterhub/singleuser',
        'jupyter/r-singleuser'
    ]
    '''

    @observe('user_options')
    def _update_options(self, change):
        options = change.new
        if 'dockerimage' in options:
            self.singleuser_image_spec = options['dockerimage']
        if options.get('dockerpull'):
            self.singleuser_image_pull_policy = 'Always'
        self.log.debug(
            'Updated options image_spec:%s pull_policy:%s',
            self.singleuser_image_spec, self.singleuser_image_pull_policy)


# http://jupyter.readthedocs.io/en/latest/development_guide/coding_style.html
# vim: set ai et ts=4 sw=4:
