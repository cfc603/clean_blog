from fabric.contrib.files import exists, sed
from fabric.api import sudo


class Certbot(object):

    download_link = "https://dl.eff.org/certbot-auto"

    def __init__(self, **kwargs):
        self.template_directory = kwargs.pop("template_directory")
        self.url = kwargs.pop("url")

    @property
    def certbot_program(self):
        certbot_dir = "/usr/local/certbot"
        certbot = "{}/certbot-auto".format(certbot_dir)
        
        # download if it doesn't exist
        if not exists("{}/certbot-auto".format(certbot_dir)):
            sudo(
                "wget {} -P {}".format(
                    self.download_link, certbot_dir
                )
            )
            sudo("chmod a+x {}".format(certbot))
        
        return certbot

    @property
    def dhparam_file(self):
        file = "/etc/ssl/certs/dhparam.pem"

        if not exists(file):
            sudo("openssl dhparam -out {} 2048".format(file))

        return file

    @property
    def nginx_snippet_directory(self):
        directory = "/etc/nginx/snippets"

        if not exists(directory):
            sudo("mkdir -p {}".format(directory))

        return directory

    @property
    def root_directory(self):
        directory = "/var/www/{}".format(self.url)
        
        if not exists(directory):
            sudo("mkdir -p {}/.well-known".format(directory))
        
        return directory

    @property
    def ssl_domain_file(self):
        file = "ssl-{}.conf".format(self.url)

        if not exists(file):
            sudo(
                "cp {}/ssl-domain.template.conf {}/{}".format(
                    self.template_directory,
                    self.nginx_snippet_directory,
                    file
                )
            )
            sed(file, "DOMAIN", self.url, use_sudo=True)

        return file

    @property
    def ssl_params_file(self):
        file = "ssl-params.conf"

        if not exists(file):
            sudo(
                "cp {}/ssl-params.template.conf {}/{}".format(
                    self.template_directory,
                    self.nginx_snippet_directory,
                    file
                )
            )

        return file

    def get_certificate(self):
        sudo(
            "{} certonly -w {} -d {} --agree-tos".format(
                self.certbot_program, self.root_directory, self.url
            )
        )

    def set_renewal_cron(self):
        file = "/etc/cron.d/crontab-renewal"

        if not exists(file):
            sudo(
                "cp {}/certbot-renewal.template {}".format(
                    self.template_directory, file
                )
            )
            sudo("chmod +x {}".format(file))
