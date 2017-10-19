config = {
    "output_directory": "out",
    "filename_format": "report_%Y%m%d.xlsx",
    "database_path": "db/urls.db",
    "database_options": {
        "types": {
            "Date": "varchar",
            "*": "integer"
        },
        "drop_tables": False
    },
    "send_mail": True
}
