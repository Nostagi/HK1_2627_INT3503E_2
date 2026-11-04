# Product API

## Folder structure

```plain
products-api/
├── .env.example
├── requirements.txt
├── README.md
├── wsgi.py
├── seed.py
└── app/
    ├── __init__.py              # create_app() – Application Factory
    ├── config.py                # DefaultConfig / TestConfig / ProductionConfig
    ├── extensions.py            # db, migrate, ma, api
    ├── errors.py                # ApiError + subclasses + global handlers
    ├── logging_config.py        # JSON formatter + request tracking
    ├── models/
    │   ├── __init__.py
    │   └── product.py           # SQLAlchemy 2.x typed Mapped
    ├── schemas/
    │   ├── __init__.py
    │   └── product.py           # ProductOut / ProductIn / ProductPatch / ListQuery
    └── resources/
        ├── __init__.py
        ├── products.py          # products_bp (MethodView)
        └── health.py            # health_bp (/healthz, /ready)
```
