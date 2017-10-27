config = {
    "configuration_directory": "conf",
    "output_directory": "out",
    "filename_format": "report_%Y%m%d.xlsx",
    "xlsx_formats": {
        "header": {
            "bold": True,
            "align": "center",
            "bg_color": "gray",
            "top": True,
            "bottom": True,
            "left": True,
            "right": True,
        },
        "date": {
            "num_format": "dd.mm.yyyy",
            "bg_color": "#f0f0f0",
            "left": True,
            "right": True
        },
        "integer": {
            "left": True,
            "right": True,
            "num_format": "#,##0"
        },
        "percent" : {
            "color": "gray",
            "num_format": "0.00%"
        },
        "footer": {
            "bold": True,
            "bg_color": "#f0fff0",
            "top": True,
            "bottom": True,
            "left": True,
            "right": True,
            "num_format": "#,##0"
        },
    },
    "xlsx_width": {
        "integer": 12,
        "date": 10,
        "*": 15
    },
    "reader_options": {
        "strings_match_re": r"[\w\/\.,:;%\\\$\^#!@&\*\+\-]",
        "row_offset": 1,
    },
    "data_date_format": "%Y-%m-%d",
    "download_data": True,
    "send_mail": True
}
