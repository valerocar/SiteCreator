from sitecreator import *
from getpass import getpass


def main():
    site_name = input("Site Name: ")
    sudo_password = getpass("Sudo password: ")
    # sql_password = getpass('MySql password: ')

    if input("Create Certificates (y/n)?") == 'y':
        create_certificates(site_name, sudo_password)

    if input("Create Virtual Hosts (y/n)?") == 'y':
        create_wordpress_vhs(site_name, sudo_password)

    if input("Create database and database_user (y/n)?") == 'y':
        wpdb_password = input('Wordpress DB password: ')
        create_database(site_name, sudo_password, wpdb_password)

    if input("Create Wordpress Site (y/n)?") == 'y':
        create_wordpress_site(site_name, sudo_password)


main()
