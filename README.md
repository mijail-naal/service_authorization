# Service Authorization

### Auth API description

An asynchronous API for authentication and a role management system implemented with FastAPI. Also includes user registration and authentication in the Auth service by adding a login via social services (OAuth).

The API includes the next fetures:
- User registration
- Login to the account (the exchange of login and password for a pair of tokens: JWT-access token and refresh token)
- Update the access token
- Logout from an account
- Change a username or a password
- Get the user's login history to the account
- CRUD for role management (only for an admin role)
- Assign or remove a user's role
- Verify the user's rights.

<br>

### Authorization Service description
###### Integration with admin panel and content API services

A service responsible for creating, storing, and logging a user's profile. It will allow users to register at the online cinema and manage their account, store passwords correctly and ensure the security of user data.

The service architecture considers the system of interaction between services (admin, content and auth services), paying attention to error handling and possible shutdown of one of the services.

<br>

### Three steps to launch the project:

- *Change the files `.env.sample` to `.env` and set the environment variables* 

- *Run `docker-compose.yml`*

- *Execute commads to create db, roles and a superuser*

<br>

*All environment variables samples are included in the `.env.sample` files.*

*Don't forget to set the environment variables before running the project!*


<br>

### Technologies used:

![Technologies used](https://skillicons.dev/icons?i=python,django,fastapi,nginx,postgres,redis,elasticsearch,docker)

###### Python, Django, Fastapi, Nginx, PostgreSQL, Redis, Elasticsearch, Docker and Jaeger

<br><br>

###### (*) *Do not use this project for a real deployment*.

<br>

# Run the project

### 1. Set the environment variables 

```
Change all .env.sample files to .env and set the environment variables in the next locations:

- admin_service/.env
- auth_service/auth/env/prod/.env
- auth_service/.env
- content_service/etl_loader/env/prod/.env
- content_service/fastapi/env/prod/.env
- content_service/.env
```

### 2. Run docker-compose.yml

```
$ cd service_authorization/

$ sudo docker compose up --build -d
```

### 3. Execute the next commands in order

```bash
  # 1. Migrations

  docker exec -it auth sh -c "alembic upgrade head"


  # 2. Create roles

  docker exec -it auth sh -c "python create_roles.py"


  # 3. Create providers

  docker exec -it auth sh -c "python create_providers.py"


  # 4. Create superuser

  docker exec -it auth sh -c "python create_superuser.py <login> <password>"
```

<br><br>


#### URLs for local deployment

> admin service: http://localhost:8000/admin/  
> default email: admin@sample.com
>
> auth service: http://localhost:8001/api/openapi
>
> content service: http://localhost/api/openapi

<br><br>

### Project structure
----

<br>

```
service_authorization
├── admin_service
│   ├── configs
│   ├── data
│   ├── movies_admin
│   │   ├── config
│   │   ├── movies
│   │   ├── users
│   │   ├── uwsgi
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   ├── manage.py
│   │   └── requirements.txt
│   ├── .env.sample
│   ├── docker-compose.yml
│   └── nginx.conf
├── auth_service
│   ├── auth
│   │   ├── env/prod
│   │   └── src
│   │       ├── alembic
│   │       ├── api/v1
│   │       ├── core
│   │       ├── db
│   │       ├── dependencies
│   │       ├── models
│   │       ├── schemas
│   │       ├── services
│   │       ├── utils
│   │       ├── alembic.ini
│   │       ├── create_providers.py
│   │       ├── create_roles.py
│   │       ├── create_superuser.py
│   │       ├── Dockerfile
│   │       ├── main.py
│   │       └── requirements.txt
│   ├── nginx
│   │   ├── configs
│   │   │   └── site.conf
│   │   ├── Dockerfile
│   │   ├── nginx.conf
│   │   └── uwsgi_params
│   ├── .env.sample
│   └── docker-compose.yml
├── content_service
│   ├── es
│   ├── etl_loader
│   │   ├── docs
│   │   ├── env/prod
│   │   ├── es
│   │   ├── indices
│   │   ├── process
│   │   │   └── elasticloader.py
│   │   ├── utils
│   │   │   └── logger.py
│   │   ├── Dockerfile
│   │   ├── load_data.py
│   │   └── requirements.txt
│   ├── fastapi
│   │   ├── env/prod
│   │   ├── src
│   │   │   ├── api/v1
│   │   │   ├── core
│   │   │   ├── db
│   │   │   ├── docker
│   │   │   ├── models
│   │   │   ├── services
│   │   │   ├── utils
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── nginx
│   │   ├── configs
│   │   │   └── site.conf
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   ├── redis/data
│   ├── .env.sample
│   └── docker-compose.yml
├── docker-compose.yml
└── README.md

65 directories, 129 files
```