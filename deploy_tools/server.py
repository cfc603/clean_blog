from fabric.contrib.files import exists, sed
from fabric.api import cd, env, local, prefix, run, sudo


class Server(object):

    DIRECTORIES = [
        "media",
        "secrets",
        "source",
        "static",
    ]

    nginx_config_directory = "/etc/nginx"
    upstart_init_directory = "/etc/init"

    def __init__(self, **kwargs):
        self.host = kwargs.pop("host")
        self.user = kwargs.pop("user")
        self.website = kwargs.pop("website")
        self.project = kwargs.pop("project")
        self.development = kwargs.pop("development", False)
        self.set_env_variables()

    @property
    def gunicorn_config(self):
        return "{}/gunicorn-{}.conf".format(
            self.upstart_init_directory, self.website
        )

    @property
    def nginx_config(self):
        return "{}/{}".format(
            self.nginx_config_available, self.website
            )

    @property
    def nginx_config_available(self):
        return "{}/sites-available".format(
            self.nginx_config_directory
        )

    @property
    def nginx_config_enabled(self):
        return "{}/sites-enabled".format(
            self.nginx_config_directory
        )

    @property
    def settings_location(self):
        if self.development:
            return "{}.settings.staging".format(self.project)
        else:
            return "{}.settings.production".format(self.project)

    @property
    def site_directory(self):
        return "/home/{}/sites/{}".format(self.user, self.website)

    @property
    def source_directory(self):
        return "{}/source".format(self.site_directory)

    @property
    def template_directory(self):
        return "{}/deploy_tools/templates".format(
            self.source_directory
        )

    @property
    def virtualenv_directory(self):
        return "/home/{}/.virtualenvs/{}".format(
            self.user, self.website
        )

    def create_directories(self):
        for directory in self.DIRECTORIES:
            run("mkdir -p {}/{}".format(self.site_directory, directory))

    def disable_nginx_config(self, config):
        config_link = "{}/{}".format(
            self.nginx_config_enabled, config
        )
        if exists(config_link):
            sudo("rm {}".format(config_link))

    def enable_nginx_config(self):
        config_link = "{}/{}".format(
            self.nginx_config_enabled, self.website
        )
        if not exists(config_link):
            sudo(
                "ln -s {} {}".format(
                    self.nginx_config,
                    config_link
                )
            )
            sudo("service nginx reload")

    def get_latest_source(self, repo_url):
        if exists("{}/.git".format(self.source_directory)):
            run("cd {} && git pull".format(self.source_directory))
        else:
            run("git clone {} {}".format(
                repo_url, self.source_directory
            ))

    def restart_gunicorn(self):
        run("sudo {}_gunicorn state=restarted".format(self.website))

    def set_env_variables(self):
        env.host_string = self.host
        env.user = self.user
        return env

    def set_gunicorn_config(self):
        sudo("cp {}/gunicorn-upstart-template.conf {}".format(
            self.template_directory, self.gunicorn_config
        ))

        replacements = {
            "{{ site_name }}": self.website,
            "{{ user }}": self.user,
            "{{ project_name }}": self.project
        }
        for temp_var, value in replacements.iteritems():
            sed(self.gunicorn_config, temp_var, value, use_sudo=True)

        sudo("start {}".format(self.gunicorn_config))

    def set_nginx_config(self):
        sudo("cp {}/nginx.template.conf {}".format(
            self.template_directory, self.nginx_config
        ))

        sed(
            self.nginx_config,
            "{{ site_name }}",
            self.website,
            use_sudo=True
        )
        sed(self.nginx_config, "{{ user }}", self.user, use_sudo=True)

    def update_database(self):
        with cd(self.source_directory):
            with prefix("workon {}".format(self.website)):
                run("python manage.py migrate --noinput")

    def update_static_files(self):
        with cd(self.source_directory):
            with prefix("workon {}".format(self.website)):
                run("python manage.py collectstatic --noinput")
 
    def update_virtualenv(self):
        if not exists(self.virtualenv_directory):
            run("mkvirtualenv {}".format(self.website))
            
            new_line = """echo 'export DJANGO_SETTINGS_MODULE="{}"' >> {}/bin/postactivate"""
            run(new_line.format(
                self.settings_location, self.virtualenv_directory
            ))

        with prefix("workon {}".format(self.website)):
            run("pip install -r {}/requirements.txt".format(
                self.source_directory
            ))
            if self.development:
                run("pip install -r {}/dev_requirements.txt".format(
                    self.source_directory
                ))
