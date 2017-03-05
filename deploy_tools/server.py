from fabric.contrib.files import exists, sed
from fabric.api import cd, env, local, prefix, run, sudo

from .certbot import Certbot


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
        self.url = kwargs.pop("url")
        self.project = kwargs.pop("project")
        self.development = kwargs.pop("development", False)
        self.set_env_variables()
        self.certbot = Certbot(**{
                "template_directory": self.template_directory,
                "url": self.url,
            })

    @property
    def gunicorn_config(self):
        return "{}/gunicorn-{}.conf".format(
            self.upstart_init_directory, self.url
        )

    @property
    def nginx_config(self):
        return "{}/{}".format(
            self.nginx_config_available, self.url
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
        return "/home/{}/sites/{}".format(self.user, self.url)

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
            self.user, self.url
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
            self.nginx_config_enabled, self.url
        )
        if not exists(config_link):
            sudo(
                "ln -s {} {}".format(
                    self.nginx_config,
                    config_link
                )
            )
            self.reload_nginx()

    def get_latest_source(self, repo_url):
        if exists("{}/.git".format(self.source_directory)):
            run("cd {} && git pull".format(self.source_directory))
        else:
            run("git clone {} {}".format(
                repo_url, self.source_directory
            ))

    def reload_gunicorn(self):
        run("sudo reload gunicorn-{}".format(self.url))

    def reload_nginx(self):
        sudo("service nginx reload")

    def secure_domain(self):
        self.reload_nginx()
        self.certbot.get_certificate()
        self.certbot.generate_dhparam_file()
        self.set_nginx_config(True)
        self.reload_nginx()
        self.certbot.set_renewal_cron()

    def set_env_variables(self):
        env.host_string = self.host
        env.user = self.user
        return env

    def set_gunicorn_config(self):
        replacements = {
            "SITE_NAME": self.url,
            "USER": self.user,
            "PROJECT_NAME": self.project
        }

        self.set_template(
            "{}/gunicorn-upstart.template.conf".format(
                self.template_directory
            ),
            self.gunicorn_config,
            replacements
        )

        sudo("start gunicorn-{}".format(self.url))

    def set_nginx_config(self, secure=False):
        if not secure:
            template = "{}/nginx.template.conf"
        else:
            template = "{}/nginx-secure.template.conf"
        template = template.format(self.template_directory)

        replacements = {
            "SITE_NAME": self.url,
            "USER": self.user,
            "ROOT_DIRECTORY": self.certbot.root_directory,
        }
        if secure:
            replacements["SSL_DOMAIN_FILE"] = self.certbot.ssl_domain_file
            replacements["SSL_PARAMS_FILE"] = self.certbot.ssl_params_file

        self.set_template(
            template, self.nginx_config, replacements
        )

    def set_template(self, template, location, replacements):
        if not exists(location):
            sudo("cp {} {}".format(template, location))

        for temp_var, value in replacements.iteritems():
            sed(location, temp_var, value, use_sudo=True)

    def update_database(self):
        with cd(self.source_directory):
            with prefix("workon {}".format(self.url)):
                run("python manage.py migrate --noinput")

    def update_static_files(self):
        with cd(self.source_directory):
            with prefix("workon {}".format(self.url)):
                run("python manage.py collectstatic --noinput")
 
    def update_virtualenv(self):
        if not exists(self.virtualenv_directory):
            run("mkvirtualenv {}".format(self.url))
            
            new_line = """echo 'export DJANGO_SETTINGS_MODULE="{}"' >> {}/bin/postactivate"""
            run(new_line.format(
                self.settings_location, self.virtualenv_directory
            ))

        with prefix("workon {}".format(self.url)):
            run("pip install -r {}/requirements.txt".format(
                self.source_directory
            ))
            if self.development:
                run("pip install -r {}/dev_requirements.txt".format(
                    self.source_directory
                ))
