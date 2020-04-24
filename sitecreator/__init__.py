import subprocess
import os

acme = '/home/valeroc/.acme.sh/acme.sh'
home = '/home/valeroc/'

os.environ['GD_Key'] = "AEYjFzkdWS4_6UsykHMLGpeoZs4XEfMbGx"
os.environ['GD_Secret'] = "Y3emoSwoQKdy9bVHuEp5yq"
os.environ['SHELL'] = "/bin/bash"


def run(cmd, sdo_pwd=None):
    my_cmd = cmd
    if sdo_pwd:
        my_cmd = 'sudo -S <<< "{0}" {1}'.format(sdo_pwd, cmd)
    print(my_cmd)
    # info.insert(tk.INSERT, my_cmd + '\n')
    subprocess.call(["bash", "-c", my_cmd])
    # os.system('/bin/bash -c' + "{}".format(my_cmd))


def create_certificates(site_name, sdo_pwd):
    print('CREATING CERTIFICATES FOR {}'.format(site_name))
    print(100 * '_')
    run('{0} --issue --dns dns_gd -d {1}.com -d www.{1}.com'.format(acme, site_name))
    run('mkdir -p /var/www/ssl/{}'.format(site_name), sdo_pwd=sdo_pwd)
    run('ln -s {0}.acme.sh/{1}.com/{1}.com.cer /var/www/ssl/{1}/cert.cer'.format(home, site_name), sdo_pwd=sdo_pwd)
    run('ln -s {0}.acme.sh/{1}.com/{1}.com.key /var/www/ssl/{1}/key.key'.format(home, site_name), sdo_pwd=sdo_pwd)
    run('ln -s {0}.acme.sh/{1}.com/fullchain.cer /var/www/ssl/{1}/fullchain.cer'.format(home, site_name),
        sdo_pwd=sdo_pwd)


def create_flask_site(site_name, user_name, app_name, sdo_pwd):
    print('CREATING VIRTUAL HOSTS FOR FLASK SITE {}'.format(site_name))
    print(100 * '_')
    # Create http configuration
    with open('templates/base_flask.conf', 'r') as file:
        s = file.read().replace('site', site_name)
    with open('{}.conf'.format(site_name), 'w+') as file:
        file.write(s)

    # Create https configuration
    with open('templates/flask-ssl.conf', 'r') as file:
        s = file.read().replace('site_name', site_name)
        s = s.replace('user_name', user_name)
        s = s.replace('app_name', app_name)

    with open('{}-ssl.conf'.format(site_name), 'w+') as file:
        file.write(s)

    cmds = list()
    # Moving directories
    cmds.append('mv {}.conf /etc/apache2/sites-available'.format(site_name))
    cmds.append('mv {}-ssl.conf /etc/apache2/sites-available'.format(site_name))
    # Setting permissions
    cmds.append('chown root:root /etc/apache2/sites-available/{}.conf'.format(site_name))
    cmds.append('chown root:root /etc/apache2/sites-available/{}-ssl.conf'.format(site_name))
    cmds.append('chmod 644 /etc/apache2/sites-available/{}.conf'.format(site_name))
    cmds.append('chmod 644 /etc/apache2/sites-available/{}-ssl.conf'.format(site_name))
    # Activating sites
    cmds.append('cd /etc/apache2/sites-available')
    cmds.append('a2ensite {}.conf'.format(site_name))
    cmds.append('a2ensite {}-ssl.conf'.format(site_name))
    cmds.append('systemctl reload apache2')
    # Create directory that will hold content
    cmds.append('mkdir /var/www/{}'.format(site_name))
    cmds.append('chown -R {0}:{0} /var/www/{1}'.format(user_name, site_name))
    cmds.append('chmod -R 755 /var/www/{}'.format(site_name))

    for c in cmds:
        run(c, sdo_pwd=sdo_pwd)


def create_wordpress_vhs(site_name, sdo_pwd):
    print('CREATING VIRTUAL HOSTS FOR WORDPRESS SITE {}'.format(site_name))
    print(100 * '_')
    with open('templates/wordpress.conf', 'r') as file:
        s = file.read().replace('site', site_name)
    with open('{}.conf'.format(site_name), 'w+') as file:
        file.write(s)

    cmds = list()
    cmds.append('mv {}.conf /etc/apache2/sites-available'.format(site_name))
    cmds.append('chown root:root /etc/apache2/sites-available/{}.conf'.format(site_name))
    cmds.append('chmod 644 /etc/apache2/sites-available/{}.conf'.format(site_name))
    cmds.append('cd /etc/apache2/sites-available')
    cmds.append('a2ensite {}.conf'.format(site_name))
    cmds.append('systemctl reload apache2')

    for c in cmds:
        run(c, sdo_pwd=sdo_pwd)


def create_wordpress_site(site_name, sdo_pwd):
    run('cd ~')
    run('wget http://wordpress.org/latest.tar.gz')
    run('tar xzf latest.tar.gz')
    run('rm latest.tar.gz')
    run('mv wordpress /var/www/{}'.format(site_name), sdo_pwd=sdo_pwd)
    run('chown -R www-data:www-data /var/www/{}'.format(site_name), sdo_pwd=sdo_pwd)
    run('chmod -R 755 /var/www/{}'.format(site_name), sdo_pwd=sdo_pwd)


def create_database(site_name, sdo_pwd, wpdb_pwd):
    sql1 = "CREATE DATABASE {};".format(site_name.upper())
    sql2 = "CREATE USER '{0}'@'localhost' IDENTIFIED BY '{1}';".format(site_name, wpdb_pwd)
    sql3 = "GRANT ALL ON {0}.* TO '{1}'@'localhost' IDENTIFIED BY '{2}';".format(site_name.upper(), site_name, wpdb_pwd)
    sql4 = "FLUSH PRIVILEGES;"

    cmds = list()
    cmds.append('mysql -uroot -e "{}"'.format(sql1))
    cmds.append('mysql -uroot -e "{}"'.format(sql2))
    cmds.append('mysql -uroot -e "{}"'.format(sql3))
    cmds.append('mysql -uroot -e "{}"'.format(sql4))

    for c in cmds:
        run(c, sdo_pwd=sdo_pwd)

# root.mainloop()
