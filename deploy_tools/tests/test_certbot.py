from django.test import TestCase

from mock import call, patch

from deploy_tools.certbot import Certbot


class CertbotTest(TestCase):

    def certbot_for_tests(self, **kwargs):
        data = {
            "template_directory": "test/template/dir",
            "url": "test_url.com",
        }

        for key, value in kwargs.iteritems():
            data[key] = value

        return Certbot(**data)

    def test_init(self):
        certbot = self.certbot_for_tests()

        self.assertEqual(
            certbot.template_directory, "test/template/dir"
        )
        self.assertEqual(certbot.url, "test_url.com")
        self.assertEqual(
            certbot.download_link, "https://dl.eff.org/certbot-auto"
        )

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_certbot_program_if_not_exists(self, sudo, exists):
        exists.return_value = False

        certbot = self.certbot_for_tests()
        certbot_program = certbot.certbot_program

        exists.assert_called_once_with(
            "/usr/local/certbot/certbot-auto"
        )
        sudo.assert_has_calls([
            call(
                "wget {} -P /usr/local/certbot".format(
                    certbot.download_link
                )
            ),
            call("chmod a+x /usr/local/certbot/certbot-auto")
        ])
        self.assertEqual(
            certbot_program, "/usr/local/certbot/certbot-auto"
        )

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_certbot_program_if_exists(self, sudo, exists):
        exists.return_value = True

        certbot = self.certbot_for_tests()
        certbot_program = certbot.certbot_program

        exists.assert_called_once_with(
            "/usr/local/certbot/certbot-auto"
        )
        sudo.assert_not_called()
        self.assertEqual(
            certbot_program, "/usr/local/certbot/certbot-auto"
        )

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_nginx_snippet_directory_if_not_exists(self, sudo, exists):
        exists.return_value = False
        directory = "/etc/nginx/snippets"

        certbot = self.certbot_for_tests()
        nginx_snippet_directory = certbot.nginx_snippet_directory

        exists.assert_called_once_with(directory)
        sudo.assert_called_once_with("mkdir -p {}".format(directory))
        self.assertEqual(nginx_snippet_directory, directory)

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_nginx_snippet_directory_if_exists(self, sudo, exists):
        exists.return_value = True
        directory = "/etc/nginx/snippets"

        certbot = self.certbot_for_tests()
        nginx_snippet_directory = certbot.nginx_snippet_directory

        exists.assert_called_once_with(directory)
        sudo.assert_not_called()
        self.assertEqual(nginx_snippet_directory, directory)

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_root_directory_if_not_exists(self, sudo, exists):
        exists.return_value = False
        directory = "/var/www/test_url.com"

        certbot = self.certbot_for_tests()
        root_directory = certbot.root_directory

        exists.assert_called_once_with(directory)
        sudo.assert_called_once_with(
            "mkdir -p {}/.well-known".format(directory)
        )
        self.assertEqual(root_directory, directory)

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_root_directory_if_exists(self, sudo, exists):
        exists.return_value = True
        directory = "/var/www/test_url.com"

        certbot = self.certbot_for_tests()
        root_directory = certbot.root_directory

        exists.assert_called_once_with(directory)
        sudo.assert_not_called()
        self.assertEqual(root_directory, directory)

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    @patch("deploy_tools.certbot.Certbot.nginx_snippet_directory")
    @patch("deploy_tools.certbot.sed")
    def test_ssl_domain_file_if_not_exists(self, sed, snip_dir, sudo, exists):
        exists.return_value = False
        file = "ssl-test_url.com.conf"
        file_path = "{}/{}".format(snip_dir, file)

        certbot = self.certbot_for_tests()
        ssl_domain_file = certbot.ssl_domain_file

        exists.assert_called_once_with(file)
        sudo.assert_called_once_with(
            "cp test/template/dir/ssl-domain.template.conf {}".format(
                file_path
            )
        )
        sed.assert_called_once_with(
            file_path, "DOMAIN", "test_url.com", use_sudo=True
        )
        self.assertEqual(ssl_domain_file, file)

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    @patch("deploy_tools.certbot.sed")
    def test_ssl_domain_file_if_exists(self, sed, sudo, exists):
        exists.return_value = True
        file = "ssl-test_url.com.conf"

        certbot = self.certbot_for_tests()
        ssl_domain_file = certbot.ssl_domain_file

        exists.assert_called_once_with(file)
        sudo.assert_not_called()
        sed.assert_not_called()
        self.assertEqual(ssl_domain_file, file)

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    @patch("deploy_tools.certbot.Certbot.nginx_snippet_directory")
    def test_ssl_params_file_if_not_exists(self, snip_dir, sudo, exists):
        exists.return_value = False
        file = "ssl-params.conf"

        certbot = self.certbot_for_tests()
        ssl_params_file = certbot.ssl_params_file

        exists.assert_called_once_with(file)
        sudo.assert_called_once_with(
            "cp test/template/dir/ssl-params.template.conf {}/{}".format(
                snip_dir,
                file
            )
        )
        self.assertEqual(ssl_params_file, file)

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_ssl_params_file_if_exists(self, sudo, exists):
        exists.return_value = True
        file = "ssl-params.conf"

        certbot = self.certbot_for_tests()
        ssl_params_file = certbot.ssl_params_file

        exists.assert_called_once_with(file)
        sudo.assert_not_called()
        self.assertEqual(ssl_params_file, file)

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_generate_dhparam_file_if_not_exists(self, sudo, exists):
        exists.return_value = False
        file = "/etc/ssl/certs/dhparam.pem"

        certbot = self.certbot_for_tests()
        certbot.generate_dhparam_file()

        exists.assert_called_once_with(file)
        sudo.assert_called_once_with(
            "openssl dhparam -out {} 2048".format(file)
        )

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_generate_dhparam_file_if_exists(self, sudo, exists):
        exists.return_value = True
        file = "/etc/ssl/certs/dhparam.pem"

        certbot = self.certbot_for_tests()
        certbot.generate_dhparam_file()

        exists.assert_called_once_with(file)
        sudo.assert_not_called()

    @patch("deploy_tools.certbot.sudo")
    @patch("deploy_tools.certbot.Certbot.certbot_program")
    @patch("deploy_tools.certbot.Certbot.root_directory")
    def test_get_certificate(self, root_dir, certbot_program, sudo):
        certbot = self.certbot_for_tests()
        certbot.get_certificate()

        sudo.assert_called_once_with(
            "{} certonly -w {} -d test_url.com --agree-tos".format(
                certbot_program, root_dir
            )
        )

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_set_renewal_cron_if_not_exists(self, sudo, exists):
        exists.return_value = False
        file = "/etc/cron.d/crontab-renewal"

        certbot = self.certbot_for_tests()
        certbot.set_renewal_cron()

        exists.assert_called_once_with(file)
        sudo.assert_has_calls([
            call(
                "cp {}/certbot-renewal.template {}".format(
                    certbot.template_directory, file
                )
            ),
            call("chmod +x {}".format(file))
        ])

    @patch("deploy_tools.certbot.exists")
    @patch("deploy_tools.certbot.sudo")
    def test_set_renewal_cron_if_exists(self, sudo, exists):
        exists.return_value = True
        file = "/etc/cron.d/crontab-renewal"

        certbot = self.certbot_for_tests()
        certbot.set_renewal_cron()

        exists.assert_called_once_with(file)
        sudo.assert_not_called()
