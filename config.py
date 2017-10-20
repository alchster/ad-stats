config = {
    "output_directory": "out",
    "filename_format": "report_%Y%m%d.xlsx",
    "database_path": "db/urls.db",
    "database_types": {
        "Date": "varchar primary key",
        "*": "integer"
    },
    "xlsx_formats": {
        "header": {
            "bold": True,
            "align": "center",
            "bg_color": "gray",
            "top": True,
            "bottom": True,
            "left": True,
            "right": True
        },
        "date": {
            "num_format": "dd.mm.yyyy",
            "bg_color": "#f0f0f0",
            "left": True,
            "right": True
        },
        "integer": {
            "left": True,
            "right": True
        },
        "footer": {
            "bold": True,
            "bg_color": "#f0fff0",
            "top": True,
            "bottom": True,
            "left": True,
            "right": True
        },
    },
    "xlsx_width": {
        "integer": 12,
        "date": 10,
        "*": 15
    },
    "data_date_format": "%Y-%m-%d",
    "download_data": True,
    "send_mail": True
}
