config = {
    "output_directory": "out",
    "filename_format": "report_%Y%m%d.xlsx",
    "database_path": "db/urls.db",
    "database_types": {
        "Date": "varchar primary key",
        "*": "integer"
    },
#    "download_data": True,
    "download_data": False,
    "send_mail": True
}
