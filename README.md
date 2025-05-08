# keycloak-playground
A sandbox environment to explore Keycloak.

## Quick Start
Before proceeding, verify that port 8080 is not in use on your system.
1. Setup password
    
    Configure the password in `.env` and `keycloak.conf`.

    For `.env`
    ```
    KC_BOOTSTRAP_ADMIN_USERNAME=<The admin username for keycloak admin portal>
    KC_BOOTSTRAP_ADMIN_PASSWORD=<The admin password for keycloak admin portal>

    POSTGRES_USER=<The postgres user for postgreSQL>
    POSTGRES_PASSWORD=<The postgres password for postgreSQL>

    REALM_NAME=<realm name>
    REALM_ADMIN_USER=<realm user name with admin role>
    REALM_ADMIN_PASSWORD=<realm user password with admin role>
    REALM_NORMAL_USER=<realm user name with user role>
    REALM_NORMAL_PASSWORD=<realm user password with user role>
    REALM_CLIENT_ID=<realm client id>
    ```
    For `keycloak.conf`
    ```
    db-username=<The postgres user for postgreSQL>
    db-password=<The postgres password for postgreSQL>
    ```

2. Launch keycloak
    ```bash
    make all
    ```

3. You can login the keycloak admin portal with the password configured in step 1.

4. To clean up, run the following command
    ```bash
    make clean
    ```

## Reference
* [Keycloak document](https://www.keycloak.org/guides)
* [Self-Signed vs. CA-Signed Certificates](https://medium.com/@talyitzhak/understanding-digital-certificates-and-self-signed-certificates-b1cdca759bbc)
* [Automated realm configruation with json config](https://medium.com/@devripper133127/keycloak-in-docker-automated-configuration-with-json-config-216f86bb4ad7)
