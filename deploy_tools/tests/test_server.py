from django.test import TestCase

from mock import call, patch

from deploy_tools.server import Server


class ServerTest(TestCase):

    def server_for_tests(self, **kwargs):
        data = {
            "host": "test_host",
            "user": "test_user",
            "url": "test_site",
            "project": "test_project",
        }
        for key, value in kwargs.iteritems():
            data[key] = value
        return Server(**data)

    @patch("deploy_tools.server.Server.set_env_variables")
    @patch("deploy_tools.server.Certbot")
    def test_init(self, certbot, set_env_variables):
        server = self.server_for_tests()
        self.assertEqual(server.host, "test_host")
        self.assertEqual(server.user, "test_user")
        self.assertEqual(server.url, "test_site")
        set_env_variables.assert_called_once()
        certbot.assert_called_once_with(**{
                "template_directory": server.template_directory,
                "url": server.url
            })

    def test_gunicorn_config(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.gunicorn_config,
            "/etc/init/gunicorn-test_site.conf"
        )

    def test_nginx_config(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.nginx_config,
            "/etc/nginx/sites-available/test_site"
        )

    def test_nginx_config_available(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.nginx_config_available,
            "/etc/nginx/sites-available"
        )

    def test_nginx_config_enabled(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.nginx_config_enabled,
            "/etc/nginx/sites-enabled"
        )

    def test_site_directory(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.site_directory, "/home/test_user/sites/test_site"
        )

    def test_source_directory(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.source_directory,
            "/home/test_user/sites/test_site/source"
        )

    def test_template_directory(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.template_directory,
            "/home/test_user/sites/test_site/source/deploy_tools/templates"
        )

    def test_virtualenv_directory(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.virtualenv_directory,
            "/home/test_user/.virtualenvs/test_site"
        )

    def test_settings_location_if_development(self):
        server = self.server_for_tests(**{"development": True})

        self.assertEqual(
            server.settings_location,
            "test_project.settings.staging"
        )

    def test_settings_location_if_not_development(self):
        server = self.server_for_tests()

        self.assertEqual(
            server.settings_location,
            "test_project.settings.production"
        )

    @patch("deploy_tools.server.run")
    def test_create_directories(self, mock_run):
        server = self.server_for_tests()
        server.create_directories()

        call_string = "mkdir -p /home/test_user/sites/test_site/{}"
        calls = [
            call(call_string.format("media")),
            call(call_string.format("secrets")),
            call(call_string.format("source")),
            call(call_string.format("static")),
        ]
        mock_run.assert_has_calls(calls)

    @patch("deploy_tools.server.sudo")
    @patch("deploy_tools.server.exists")
    def test_disable_nginx_config_if_exists(self, exists, sudo):
        exists.return_value = True

        server = self.server_for_tests()
        server.disable_nginx_config("test_config")

        sudo.assert_called_once_with(
            "rm /etc/nginx/sites-enabled/test_config"
        )

    @patch("deploy_tools.server.sudo")
    @patch("deploy_tools.server.exists")
    def test_disable_nginx_config_if_not_exists(self, exists, sudo):
        exists.return_value = False

        server = self.server_for_tests()
        server.disable_nginx_config("test_config")

        sudo.assert_not_called()

    @patch("deploy_tools.server.exists")
    @patch("deploy_tools.server.sudo")
    def test_enable_nginx_config_if_not_exists(self, sudo, exists):
        exists.return_value = False

        server = self.server_for_tests()
        server.enable_nginx_config()

        sudo.assert_has_calls([
            call(
                "ln -s {} /etc/nginx/sites-enabled/test_site".format(
                    server.nginx_config
                )
            ),
            call("service nginx reload")
        ])

    @patch("deploy_tools.server.exists")
    @patch("deploy_tools.server.sudo")
    def test_enable_nginx_config_if_exists(self, sudo, exists):
        exists.return_value = True

        server = self.server_for_tests()
        server.enable_nginx_config()

        sudo.assert_not_called()

    @patch("deploy_tools.server.local")
    @patch("deploy_tools.server.run")
    @patch("deploy_tools.server.exists")
    @patch("deploy_tools.server.cd")
    def test_get_latest_source_if_exists(self, cd, exists, run, local):
        exists.return_value = True
        local.return_value = "test commit"
        
        server = self.server_for_tests()
        server.get_latest_source("test_repo")
        
        exists.assert_called_once_with(
            "{}/.git".format(server.source_directory)
        )
        run.assert_called_once_with(
            "cd {} && git pull".format(server.source_directory)
        )

    @patch("deploy_tools.server.local")
    @patch("deploy_tools.server.run")
    @patch("deploy_tools.server.exists")
    @patch("deploy_tools.server.cd")
    def test_get_latest_source(self, cd, exists, run, local):
        exists.return_value = False
        local.return_value = "test commit"
        
        server = self.server_for_tests()
        server.get_latest_source("test_repo")
        
        exists.assert_called_once_with(
            "{}/.git".format(server.source_directory)
        )
        run.assert_called_once_with(
            "git clone {} {}".format(
                "test_repo", server.source_directory
            )
        )

    @patch("deploy_tools.server.run")
    def test_reload_gunicorn(self, run):
        server = self.server_for_tests()
        server.reload_gunicorn()

        run.assert_called_once_with(
            "sudo reload gunicorn-{}".format(server.url)
        )

    @patch("deploy_tools.server.sudo")
    def test_reload_nginx(self, sudo):
        server = self.server_for_tests()
        server.reload_nginx()

        sudo.assert_called_once_with("service nginx reload")

    def test_set_env_variables(self):
        server = self.server_for_tests()
        env = server.set_env_variables()

        self.assertEqual(env.host_string, "test_host")
        self.assertEqual(env.user, "test_user")

    @patch("deploy_tools.server.sed")
    @patch("deploy_tools.server.sudo")
    def test_set_gunicorn_config(self, sudo, sed):
        server = self.server_for_tests()
        server.set_gunicorn_config()

        sudo.assert_has_calls([
            call(
                "cp {}/gunicorn-upstart.template.conf {}".format(
                    server.template_directory, server.gunicorn_config
                )
            ),
            call("start gunicorn-{}".format(server.url))
        ])
        sed.assert_has_calls([
            call(server.gunicorn_config, "PROJECT_NAME", server.project, use_sudo=True),
            call(server.gunicorn_config, "SITE_NAME", server.url, use_sudo=True),
            call(server.gunicorn_config, "USER", server.user, use_sudo=True),
        ])


    @patch("deploy_tools.server.sed")
    @patch("deploy_tools.server.Certbot")
    @patch("deploy_tools.server.sudo")
    def test_set_nginx_config_if_not_secure(self, sudo, certbot, sed):
        server = self.server_for_tests()
        server.set_nginx_config()

        sudo.assert_called_once_with(
            "cp {}/deploy_tools/templates/nginx.template.conf {}".format(
                server.source_directory,
                server.nginx_config
            )
        )
        sed.assert_has_calls([
            call(server.nginx_config, "SITE_NAME", server.url, use_sudo=True),
            call(server.nginx_config, "USER", server.user, use_sudo=True),
            call(server.nginx_config, "ROOT_DIRECTORY", server.certbot.root_directory, use_sudo=True),
        ])

    @patch("deploy_tools.server.sed")
    @patch("deploy_tools.server.Certbot")
    @patch("deploy_tools.server.sudo")
    def test_set_nginx_config_if_secure(self, sudo, certbot, sed):
        server = self.server_for_tests()
        server.set_nginx_config(True)

        sudo.assert_called_once_with(
            "cp {}/deploy_tools/templates/nginx-secure.template.conf {}".format(
                server.source_directory,
                server.nginx_config
            )
        )
        sed.assert_has_calls([
            call(server.nginx_config, "SSL_PARAMS_FILE", server.certbot.ssl_params_file, use_sudo=True),
            call(server.nginx_config, "SITE_NAME", server.url, use_sudo=True),
            call(server.nginx_config, "USER", server.user, use_sudo=True),
            call(server.nginx_config, "ROOT_DIRECTORY", server.certbot.root_directory, use_sudo=True),
            call(server.nginx_config, "SSL_DOMAIN_FILE", server.certbot.ssl_domain_file, use_sudo=True),
        ])

    @patch("deploy_tools.server.run")
    @patch("deploy_tools.server.prefix")
    @patch("deploy_tools.server.cd")
    def test_update_database(self, cd, prefix, run):
        server = self.server_for_tests()
        server.update_database()

        cd.assert_called_once_with(server.source_directory)
        prefix.assert_called_once_with(
            "workon {}".format(server.url)
        )
        run.assert_called_once_with(
            "python manage.py migrate --noinput"
        )

    @patch("deploy_tools.server.run")
    @patch("deploy_tools.server.prefix")
    @patch("deploy_tools.server.cd")
    def test_update_static_files(self, cd, prefix, run):
        server = self.server_for_tests()
        server.update_static_files()

        cd.assert_called_once_with(server.source_directory)
        prefix.assert_called_once_with(
            "workon {}".format(server.url)
        )
        run.assert_called_once_with(
            "python manage.py collectstatic --noinput"
        )

    @patch("deploy_tools.server.prefix")
    @patch("deploy_tools.server.run")
    @patch("deploy_tools.server.exists")
    def test_update_virtualenv_if_not_exists(self, exists, run, prefix):
        exists.return_value = False

        server = self.server_for_tests()
        server.update_virtualenv()

        exists.assert_called_once_with(server.virtualenv_directory)
        run.assert_has_calls([
            call("mkvirtualenv test_site"),
            call("echo 'export DJANGO_SETTINGS_MODULE="+
                "\"test_project.settings.production\"' >> "+
                "/home/test_user/.virtualenvs/"+
                "test_site/bin/postactivate"
            ),
            call("pip install -r {}/requirements.txt".format(
                server.source_directory
            )),
        ])

    @patch("deploy_tools.server.prefix")
    @patch("deploy_tools.server.run")
    @patch("deploy_tools.server.exists")
    def test_update_virtualenv_if_exists(self, exists, run, prefix):
        exists.return_value = True

        server = self.server_for_tests()
        server.update_virtualenv()

        exists.assert_called_once_with(server.virtualenv_directory)
        run.assert_has_calls([
            call("pip install -r {}/requirements.txt".format(
                server.source_directory
            )),
        ])

    @patch("deploy_tools.server.prefix")
    @patch("deploy_tools.server.run")
    @patch("deploy_tools.server.exists")
    def test_update_virtualenv_if_development(self, exists, run, prefix):
        exists.return_value = True

        server = self.server_for_tests(**{"development": True})
        server.update_virtualenv()

        exists.assert_called_once_with(server.virtualenv_directory)
        run.assert_has_calls([
            call("pip install -r {}/requirements.txt".format(
                server.source_directory
            )),
            call("pip install -r {}/dev_requirements.txt".format(
                server.source_directory
            )),
        ])