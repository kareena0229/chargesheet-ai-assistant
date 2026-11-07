"""
IPC/BNS Section Knowledge Base
"""

IPC_BNS_MAP = {

    # Theft
    "379": {
        "crime": "Theft",
        "category": "Property Crime",
        "related": ["380", "411", "34"]
    },

    "380": {
        "crime": "Theft in Dwelling House",
        "category": "Property Crime",
        "related": ["379", "411"]
    },

    "411": {
        "crime": "Receiving Stolen Property",
        "category": "Property Crime",
        "related": ["379"]
    },

    # Robbery

    "392": {
        "crime": "Robbery",
        "category": "Violent Crime",
        "related": ["394", "397"]
    },

    "394": {
        "crime": "Voluntarily Causing Hurt in Robbery",
        "category": "Violent Crime",
        "related": ["392"]
    },

    # Murder

    "302": {
        "crime": "Murder",
        "category": "Crime Against Person",
        "related": ["34", "120B"]
    },

    # Assault

    "323": {
        "crime": "Voluntarily Causing Hurt",
        "category": "Crime Against Person",
        "related": ["324"]
    },

    "324": {
        "crime": "Causing Hurt by Dangerous Weapons",
        "category": "Crime Against Person",
        "related": ["323"]
    },

    # Cheating

    "420": {
        "crime": "Cheating",
        "category": "Economic Crime",
        "related": ["406", "468"]
    },

    # Cyber

    "66C": {
        "crime": "Identity Theft",
        "category": "Cyber Crime",
        "related": ["66D"]
    },

    "66D": {
        "crime": "Online Cheating",
        "category": "Cyber Crime",
        "related": ["66C"]
    },

    # NDPS

    "NDPS": {
        "crime": "Narcotics Offence",
        "category": "NDPS",
        "related": []
    }

}